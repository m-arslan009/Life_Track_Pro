from datetime import date
from rest_framework import serializers
from .models import Milestone
from config.apps.projects.models import Projects, TeamMembers
from config.apps.tasks.serializers import TaskSerializer


class MilestoneSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)
    milestone_tasks = TaskSerializer(source="tasks", many=True, read_only=True)
    teamMembers = serializers.SerializerMethodField()
    team_members = serializers.SerializerMethodField()
    start_date = serializers.DateField(required=False)
    status = serializers.CharField(required=False)

    class Meta:
        model = Milestone
        fields = (
            'id',
            'title',
            'description',
            'status',
            'start_date',
            'due_date',
            'project',
            'members',
            'teamMembers',
            'team_members',
            'tasks',
            'milestone_tasks',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_teamMembers(self, obj):
        return list(obj.members.values_list('id', flat=True))

    def get_team_members(self, obj):
        return self.get_teamMembers(obj)

    def validate(self, attrs):
        instance = getattr(self, 'instance', None)

        alias_map = {
            'active': 'in_progress',
            'on_track': 'in_progress',
            'complete': 'completed',
            'completed': 'completed',
            'at_risk': 'delayed',
            'delayed': 'delayed',
            'planned': 'planned',
            'in_progress': 'in_progress',
        }
        if 'status' in attrs:
            mapped_status = alias_map.get(str(attrs['status']).lower())
            if mapped_status is None:
                allowed = ', '.join(sorted(set(alias_map.keys())))
                raise serializers.ValidationError({'status': f'Invalid status. Allowed values: {allowed}.'})
            attrs['status'] = mapped_status

        start_date = attrs.get('start_date', instance.start_date if instance else None)
        due_date = attrs.get('due_date', instance.due_date if instance else None)
        status = attrs.get('status', instance.status if instance else 'planned')
        project = attrs.get('project', instance.project if instance else None)
        members = attrs.get('members', None)

        if start_date and due_date and due_date < start_date:
            raise serializers.ValidationError({'due_date': 'Due date cannot be before start date.'})

        request = self.context.get('request')
        if request and project:
            is_owner = project.owner_id_id == request.user.id
            is_team_member = TeamMembers.objects.filter(Projects=project, user=request.user).exists()
            if not (is_owner or is_team_member):
                raise serializers.ValidationError({'project': 'You do not have access to this project.'})

        if members is not None and project:
            invalid_members = [m.id for m in members if m.Projects_id != project.id]
            if invalid_members:
                raise serializers.ValidationError(
                    {'members': f'Members must belong to project {project.id}. Invalid TeamMembers IDs: {invalid_members}'}
                )

        return attrs

    def create(self, validated_data):
        validated_data.setdefault('start_date', date.today())
        validated_data.setdefault('status', Milestone.STATUS_PLANNED)
        return super().create(validated_data)
