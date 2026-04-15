from rest_framework import serializers
from .models import Task
from projects.models import TeamMembers


class TaskSerializer(serializers.ModelSerializer):
	# Compatibility aliases used by existing frontend state shape
	milestone_id = serializers.IntegerField(read_only=True)
	assignee_id = serializers.IntegerField(read_only=True)

	class Meta:
		model = Task
		fields = (
			"id",
			"title",
			"description",
			"status",
			"project",
			"milestone",
			"assignee",
			"created_at",
			"updated_at",
			"milestone_id",
			"assignee_id",
		)
		read_only_fields = ("id", "created_at", "updated_at")

	def validate(self, attrs):
		instance = getattr(self, "instance", None)
		request = self.context.get("request")

		project = attrs.get("project", instance.project if instance else None)
		milestone = attrs.get("milestone", instance.milestone if instance else None)
		assignee = attrs.get("assignee", instance.assignee if instance else None)

		if milestone and project and milestone.project_id != project.id:
			raise serializers.ValidationError(
				{"milestone": "Milestone must belong to the selected project."}
			)

		if assignee and project and assignee.Projects_id != project.id:
			raise serializers.ValidationError(
				{"assignee": "Assignee must belong to the selected project."}
			)

		if request and project:
			is_owner = project.owner_id_id == request.user.id
			is_member = TeamMembers.objects.filter(
				Projects=project,
				user=request.user,
			).exists()
			if not (is_owner or is_member):
				raise serializers.ValidationError(
					{"project": "You do not have access to this project."}
				)

		return attrs