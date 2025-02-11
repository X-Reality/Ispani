# models.py
from django.db import models
from django.contrib.auth.models import User

class Group(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    skills = models.CharField(max_length=255, blank=True, null=True)
    preferences = models.CharField(max_length=255, blank=True, null=True)  # Preferences of the student
    groups = models.ManyToManyField(Group, related_name='members', blank=True)  # Automatically assign groups based on preferences

    def __str__(self):
        return self.user.username


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.timestamp}"


# models.py
class Project(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects")
    participants = models.ManyToManyField(User, related_name="project_participants", blank=True)

    def __str__(self):
        return self.title
    

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField()

    def __str__(self):
        return f"Comment by {self.user.username}"


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, related_name='likes', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} liked {self.project.title}"

# models.py
class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    group = models.ForeignKey(Group, related_name='events', on_delete=models.CASCADE)

    def __str__(self):
        return self.title

# models.py
class RSVP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, related_name='rsvps', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} is attending {self.event.title}"
