from rest_framework import serializers
from django.utils import timezone
from .authentication import UserSerializer
from ..models import (
    CustomUser, ExternalCalendarConnection, MeetingProvider,CalendlyEvent,
    Booking,GroupSessionParticipant,Payment, StudentProfile,TutorAvailability, TutorProfile, UserStatus
)

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