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




class CustomUser(AbstractUser):
   

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

class Registration(models.Model):
    name = models.CharField(max_length=255)
    course = models.CharField(max_length=255)
    qualification = models.CharField(max_length=255)
    year_of_study = models.IntegerField()
    piece_jobs = models.JSONField(default=list)  # Stores list of jobs
    hobbies = models.JSONField(default=list)  # Stores list of hobbies
    communication_preference = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Group(models.Model):
    name = models.CharField(max_length=255)
    members = models.ManyToManyField(CustomUser, related_name='user_groups', blank=True)
    group_type = models.CharField(max_length=255, choices=[('Hobby', 'Hobby'), ('Piece Job', 'Piece Job')])
    created_at = models.DateTimeField(auto_now_add=True)  # Track when the group was created

    def __str__(self):
        return self.name


class Message(models.Model):
    group = models.ForeignKey('Group', on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
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
    tutor = models.OneToOneField('CustomUser', on_delete=models.CASCADE, related_name="tutor_profile")  # Use string reference
    subjects = models.ManyToManyField('SubjectSpecialization', related_name="tutors")  # Use string reference
    available_times = models.TextField()  # A simple text field to store available times (could be refined)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"Tutor: {self.tutor.username}"


class TutoringSession(models.Model):
    tutor = models.ForeignKey('TutorProfile', on_delete=models.CASCADE, related_name="sessions")  # Use string reference
    student = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name="booked_sessions")  # Use string reference
    subject = models.CharField(max_length=100)
    date = models.DateTimeField()
    duration = models.IntegerField(help_text="Duration in minutes")
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('completed', 'Completed')], default='pending')

    def __str__(self):
        return f"Session with {self.tutor.tutor.username} for {self.student.username} on {self.date}"


class Booking(models.Model):
    student = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name="bookings")  # Use string reference
    tutor = models.ForeignKey('TutorProfile', on_delete=models.CASCADE, related_name="bookings")  # Use string reference
    session = models.ForeignKey('TutoringSession', on_delete=models.CASCADE, related_name="bookings")  # Use string reference
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('confirmed', 'Confirmed')], default='pending')

    def __str__(self):
        return f"Booking: {self.student.username} with {self.tutor.tutor.username} - Status: {self.status}"