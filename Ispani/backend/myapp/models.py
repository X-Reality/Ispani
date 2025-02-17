from django.db import models
from django.contrib.auth.models import AbstractUser



ROLE_CHOICES = (
    ('student', 'Student'),
)

class StudentProfile(AbstractUser):
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='student')
    year_of_study = models.IntegerField(null=True, blank=True)  # Add this field
    field_of_study = models.CharField(max_length=100, null=True, blank=True) 
    interests = models.TextField(null=True, blank=True)  # Add this field
    desired_jobs = models.TextField(null=True, blank=True)  # Add this field

    # Add unique related_name to avoid clash with auth.User
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="studentprofile_groups",  # Unique related_name
        related_query_name="studentprofile",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="studentprofile_user_permissions",  # Unique related_name
        related_query_name="studentprofile",
    )

    def __str__(self):
        return self.get_full_name() or self.username  # Use full name if available, otherwise username

class Group(models.Model):
    name = models.CharField(max_length=100)
    year_of_study = models.IntegerField(null=True, blank=True)
    field_of_study = models.CharField(max_length=255, null=True, blank=True)
    # Provide a unique related_name for reverse relationship from StudentProfile
    members = models.ManyToManyField(StudentProfile, related_name='groups_in', blank=True)

    def __str__(self):
        return f"{self.name} - {self.field_of_study} (Year {self.year_of_study})"

class Message(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} - {self.timestamp}"  # or self.sender.get_full_name()

class SubjectSpecialization(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class TutorProfile(models.Model):
    tutor = models.OneToOneField(StudentProfile, on_delete=models.CASCADE, related_name="tutor_profile")
    subjects = models.ManyToManyField(SubjectSpecialization, related_name="tutors")  # Many-to-many without intermediate model
    available_times = models.TextField()  # A simple text field to store available times (could be refined)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"Tutor: {self.tutor.username}"
    
class TutoringSession(models.Model):
    tutor = models.ForeignKey(TutorProfile, on_delete=models.CASCADE, related_name="sessions")
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="booked_sessions")
    subject = models.CharField(max_length=100)
    date = models.DateTimeField()
    duration = models.IntegerField(help_text="Duration in minutes")
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('completed', 'Completed')], default='pending')

    def __str__(self):
        return f"Session with {self.tutor.tutor.username} for {self.student.username} on {self.date}"
    
class Booking(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="bookings")
    tutor = models.ForeignKey(TutorProfile, on_delete=models.CASCADE, related_name="bookings")
    session = models.ForeignKey(TutoringSession, on_delete=models.CASCADE, related_name="bookings")
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('confirmed', 'Confirmed')], default='pending')

    def __str__(self):
        return f"Booking: {self.student.username} with {self.tutor.tutor.username} - Status: {self.status}"
