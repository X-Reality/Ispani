from rest_framework import serializers
from .models import StudentProfile, Group, Message
from rest_framework.exceptions import ValidationError

class StudentProfileSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = StudentProfile
        fields = ['id', 'username', 'email', 'password', 'year_of_study', 'course', 'hobbies', 'piece_jobs','communication_preference']

    def create(self, validated_data):
        # Create a new user with a hashed password
        user = StudentProfile.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email'),

            year_of_study=validated_data.get('year_of_study'),
            course=validated_data.get('course'),
            hobbies=validated_data.get('hobbies'),
            piece_jobs=validated_data.get('piece_jobs'),
            communication_preference=validated_data.get('communication_preference')

        )
        user.is_active = True
        user.save()

        # Automatically assign the user to groups
        self.assign_to_study_groups(user)
        self.assign_to_hobby_groups(user)

        return user

    def assign_to_study_groups(self, user):
        course = user.course
        year_of_study = user.year_of_study

        if course and year_of_study:
            group, created = Group.objects.get_or_create(
                name=f"{course} - Year {year_of_study}",
                field_of_study=course,
                year_of_study=year_of_study,
            )
            group.members.add(user)

    def assign_to_hobby_groups(self, user):
        hobbies = user.hobbies
        if hobbies:
            for hobby in hobbies.split(','):
                hobby = hobby.strip()
                if hobby:
                    group, created = Group.objects.get_or_create(
                        name=f"{hobby} Community",
                        field_of_study=None,
                        year_of_study=None,
                    )
                    group.members.add(user)


class MessageSerializer(serializers.ModelSerializer):
    sender = StudentProfileSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'content', 'timestamp', 'sender', 'group','recipient']

class PrivateMessageSerializer(serializers.ModelSerializer):
    sender = StudentProfileSerializer(read_only=True)
    recipient = StudentProfileSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'content', 'timestamp', 'sender', 'recipient']



class GroupSerializer(serializers.ModelSerializer):
    members = StudentProfileSerializer(many=True, read_only=True)
    messages = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    last_message_time = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    is_member = serializers.SerializerMethodField()
    
    class Meta:
        model = Group
        fields = ['id', 'name', 'members', 'course', 'year_of_study', 
                  'messages', 'last_message', 'last_message_time', 'unread_count', 'is_member']
    
    def get_messages(self, obj):
        # Only fetch the last 20 messages for performance
        recent_messages = Message.objects.filter(group=obj).order_by('-timestamp')[:20]
        return MessageSerializer(recent_messages, many=True).data
    
    def get_last_message(self, obj):
        last_message = Message.objects.filter(group=obj).order_by('-timestamp').first()
        if last_message:
            return f"{last_message.sender.username}: {last_message.content[:30]}"
        return None
    
    def get_last_message_time(self, obj):
        last_message = Message.objects.filter(group=obj).order_by('-timestamp').first()
        if last_message:
            return last_message.timestamp.isoformat()
        return None
    
    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            # Replace this with your actual unread message counting logic
            return Message.objects.filter(group=obj).count()  # Placeholder
        return 0
    
    def get_is_member(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            return obj.members.filter(id=request.user.id).exists()
        return False

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
            student_profile = request.user
            self.group.members.add(student_profile)
            return self.group
        raise serializers.ValidationError("User must be authenticated to join a group")

class CommunitySerializer(serializers.ModelSerializer):
    admin = StudentProfileSerializer(read_only=True)
    members_count = serializers.SerializerMethodField()
    groups_count = serializers.SerializerMethodField()
    is_member = serializers.SerializerMethodField()
    
    class Meta:
        model = Community
        fields = ['id', 'name', 'description', 'admin', 'members_count', 
                  'groups_count', 'created_at', 'is_member']
    
    def get_members_count(self, obj):
        return obj.members.count()
    
    def get_groups_count(self, obj):
        return obj.groups.count()
    
    def get_is_member(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            return obj.members.filter(id=request.user.id).exists()
        return False

class CommunityDetailSerializer(CommunitySerializer):
    members = StudentProfileSerializer(many=True, read_only=True)
    groups = GroupSerializer(many=True, read_only=True)
    
    class Meta:
        model = Community
        fields = ['id', 'name', 'description', 'admin', 'members', 
                  'groups', 'created_at', 'is_member']