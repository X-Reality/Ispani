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
    
    def validate_group_id(self, value):
        try:
            self.group = Group.objects.get(id=value)
        except Group.DoesNotExist:
            raise serializers.ValidationError("Group does not exist")
        return value
    
    def save(self):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user
            self.group.members.add(user)
            return self.group
        raise serializers.ValidationError("User must be authenticated to join a group")