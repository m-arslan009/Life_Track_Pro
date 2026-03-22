from rest_framework import serializers
from .models import Projects, TeamMembers
from users.serializers import UserSerializer

class TeamMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = TeamMembers
        fields = ('id', 'user', 'role')

class ProjectSerializer(serializers.ModelSerializer):
    teamMembers = TeamMemberSerializer(many=True, read_only=True)
    
    class Meta:
        model = Projects
        fields = '__all__'
        read_only_fields = ('id', 'owner_id')

