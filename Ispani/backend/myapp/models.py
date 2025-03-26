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

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='student_bookings')
    tutor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='tutor_bookings')
    availability = models.OneToOneField(TutorAvailability, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    meeting_link = models.URLField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    duration_minutes = models.PositiveIntegerField(default=60, validators=[MinValueValidator(15), MaxValueValidator(240)])

    def __str__(self):
        return f"Booking #{self.id} - {self.student.username} with {self.tutor.username}"

class Payment(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_intent_id = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Payment for Booking #{self.booking.id}"