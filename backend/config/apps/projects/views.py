from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .models import Projects, TeamMembers
from .serializers import ProjectSerializer

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
            print("Project Saved:", project.id)
            
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
                    print(f"Added member {user_id} to project {project.id}")
                except User.DoesNotExist:
                    print(f"User {user_id} not found")
                    continue
                    
            # Re-serialize to include newly added team members
            result_serializer = ProjectSerializer(project)
            return Response(result_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print("Error during creation:", str(e))
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    print("Validation Errors:", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def getAllProjects(request):
    try:
        projectList = Projects.objects.all()
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
        
        # Handle project details update
        serializer = ProjectSerializer(project, data=data, partial=True)
        if serializer.is_valid():
            project = serializer.save()
            
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
                for user_id in (new_member_ids - current_member_ids):
                    try:
                        user = User.objects.get(id=user_id)
                        TeamMembers.objects.create(Projects=project, user=user, role='developer')
                    except User.DoesNotExist:
                        continue
            
            # Refresh project to get updated team members
            project.refresh_from_db()
            result_serializer = ProjectSerializer(project)
            return Response(result_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        project.delete()
        return Response({'Detail': 'Project deleted successfully'}, status=status.HTTP_200_OK)

    return Response({'Detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)