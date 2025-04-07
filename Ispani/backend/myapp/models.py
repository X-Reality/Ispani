from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
import os

ROLE_CHOICES = (
    ('tutor', 'Tutor'),
    ('student', 'Student'),
)

class CustomUser(AbstractUser):
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='student')
    email = models.EmailField(unique=True)

    REQUIRED_FIELDS = ['email']
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username

class StudentProfile(models.Model):

    REQUIRED_FIELDS = ['email'] 
    REQUIRED_FIELDS = ['username']

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student_profile')
    year_of_study = models.IntegerField(null=True, blank=True)
    course = models.CharField(max_length=100, null=True, blank=True)
    hobbies = models.TextField(null=True, blank=True)
    piece_jobs = models.TextField(null=True, blank=True)
    communication_preference = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"Student Profile: {self.user.username}"

class TutorProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='tutor_profile')
    subject_expertise = models.TextField()
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    qualifications = models.TextField()
    availability = models.TextField()
    verification_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='pending')
    
    def __str__(self):
        return f"Tutor Profile: {self.user.username}"

class Group(models.Model):
    GROUP_TYPE_CHOICES = [
        ('study', 'Study Group'),
        ('hobby', 'Hobby Group'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    group_type = models.CharField(max_length=5, choices=GROUP_TYPE_CHOICES)
    year_of_study = models.IntegerField(null=True, blank=True)
    course = models.CharField(max_length=100, null=True, blank=True)
    hobbies = models.CharField(max_length=100, null=True, blank=True)
    members = models.ManyToManyField(CustomUser, related_name='groups_in', blank=True)
    admin = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='admin_groups', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    invite_link = models.CharField(max_length=50, unique=True, null=True, blank=True)

    def clean(self):
        if self.group_type == 'study':
            if not self.year_of_study or not self.course:
                raise ValidationError("Year of study and course are required for study groups.")
            self.hobbies = None
        elif self.group_type == 'hobby':
            if not self.hobbies:
                raise ValidationError("Hobbies are required for hobby groups.")
            self.year_of_study = None
            self.course = None

    def __str__(self):
        return f"{self.name} - {self.get_group_type_display()}"

class ChatRoom(models.Model):
    CHAT_TYPES = [
        ('group', 'Group Chat'),
        ('study_group', 'Study Group Chat'),
        ('hobby_group', 'Hobby Group Chat'),
    ]

    name = models.CharField(max_length=255)
    chat_type = models.CharField(max_length=20, choices=CHAT_TYPES)
    members = models.ManyToManyField(CustomUser, related_name="chat_rooms")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.chat_type})"

class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="sent_messages")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender} in {self.room.name}"

class PrivateChat(models.Model):
    user1 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='chats_initiated')
    user2 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='chats_received')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user1', 'user2']

    def __str__(self):
        return f"Chat between {self.user1.username} and {self.user2.username}"

class PrivateMessage(models.Model):
    chat = models.ForeignKey(PrivateChat, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="private_sent_messages")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.username}"

class UserStatus(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='status')
    is_online = models.BooleanField(default=False)
    last_active = models.DateTimeField(auto_now=True)
    status_message = models.CharField(max_length=100, blank=True, default="Available")

    def __str__(self):
        return f"{self.user.username} - {'Online' if self.is_online else 'Offline'}"

class GroupMembership(models.Model):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('MEMBER', 'Member'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='memberships')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='memberships')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='MEMBER')
    joined_at = models.DateTimeField(auto_now_add=True)
    muted_until = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'group')

    def __str__(self):
        return f"{self.user.username} - {self.group.name} ({self.get_role_display()})"

class MessageAttachment(models.Model):
    ATTACHMENT_TYPES = (
        ('IMAGE', 'Image'),
        ('VIDEO', 'Video'),
        ('AUDIO', 'Audio'),
        ('DOCUMENT', 'Document'),
    )

    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='message_attachments/')
    attachment_type = models.CharField(max_length=10, choices=ATTACHMENT_TYPES)
    thumbnail = models.ImageField(upload_to='message_thumbnails/', null=True, blank=True)

    def __str__(self):
        return f"{self.get_attachment_type_display()} for message {self.message.id}"

    def filename(self):
        return os.path.basename(self.file.name)

@receiver(post_save, sender=CustomUser)
def create_user_status(sender, instance, created, **kwargs):
    if created:
        UserStatus.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.role == 'student':
        StudentProfile.objects.create(user=instance)

class TutorAvailability(models.Model):
    tutor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='availabilities')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_booked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Tutor Availabilities"
        ordering = ['start_time']

    def __str__(self):
        return f"{self.tutor.username} available from {self.start_time} to {self.end_time}"

class ExternalCalendarConnection(models.Model):
    """Model to store tutor's external calendar connections"""
    PROVIDER_CHOICES = [
        ('calendly', 'Calendly'),
        ('google', 'Google Calendar'),
        ('microsoft', 'Microsoft Calendar'),
    ]
    
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='calendar_connections')
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    provider_user_id = models.CharField(max_length=255, blank=True, null=True)
    access_token = models.TextField()
    refresh_token = models.TextField(blank=True, null=True)
    token_expires_at = models.DateTimeField(blank=True, null=True)
    calendly_username = models.CharField(max_length=255, blank=True, null=True)
    calendly_uri = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'provider']
        
    def __str__(self):
        return f"{self.user.username}'s {self.get_provider_display()} connection"

