from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Q
from django.utils import timezone
from .models import Projects, TeamMembers
from .serializers import ProjectSerializer
from config.apps.notifications.services import actor_message, notify_project_event


def _is_owner_or_member(project, user):
    if project.owner_id == user:
        return True
    return TeamMembers.objects.filter(Projects=project, user=user).exists()

# Create your views here.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createProject(request):
    data = request.data.copy()
    team_members_ids = data.pop('team_members', [])
    serializer = ProjectSerializer(data=data)
    
    if serializer.is_valid():
        try:
            project = serializer.save(owner_id=request.user)
            
            from django.contrib.auth import get_user_model
            User = get_user_model()
            for user_id in team_members_ids:
                try:
                    user = User.objects.get(id=user_id)
                    TeamMembers.objects.create(
                        Projects=project,
                        user=user,
                        role='developer' 
                    )
                except User.DoesNotExist:
                    continue

            notify_project_event(
                project=project,
                notification_type='project_created',
                title='Project Created',
                message=actor_message(request.user, f"created project '{project.project_name}'."),
            )

            if team_members_ids:
                notify_project_event(
                    project=project,
                    notification_type='team_member_added',
                    title='Team Updated',
                    message=actor_message(request.user, 'added team members to the project.'),
                )
                    
            # Re-serialize to include newly added team members
            result_serializer = ProjectSerializer(project)
            return Response(result_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getAllProjects(request):
    try:
        projectList = (
            Projects.objects.filter(
                Q(owner_id=request.user) | Q(teamMembers__user=request.user)
            )
            .distinct()
            .order_by('-id')
        )
        serializer = ProjectSerializer(projectList, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'Detail': "Unable to fetch Projects"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def projectDetail(request, pk):
    try:
        project = Projects.objects.get(id=pk)
    except Projects.DoesNotExist:
        return Response({'Detail': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

    # Permission check for both PUT and DELETE
    if project.owner_id != request.user:
        return Response({'Detail': "You don't have permission to perform this action"}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'PUT':
        data = request.data.copy()
        team_members_ids = data.pop('team_members', None)
        previous_status = project.status
        
        # Handle project details update
        serializer = ProjectSerializer(project, data=data, partial=True)
        if serializer.is_valid():
            project = serializer.save()
            added_members_count = 0
            
            # Synchronize team members if provided in the request
            if team_members_ids is not None:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                
                # Simple sync: remove all and re-add (or more complex sync if needed)
                # For now, let's do a sync logic:
                current_member_ids = set(TeamMembers.objects.filter(Projects=project).values_list('user_id', flat=True))
                new_member_ids = set(int(uid) for uid in team_members_ids)
                
                # Members to remove
                TeamMembers.objects.filter(Projects=project, user_id__in=current_member_ids - new_member_ids).delete()
                
                # Members to add
                members_to_add = (new_member_ids - current_member_ids)
                added_members_count = len(members_to_add)
                for user_id in members_to_add:
                    try:
                        user = User.objects.get(id=user_id)
                        TeamMembers.objects.create(Projects=project, user=user, role='developer')
                    except User.DoesNotExist:
                        continue

            if previous_status != project.status and project.status == 'complete':
                notify_project_event(
                    project=project,
                    notification_type='project_completed',
                    title='Project Completed',
                    message=actor_message(request.user, f"marked project '{project.project_name}' as completed."),
                )
            elif previous_status != project.status and project.status == 'at_risk':
                notify_project_event(
                    project=project,
                    notification_type='project_at_risk',
                    title='Project At Risk',
                    message=actor_message(request.user, f"updated project '{project.project_name}' to at-risk status."),
                )
            else:
                notify_project_event(
                    project=project,
                    notification_type='project_updated',
                    title='Project Updated',
                    message=actor_message(request.user, f"updated project '{project.project_name}'."),
                )

            if added_members_count > 0:
                notify_project_event(
                    project=project,
                    notification_type='team_member_added',
                    title='Team Updated',
                    message=actor_message(request.user, f"added {added_members_count} team member(s) to the project."),
                )
            
            # Refresh project to get updated team members
            project.refresh_from_db()
            result_serializer = ProjectSerializer(project)
            return Response(result_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        notify_project_event(
            project=project,
            notification_type='project_updated',
            title='Project Deleted',
            message=actor_message(request.user, f"deleted project '{project.project_name}'."),
        )
        project.delete()
        return Response({'Detail': 'Project deleted successfully'}, status=status.HTTP_200_OK)

    return Response({'Detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def projectStatusUpdate(request, pk):
    try:
        project = Projects.objects.get(id=pk)
    except Projects.DoesNotExist:
        return Response({'Detail': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

    if project.owner_id != request.user:
        return Response({'Detail': "Only the project owner can change project status"}, status=status.HTTP_403_FORBIDDEN)

    next_status = request.data.get('status')
    valid_statuses = [choice[0] for choice in Projects._meta.get_field('status').choices]

    if next_status not in valid_statuses:
        return Response(
            {'status': [f"Invalid status. Allowed values: {', '.join(valid_statuses)}"]},
            status=status.HTTP_400_BAD_REQUEST,
        )

    previous_status = project.status
    project.status = next_status
    project.save(update_fields=['status'])

    if previous_status != project.status and project.status == 'complete':
        notify_project_event(
            project=project,
            notification_type='project_completed',
            title='Project Completed',
            message=actor_message(request.user, f"marked project '{project.project_name}' as completed."),
        )
    elif previous_status != project.status and project.status == 'at_risk':
        notify_project_event(
            project=project,
            notification_type='project_at_risk',
            title='Project At Risk',
            message=actor_message(request.user, f"updated project '{project.project_name}' to at-risk status."),
        )
    else:
        notify_project_event(
            project=project,
            notification_type='project_updated',
            title='Project Status Updated',
            message=actor_message(request.user, f"updated project '{project.project_name}' status to {project.status}."),
        )

    serializer = ProjectSerializer(project)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def projectDashboardOverview(request):
    today = timezone.localdate()

    visible_projects = Projects.objects.filter(
        Q(owner_id=request.user) | Q(teamMembers__user=request.user)
    ).distinct()

    active_projects_qs = (
        visible_projects
        .filter(status__in=['active', 'on_track', 'at_risk'])
        .select_related('owner_id')
        .prefetch_related('teamMembers__user')
        .annotate(
            member_count=Count('teamMembers', distinct=True),
            milestone_count=Count('milestones', distinct=True),
            completed_milestone_count=Count(
                'milestones',
                filter=Q(milestones__status='completed'),
                distinct=True,
            ),
            task_count=Count('tasks', distinct=True),
            completed_task_count=Count(
                'tasks',
                filter=Q(tasks__status='done'),
                distinct=True,
            ),
        )
        .order_by('due_date', '-id')
    )

    active_projects = []
    for project in active_projects_qs:
        days_remaining = None
        if project.due_date:
            days_remaining = (project.due_date - today).days

        owner_name = (
            f"{project.owner_id.first_name} {project.owner_id.last_name}".strip()
            or project.owner_id.username
        )

        active_projects.append(
            {
                'id': project.id,
                'project_name': project.project_name,
                'project_description': project.project_description,
                'status': project.status,
                'progress': project.progress,
                'start_date': project.start_date,
                'due_date': project.due_date,
                'owner_id': project.owner_id_id,
                'owner_name': owner_name,
                'team_size': project.member_count + 1,
                'milestone_count': project.milestone_count,
                'completed_milestones': project.completed_milestone_count,
                'task_count': project.task_count,
                'completed_tasks': project.completed_task_count,
                'days_remaining': days_remaining,
                'is_overdue': bool(days_remaining is not None and days_remaining < 0),
            }
        )

    overview_payload = {
        'summary': {
            'total_projects': visible_projects.count(),
            'active_projects': len(active_projects),
            'on_track_projects': sum(1 for project in active_projects if project['status'] == 'on_track'),
            'at_risk_projects': sum(1 for project in active_projects if project['status'] == 'at_risk'),
            'due_this_week': sum(
                1
                for project in active_projects
                if project['days_remaining'] is not None and 0 <= project['days_remaining'] <= 7
            ),
            'overdue_projects': sum(1 for project in active_projects if project['is_overdue']),
        },
        'active_projects': active_projects,
    }

    return Response(overview_payload, status=status.HTTP_200_OK)
