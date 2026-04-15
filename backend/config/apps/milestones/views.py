from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from .models import Milestone
from .serializers import MilestoneSerializer
from projects.models import TeamMembers
from projects.progress import recalculate_project_progress


def _project_visible_to_user(project, user):
	if project.owner_id == user:
		return True
	return TeamMembers.objects.filter(Projects=project, user=user).exists()


def _project_owner_only(project, user):
	return project.owner_id == user


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def milestoneListCreate(request):
	if request.method == "GET":
		project_id = request.GET.get("project_id")
		qs = Milestone.objects.filter(
			Q(project__owner_id=request.user)
			| Q(project__teamMembers__user=request.user)
		).distinct()

		if project_id:
			qs = qs.filter(project_id=project_id)

		serializer = MilestoneSerializer(qs.order_by("due_date", "id"), many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)

	serializer = MilestoneSerializer(data=request.data, context={"request": request})
	if serializer.is_valid():
		if not _project_owner_only(serializer.validated_data["project"], request.user):
			return Response(
				{"Detail": "Only the project owner can create milestones"},
				status=status.HTTP_403_FORBIDDEN,
			)
		milestone = serializer.save()
		return Response(MilestoneSerializer(milestone).data, status=status.HTTP_201_CREATED)
	return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def milestoneDetail(request, pk):
	try:
		milestone = Milestone.objects.get(id=pk)
	except Milestone.DoesNotExist:
		return Response({"Detail": "Milestone not found"}, status=status.HTTP_404_NOT_FOUND)

	if not _project_visible_to_user(milestone.project, request.user):
		return Response(
			{"Detail": "You do not have permission to access this milestone"},
			status=status.HTTP_403_FORBIDDEN,
		)

	if request.method == "GET":
		return Response(MilestoneSerializer(milestone).data, status=status.HTTP_200_OK)

	if request.method in ["PUT", "PATCH"]:
		if not _project_owner_only(milestone.project, request.user):
			return Response(
				{"Detail": "Only the project owner can update milestones"},
				status=status.HTTP_403_FORBIDDEN,
			)
		serializer = MilestoneSerializer(
			milestone,
			data=request.data,
			partial=request.method == "PATCH",
			context={"request": request},
		)
		if serializer.is_valid():
			updated = serializer.save()
			return Response(MilestoneSerializer(updated).data, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	project = milestone.project
	if not _project_owner_only(project, request.user):
		return Response(
			{"Detail": "Only the project owner can delete milestones"},
			status=status.HTTP_403_FORBIDDEN,
		)
	milestone.delete()
	recalculate_project_progress(project)
	return Response({"Detail": "Milestone deleted"}, status=status.HTTP_200_OK)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def milestoneStatusUpdate(request, pk):
	try:
		milestone = Milestone.objects.get(id=pk)
	except Milestone.DoesNotExist:
		return Response({"Detail": "Milestone not found"}, status=status.HTTP_404_NOT_FOUND)

	if not _project_owner_only(milestone.project, request.user):
		return Response(
			{"Detail": "Only the project owner can update milestone status"},
			status=status.HTTP_403_FORBIDDEN,
		)

	status_value = request.data.get("status")
	valid_status = [choice[0] for choice in Milestone.STATUS_CHOICES]
	if status_value not in valid_status:
		return Response(
			{"status": [f"Invalid status. Allowed values: {', '.join(valid_status)}"]},
			status=status.HTTP_400_BAD_REQUEST,
		)

	milestone.status = status_value
	milestone.save(update_fields=["status", "updated_at"])

	return Response(MilestoneSerializer(milestone).data, status=status.HTTP_200_OK)
