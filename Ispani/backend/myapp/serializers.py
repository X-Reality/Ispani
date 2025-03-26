from rest_framework import serializers
from django.utils import timezone
from .models import (
    CustomUser, StudentProfile, TutorProfile, Group, 
    ChatMessage, UserStatus, GroupMembership, MessageAttachment,
    ChatRoom, PrivateChat, PrivateMessage,Booking,Payment,TutorAvailability
)
from rest_framework.exceptions import ValidationError
from django.contrib.auth.hashers import make_password

class UserStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStatus
        fields = ['is_online', 'last_active', 'status_message']

class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = ['year_of_study', 'course', 'hobbies', 'piece_jobs', 'communication_preference']

class TutorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TutorProfile
        fields = ['subject_expertise', 'hourly_rate', 'qualifications', 'availability', 'verification_status']

class UserSerializer(serializers.ModelSerializer):
    student_profile = StudentProfileSerializer(required=False)
    tutor_profile = TutorProfileSerializer(required=False)
    status = UserStatusSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role', 'student_profile', 'tutor_profile', 'status']
        extra_kwargs = {'password': {'write_only': True}}

class UserRegistrationSerializer(serializers.ModelSerializer):
    student_profile = StudentProfileSerializer(required=False)
    tutor_profile = TutorProfileSerializer(required=False)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'role', 'student_profile', 'tutor_profile']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        student_profile_data = validated_data.pop('student_profile', None)
        tutor_profile_data = validated_data.pop('tutor_profile', None)
        
        # Hash password
        validated_data['password'] = make_password(validated_data['password'])
        
        user = CustomUser.objects.create(**validated_data)
        
        if user.role == 'student' and student_profile_data:
            StudentProfile.objects.create(user=user, **student_profile_data)
        elif user.role == 'tutor' and tutor_profile_data:
            TutorProfile.objects.create(user=user, **tutor_profile_data)
        
        return user

class GroupMembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = GroupMembership
        fields = ['user', 'role', 'joined_at', 'muted_until']

class GroupSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True, read_only=True)
    admin = UserSerializer(read_only=True)

    class Meta:
        model = Group
        fields = '__all__'

class ChatRoomSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True, read_only=True)

    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'chat_type', 'members', 'created_at']

class MessageAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageAttachment
        fields = ['id', 'file', 'attachment_type', 'thumbnail']

class ChatMessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    attachments = MessageAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = ChatMessage
        fields = ['id', 'room', 'sender', 'content', 'attachments', 'timestamp']
        read_only_fields = ['sender', 'timestamp']

class PrivateChatSerializer(serializers.ModelSerializer):
    user1 = UserSerializer(read_only=True)
    user2 = UserSerializer(read_only=True)

    class Meta:
        model = PrivateChat
        fields = ['id', 'user1', 'user2', 'created_at']

class PrivateMessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = PrivateMessage
        fields = ['id', 'chat', 'sender', 'content', 'timestamp']
        read_only_fields = ['sender', 'timestamp']

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

class TutorAvailabilitySerializer(serializers.ModelSerializer):
    tutor = UserSerializer(read_only=True)
    is_available = serializers.SerializerMethodField()

    class Meta:
        model = TutorAvailability
        fields = ['id', 'tutor', 'start_time', 'end_time', 'is_booked', 'is_available']
        read_only_fields = ['id', 'tutor', 'is_booked']

    def get_is_available(self, obj):
        return obj.start_time > timezone.now() and not obj.is_booked

class BookingSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    tutor = UserSerializer(read_only=True)
    availability = TutorAvailabilitySerializer(read_only=True)
    
    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ['student', 'tutor', 'status', 'created_at', 'updated_at']

class CreateBookingSerializer(serializers.ModelSerializer):
    availability_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Booking
        fields = ['availability_id', 'subject', 'notes', 'duration_minutes']
    
    def validate(self, data):
        availability = TutorAvailability.objects.filter(
            id=data['availability_id'],
            is_booked=False,
            start_time__gt=timezone.now()
        ).first()
        
        if not availability:
            raise serializers.ValidationError("This time slot is not available")
        
        data['availability'] = availability
        data['tutor'] = availability.tutor
        data['student'] = self.context['request'].user
        data['price'] = availability.tutor.tutor_profile.hourly_rate * (data['duration_minutes'] / 60)
        
        return data

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'