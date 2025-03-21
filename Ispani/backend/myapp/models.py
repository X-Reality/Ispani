from django.db import models
from django.contrib.auth.models import AbstractUser



class StudentProfile(AbstractUser):
   
    year_of_study = models.IntegerField(null=True, blank=True)  # Add this field
    course= models.CharField(max_length=100, null=True, blank=True) 
    hobbies = models.TextField(null=True, blank=True)  # Add this field
    piece_jobs = models.TextField(null=True, blank=True)  # Add this field
    communication_preference = models.CharField(max_length=50, null=True, blank=True)
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
    year_of_study = models.IntegerField()
    course = models.CharField(max_length=100)
    # Provide a unique related_name for reverse relationship from StudentProfile
    members = models.ManyToManyField(StudentProfile, related_name='groups_in', blank=True)

    def __str__(self):
        return f"{self.name} - {self.course} (Year {self.year_of_study})"

class Message(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    recipient = models.ForeignKey(StudentProfile, related_name='received_messages', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.sender.username} - {self.timestamp}"  # or self.sender.get_full_name()

class Community(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    admin = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='administered_communities')
    members = models.ManyToManyField(StudentProfile, related_name='communities')
    groups = models.ManyToManyField(Group, related_name='communities')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.names