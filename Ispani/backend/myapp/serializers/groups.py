from rest_framework import serializers

from ..models import Group, GroupMembership, CustomUser
from .authentication import UserSerializer 


class GroupMembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = GroupMembership
        fields = ['id', 'user', 'group', 'role', 'joined_at']

class GroupSerializer(serializers.ModelSerializer):
    admin = UserSerializer(read_only=True)
    member_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Group
        fields = ['id', 'name', 'description', 'group_type', 'course', 
                 'year_of_study', 'hobbies', 'admin', 'created_at', 
                 'invite_link', 'member_count']
    
    def get_member_count(self, obj):
        return obj.members.count()

class JoinGroupSerializer(serializers.Serializer):
    group_id = serializers.IntegerField()