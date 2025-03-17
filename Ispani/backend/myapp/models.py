from django.db import models
from django.contrib.auth.models import AbstractUser  
from django.db.models import JSONField
from django.utils import timezone
from datetime import timedelta


class OTP(models.Model):
    email = models.EmailField(unique=True)
    code = models.CharField(max_length=6)  # 6-digit OTP code
    user_data = JSONField()  # Temporary storage for user data
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        """Check if the OTP is expired (e.g., 10 minutes validity)"""
        return timezone.now() > self.created_at + timedelta(minutes=10)

    def __str__(self):
        return f"{self.email} - {self.code}"


class PieceJob(models.Model):
    """Model to store available piece jobs that users can select from"""
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Hobby(models.Model):
    """Model to store available hobbies that users can select from"""
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class CustomUser (AbstractUser ):
    # Add fields to store qualification and year of study
    qualification = models.CharField(max_length=255, blank=True, null=True)
    year_of_study = models.IntegerField(blank=True, null=True)
    piece_jobs = models.ManyToManyField(PieceJob, related_name='users', blank=True)
    hobbies = models.ManyToManyField(Hobby, related_name='users', blank=True)  # Added hobbies field

    # Override the default groups and permissions fields to prevent clashes
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups',  # Unique related name
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',  # Unique related name
        blank=True
    )

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser , on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    course = models.CharField(max_length=255)
    qualification = models.CharField(max_length=255)
    year_of_study = models.IntegerField()
    piece_jobs = models.JSONField()  # Store as a list of strings
    hobbies = models.JSONField()      # Store as a list of strings
    communication_preference = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Registration(models.Model):
    user = models.OneToOneField(CustomUser , on_delete=models.CASCADE, related_name='registration')
    name = models.CharField(max_length=255)
    course = models.CharField(max_length=255)
    qualification = models.CharField(max_length=255)
    year_of_study = models.IntegerField()
    piece_jobs = models.ManyToManyField(PieceJob, related_name='registrations', blank=True)
    hobbies = models.ManyToManyField(Hobby, related_name='registrations', blank=True)
    communication_preference = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Group(models.Model):
    GROUP_TYPES = (
        ('Qualification', 'Qualification'),
        ('Year', 'Year'),
        ('Course', 'Course'),
        ('Hobby', 'Hobby'),
        ('Piece Job', 'Piece Job'),
    )

    name = models.CharField(max_length=255)
    members = models.ManyToManyField(CustomUser , related_name='user_groups', blank=True)
    group_type = models.CharField(max_length=255, choices=GROUP_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(CustomUser , on_delete=models.SET_NULL, null=True, related_name='created_groups')
    is_auto_group = models.BooleanField(default=False, help_text="Whether this group was automatically created by the system")

    def __str__(self):
        return f"{self.name} ({self.group_type})"


class Message(models.Model):
    group = models.ForeignKey('Group', on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(CustomUser , on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)  # Track whether the message is read or not

    def __str__(self):
        return f"{self.sender.username} - {self.timestamp}"


class SubjectSpecialization(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class TutorProfile(models.Model):
    tutor = models.OneToOneField(CustomUser , on_delete=models.CASCADE, related_name="tutor_profile")
    subjects = models.ManyToManyField(SubjectSpecialization, related_name="tutors")
    available_times = models.TextField()  # A simple text field to store available times (could be refined)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"Tutor: {self.tutor.username}"


class TutoringSession(models.Model):
    tutor = models.ForeignKey(TutorProfile, on_delete=models.CASCADE, related_name="sessions")
    student = models.ForeignKey(CustomUser , on_delete=models.CASCADE, related_name="booked_sessions")
    subject = models.CharField(max_length=100)
    date = models.DateTimeField()
    duration = models.IntegerField(help_text="Duration in minutes")
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('completed', 'Completed')], default='pending')

    def __str__(self):
        return f"Session with {self.tutor.tutor.username} for {self.student.username} on {self.date}"


class Booking(models.Model):
    student = models.ForeignKey(CustomUser , on_delete=models.CASCADE, related_name="bookings")
    tutor = models.ForeignKey(TutorProfile, on_delete=models.CASCADE, related_name="bookings")
    session = models.ForeignKey(TutoringSession, on_delete=models.CASCADE, related_name="bookings")
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('confirmed', 'Confirmed')], default='pending')

    def __str__(self):
        return f"Booking: {self.student.username} with {self.tutor.tutor.username} - Status: {self.status}"


class DirectMessage(models.Model):
    sender = models.ForeignKey(CustomUser , on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(CustomUser , on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender.username} to {self.recipient.username} - {self.timestamp}"