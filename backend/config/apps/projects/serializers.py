from rest_framework import serializers
from datetime import date, timedelta
from .models import Projects, TeamMembers
from config.apps.users.serializers import UserSerializer
from config.apps.milestones.models import Milestone

class TeamMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = TeamMembers
        fields = ('id', 'user', 'role')

class ProjectSerializer(serializers.ModelSerializer):
    teamMembers = TeamMemberSerializer(many=True, read_only=True)
    milestones = serializers.SerializerMethodField()
    progress = serializers.IntegerField(required=False)
    start_date = serializers.DateField(required=False)
    due_date = serializers.DateField(required=False)
    
    class Meta:
        model = Projects
        fields = '__all__'
        read_only_fields = ('id', 'owner_id')

    def get_milestones(self, obj):
        milestone_list = (
            Milestone.objects.filter(project=obj)
            .prefetch_related('members', 'tasks')
            .order_by('due_date', 'id')
        )

        payload = []
        for milestone in milestone_list:
            tasks = sorted(milestone.tasks.all(), key=lambda item: item.id)
            payload.append(
                {
                    'id': milestone.id,
                    'title': milestone.title,
                    'description': milestone.description,
                    'status': milestone.status,
                    'start_date': milestone.start_date,
                    'due_date': milestone.due_date,
                    'teamMembers': list(milestone.members.values_list('id', flat=True)),
                    'tasks': [
                        {
                            'id': task.id,
                            'title': task.title,
                            'description': task.description,
                            'status': task.status,
                            'assignee': task.assignee_id,
                        }
                        for task in tasks
                    ],
                }
            )

        return payload

    def create(self, validated_data):
        validated_data.setdefault('progress', 0)
        start = validated_data.setdefault('start_date', date.today())
        validated_data.setdefault('due_date', start + timedelta(days=30))
        return super().create(validated_data)

