from django.db import models
from django.utils.crypto import get_random_string
from .authentication import CustomUser

class Group(models.Model):
    GROUP_TYPES = (
        ('study', 'Study Group'),
        ('hobby', 'Hobby Group'),
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    group_type = models.CharField(max_length=20, choices=GROUP_TYPES)
    course = models.CharField(max_length=100, blank=True)
    year_of_study = models.IntegerField(null=True, blank=True)
    hobbies = models.CharField(max_length=200, blank=True)
    members = models.ManyToManyField(CustomUser, related_name='custom_groups')
    admin = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='administered_groups')
    created_at = models.DateTimeField(auto_now_add=True)
    invite_link = models.CharField(max_length=20, unique=True)
     
    def save(self, *args, **kwargs):
        if not self.invite_link:
            self.invite_link = get_random_string(20)
        super().save(*args, **kwargs)

class GroupMembership(models.Model):
    ROLE_CHOICES = (
        ('ADMIN', 'Administrator'),
        ('MODERATOR', 'Moderator'),
        ('MEMBER', 'Member'),
    )
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='MEMBER')
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'group')