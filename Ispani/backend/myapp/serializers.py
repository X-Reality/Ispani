from rest_framework import serializers
from django.utils import timezone
from .models import (
    CustomUser, StudentProfile, TutorProfile, Group, Event,
    EventParticipant, EventTag, EventComment, EventMedia,
    ExternalCalendarConnection, MeetingProvider,CalendlyEvent,
    ChatMessage, UserStatus, GroupMembership, MessageAttachment,
    ChatRoom,PrivateChat,PrivateMessage,Booking,GroupSessionParticipant,Payment,TutorAvailability
)
from rest_framework.exceptions import ValidationError
from django.utils.crypto import get_random_string
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

class ExternalCalendarConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalCalendarConnection
        fields = ['id', 'provider', 'calendly_username', 'calendly_uri', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']

class MeetingProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingProvider
        fields = ['id', 'provider', 'is_default', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']

class CalendlyEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalendlyEvent
        fields = ['id', 'calendly_event_id', 'event_type_name', 'start_time', 'end_time', 
                 'invitee_email', 'invitee_name', 'location', 'status', 'is_group_event', 
                 'max_participants', 'created_at']
        read_only_fields = ['id', 'created_at']

class GroupSessionParticipantSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    
    class Meta:
        model = GroupSessionParticipant
        fields = ['id', 'student', 'student_name', 'payment_status', 'joined_at']
        read_only_fields = ['id', 'joined_at']
    
    def get_student_name(self, obj):
        return obj.student.username

class BookingSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    tutor_name = serializers.SerializerMethodField()
    participants = GroupSessionParticipantSerializer(many=True, read_only=True)
    has_paid = serializers.SerializerMethodField()
    
    class Meta:
        model = Booking
        fields = ['id', 'student', 'student_name', 'tutor', 'tutor_name', 'subject', 
                  'notes', 'status', 'booking_source', 'meeting_link', 'price', 
                  'duration_minutes', 'is_group_session', 'max_participants', 
                  'current_participants', 'participants', 'has_paid',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'meeting_link', 'created_at', 'updated_at']
    
    def get_student_name(self, obj):
        return obj.student.username
    
    def get_tutor_name(self, obj):
        return obj.tutor.username
    
    def get_has_paid(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        
        # Check if the current user has paid for this booking
        if obj.is_group_session:
            try:
                participant = GroupSessionParticipant.objects.get(booking=obj, student=request.user)
                return participant.payment_status == 'completed'
            except GroupSessionParticipant.DoesNotExist:
                return False
        else:
            # For one-on-one sessions
            return Payment.objects.filter(
                booking=obj,
                student=request.user,
                status='completed'
            ).exists()

class PaymentSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = ['id', 'booking', 'student', 'student_name', 'amount', 
                  'payment_intent_id', 'provider', 'status', 'created_at', 
                  'updated_at', 'paid_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'paid_at']
    
    def get_student_name(self, obj):
        return obj.student.username

class CalendlyConnectionSerializer(serializers.Serializer):
    calendly_auth_url = serializers.URLField(read_only=True)
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Generate Calendly OAuth URL
        data['calendly_auth_url'] = 'https://auth.calendly.com/oauth/authorize?client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=YOUR_REDIRECT_URI'
        return data

class CalendlyOAuthCallbackSerializer(serializers.Serializer):
    code = serializers.CharField()
    
    def validate(self, data):
        # This would be implemented in your views to handle the OAuth callback
        return data

class JoinGroupSessionSerializer(serializers.Serializer):
    booking_id = serializers.IntegerField()
    
    def validate_booking_id(self, value):
        try:
            booking = Booking.objects.get(id=value, is_group_session=True)
            if booking.current_participants >= booking.max_participants:
                raise serializers.ValidationError("This group session is already full")
            if booking.start_time < timezone.now():
                raise serializers.ValidationError("This session has already started")
            self.booking = booking
            return value
        except Booking.DoesNotExist:
            raise serializers.ValidationError("Group session not found")
    
    def save(self):
        user = self.context['request'].user
        booking = self.booking
        
        # Create participant entry
        participant, created = GroupSessionParticipant.objects.get_or_create(
            booking=booking,
            student=user
        )
        
        if created:
            booking.current_participants += 1
            booking.save()
        
        return participant

class EventTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventTag
        fields = ['id', 'name']

class EventMediaSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.StringRelatedField()
    
    class Meta:
        model = EventMedia
        fields = ['id', 'file', 'media_type', 'title', 'uploaded_by', 'uploaded_at']

class EventCommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    
    class Meta:
        model = EventComment
        fields = ['id', 'user', 'user_id', 'content', 'created_at']
        read_only_fields = ['user', 'created_at']

class EventParticipantSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = EventParticipant
        fields = ['id', 'user', 'role', 'status', 'joined_at']
        read_only_fields = ['joined_at']

class EventSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    participants_count = serializers.SerializerMethodField()
    is_creator = serializers.SerializerMethodField()
    user_status = serializers.SerializerMethodField()
    tags = EventTagSerializer(many=True, read_only=True)
    tag_names = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'event_type', 'creator', 'location', 
            'start_time', 'end_time', 'max_participants', 'is_public', 
            'recurrence', 'recurrence_end_date', 'created_at', 'updated_at',
            'invite_link', 'participants_count', 'is_creator', 'user_status',
            'tags', 'tag_names'
        ]
        read_only_fields = ['creator', 'created_at', 'updated_at', 'invite_link']
    
    def get_participants_count(self, obj):
        return obj.participants.filter(status='going').count()
    
    def get_is_creator(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.creator == request.user
        return False
    
    def get_user_status(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            try:
                participant = EventParticipant.objects.get(event=obj, user=request.user)
                return participant.status
            except EventParticipant.DoesNotExist:
                return None
        return None
    
    def create(self, validated_data):
        tag_names = validated_data.pop('tag_names', [])
        request = self.context.get('request')
        
        # Generate invite link
        invite_link = get_random_string(20)
        
        event = Event.objects.create(
            creator=request.user,
            invite_link=invite_link,
            **validated_data
        )
        
        # Add creator as organizer
        EventParticipant.objects.create(
            event=event,
            user=request.user,
            role='organizer',
            status='going'
        )
        
        # Process tags
        for tag_name in tag_names:
            tag, created = EventTag.objects.get_or_create(name=tag_name.lower().strip())
            event.tags.add(tag)
            
        return event
    
    def update(self, instance, validated_data):
        tag_names = validated_data.pop('tag_names', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        
        # Update tags if provided
        if tag_names is not None:
            instance.tags.clear()
            for tag_name in tag_names:
                tag, created = EventTag.objects.get_or_create(name=tag_name.lower().strip())
                instance.tags.add(tag)
                
        return instance

class EventDetailSerializer(EventSerializer):
    participants = EventParticipantSerializer(many=True, read_only=True)
    comments = EventCommentSerializer(many=True, read_only=True)
    media = EventMediaSerializer(many=True, read_only=True)
    
    class Meta(EventSerializer.Meta):
        fields = EventSerializer.Meta.fields + ['participants', 'comments', 'media']