class MeetingProvider(models.Model):
    """Model to store tutor's preferred meeting platforms"""
    PROVIDER_CHOICES = [
        ('zoom', 'Zoom'),
        ('google_meet', 'Google Meet'),
        ('microsoft_teams', 'Microsoft Teams'),
        ('jitsi', 'Jitsi Meet'),
    ]
    
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='meeting_providers')
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    provider_user_id = models.CharField(max_length=255, blank=True, null=True)
    access_token = models.TextField(blank=True, null=True)
    refresh_token = models.TextField(blank=True, null=True)
    token_expires_at = models.DateTimeField(blank=True, null=True)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'provider']
        
    def __str__(self):
        return f"{self.user.username}'s {self.get_provider_display()} connection"

class CalendlyEvent(models.Model):
    """Model to store Calendly event details"""
    tutor = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='calendly_events')
    calendly_event_id = models.CharField(max_length=255, unique=True)
    calendly_event_uri = models.URLField()
    event_type_name = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    invitee_email = models.EmailField()
    invitee_name = models.CharField(max_length=255)
    location = models.TextField(blank=True, null=True)
    cancellation_url = models.URLField(blank=True, null=True)
    reschedule_url = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=20, default='active')
    is_group_event = models.BooleanField(default=False)
    max_participants = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.tutor.username}'s event: {self.event_type_name}"
        
# Update your existing Booking model
class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    BOOKING_SOURCE_CHOICES = [
        ('internal', 'App Booking'),
        ('calendly', 'Calendly Booking'),
    ]

    student = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='student_bookings')
    tutor = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='tutor_bookings')
    availability = models.OneToOneField('TutorAvailability', on_delete=models.CASCADE, null=True, blank=True)
    subject = models.CharField(max_length=100)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    booking_source = models.CharField(max_length=20, choices=BOOKING_SOURCE_CHOICES, default='internal')
    meeting_link = models.URLField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    duration_minutes = models.PositiveIntegerField(default=60, validators=[MinValueValidator(15), MaxValueValidator(240)])
    is_group_session = models.BooleanField(default=False)
    max_participants = models.PositiveIntegerField(default=1)
    current_participants = models.PositiveIntegerField(default=1)
    calendly_event = models.ForeignKey(CalendlyEvent, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    
    def __str__(self):
        return f"Booking #{self.id} - {self.student.username} with {self.tutor.username}"

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

# Update your existing Payment model to handle group sessions
class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    student = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_intent_id = models.CharField(max_length=100)
    provider = models.CharField(max_length=20, default='stripe')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Payment for {self.student.username} - Booking #{self.booking.id}"


class Event(models.Model):
    EVENT_TYPE_CHOICES = [
        ('social', 'Social Gathering'),
        ('sports', 'Sports Activity'),
        ('game', 'Game Night'),
        ('study', 'Group Study'),
        ('outdoor', 'Outdoor Activity'),
        ('arts', 'Arts & Crafts'),
        ('other', 'Other')
    ]
    
    RECURRENCE_CHOICES = [
        ('one-time', 'One-time Event'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('biweekly', 'Every Two Weeks'),
        ('monthly', 'Monthly')
    ]
    
    title = models.CharField(max_length=100)
    description = models.TextField()
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    creator = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='created_events')
    location = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    max_participants = models.PositiveIntegerField(default=10)
    is_public = models.BooleanField(default=True)
    recurrence = models.CharField(max_length=20, choices=RECURRENCE_CHOICES, default='one-time')
    recurrence_end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    invite_link = models.CharField(max_length=50, unique=True, null=True, blank=True)
    tags = models.ManyToManyField('EventTag', related_name='events', blank=True)
    
    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time")
        if self.recurrence != 'one-time' and not self.recurrence_end_date:
            raise ValidationError("Recurring events must have an end date")
        
    def __str__(self):
        return f"{self.title} - {self.start_time.strftime('%d %b %Y, %H:%M')}"

class EventParticipant(models.Model):
    ROLE_CHOICES = [
        ('organizer', 'Organizer'),
        ('participant', 'Participant')
    ]
    
    STATUS_CHOICES = [
        ('invited', 'Invited'),
        ('going', 'Going'),
        ('maybe', 'Maybe'),
        ('declined', 'Declined')
    ]
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='events')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='participant')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='going')
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('event', 'user')
        
    def __str__(self):
        return f"{self.user.username} - {self.event.title} ({self.get_status_display()})"

class EventTag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

class EventComment(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='event_comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.event.title}"

class EventMedia(models.Model):
    MEDIA_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('document', 'Document')
    ]
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='media')
    file = models.FileField(upload_to='event_media/')
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPE_CHOICES)
    title = models.CharField(max_length=100, blank=True)
    uploaded_by = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_media_type_display()} for {self.event.title}"