from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .authentication import CustomUser
from django.utils import timezone

class TutorAvailability(models.Model):
    tutor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='availability_slots')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_booked = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['start_time']

class MeetingProvider(models.Model):
    PROVIDER_CHOICES = (
        ('zoom', 'Zoom'),
        ('google_meet', 'Google Meet'),
        ('microsoft_teams', 'Microsoft Teams'),
        ('other', 'Other'),
    )
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='meeting_providers')
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    credentials = models.JSONField(null=True, blank=True)
    is_default = models.BooleanField(default=False)

class ExternalCalendarConnection(models.Model):
    PROVIDER_CHOICES = (
        ('google', 'Google Calendar'),
        ('outlook', 'Outlook Calendar'),
        ('calendly', 'Calendly'),
        ('other', 'Other'),
    )
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='calendar_connections')
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    provider_user_id = models.CharField(max_length=255)
    access_token = models.TextField()
    refresh_token = models.TextField(null=True, blank=True)
    token_expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    calendly_username = models.CharField(max_length=255, blank=True)
    calendly_uri = models.CharField(max_length=255, blank=True)

class CalendlyEvent(models.Model):
    tutor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='calendly_events')
    calendly_event_id = models.CharField(max_length=255, unique=True)
    calendly_event_uri = models.CharField(max_length=255)
    event_type_name = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    invitee_email = models.EmailField()
    invitee_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True)
    cancellation_url = models.URLField(blank=True)
    reschedule_url = models.URLField(blank=True)
    is_group_event = models.BooleanField(default=False)
    status = models.CharField(max_length=20, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bookings_as_student')
    tutor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bookings_as_tutor')
    subject = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    booking_source = models.CharField(max_length=50, default='direct')
    meeting_link = models.URLField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    duration_minutes = models.IntegerField(validators=[MinValueValidator(15), MaxValueValidator(480)])
    calendly_event = models.OneToOneField(CalendlyEvent, on_delete=models.SET_NULL, null=True, blank=True)
    is_group_session = models.BooleanField(default=False)
    max_participants = models.IntegerField(default=1)
    current_participants = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

class GroupSessionParticipant(models.Model):
    """Model to store participants of group sessions"""
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='participants')
    student = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='group_sessions')
    payment_status = models.CharField(max_length=20, default='pending')
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['booking', 'student']
        
    def __str__(self):
        return f"{self.student.username} in {self.booking}"

class Payment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_intent_id = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)