from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from .models import Task
from .serializers import TaskSerializer
from projects.models import Projects, TeamMembers
from projects.progress import recalculate_project_progress


def _project_visible_to_user(project, user):
	if project.owner_id == user:
		return True
	return TeamMembers.objects.filter(Projects=project, user=user).exists()


def _project_owner_only(project, user):
	return project.owner_id == user


def _can_change_task_status(task, user):
	if task.project.owner_id == user:
		return True
	if TeamMembers.objects.filter(Projects=task.project, user=user).exists():
		return True
	return bool(task.assignee and task.assignee.user_id == user.id)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def taskListCreate(request):
	if request.method == "GET":
		project_id = request.GET.get("project_id")
		milestone_id = request.GET.get("milestone_id")

		qs = Task.objects.filter(
			Q(project__owner_id=request.user)
			| Q(project__teamMembers__user=request.user)
		).distinct()

		if project_id:
			qs = qs.filter(project_id=project_id)
		if milestone_id:
			qs = qs.filter(milestone_id=milestone_id)

		serializer = TaskSerializer(qs.order_by("id"), many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)

	serializer = TaskSerializer(data=request.data, context={"request": request})
	if serializer.is_valid():
		if not _project_owner_only(serializer.validated_data["project"], request.user):
			return Response(
				{"Detail": "Only the project owner can create tasks"},
				status=status.HTTP_403_FORBIDDEN,
			)
		task = serializer.save()
		recalculate_project_progress(task.project)
		return Response(TaskSerializer(task).data, status=status.HTTP_201_CREATED)
	return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def taskDetail(request, pk):
	try:
		task = Task.objects.get(id=pk)
	except Task.DoesNotExist:
		return Response({"Detail": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

	if not _project_visible_to_user(task.project, request.user):
		return Response(
			{"Detail": "You do not have permission to access this task"},
			status=status.HTTP_403_FORBIDDEN,
		)

	if request.method == "GET":
		return Response(TaskSerializer(task).data, status=status.HTTP_200_OK)

	if request.method in ["PUT", "PATCH"]:
		if not _project_owner_only(task.project, request.user):
			return Response(
				{"Detail": "Only the project owner can update tasks"},
				status=status.HTTP_403_FORBIDDEN,
			)
		serializer = TaskSerializer(
			task,
			data=request.data,
			partial=request.method == "PATCH",
			context={"request": request},
		)
		if serializer.is_valid():
			updated = serializer.save()
			recalculate_project_progress(updated.project)
			return Response(TaskSerializer(updated).data, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	task_project = task.project
	if not _project_owner_only(task_project, request.user):
		return Response(
			{"Detail": "Only the project owner can delete tasks"},
			status=status.HTTP_403_FORBIDDEN,
		)
	task.delete()
	recalculate_project_progress(task_project)
	return Response({"Detail": "Task deleted"}, status=status.HTTP_200_OK)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def taskStatusUpdate(request, pk):
	try:
		task = Task.objects.get(id=pk)
	except Task.DoesNotExist:
		return Response({"Detail": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

	if not _can_change_task_status(task, request.user):
		return Response(
			{"Detail": "You do not have permission to update this task status"},
			status=status.HTTP_403_FORBIDDEN,
		)

	status_value = request.data.get("status")
	valid_status = [choice[0] for choice in Task.STATUS_CHOICES]
	if status_value not in valid_status:
		return Response(
			{"status": [f"Invalid status. Allowed values: {', '.join(valid_status)}"]},
			status=status.HTTP_400_BAD_REQUEST,
		)

	task.status = status_value
	task.save(update_fields=["status", "updated_at"])
	recalculate_project_progress(task.project)

	return Response(TaskSerializer(task).data, status=status.HTTP_200_OK)
