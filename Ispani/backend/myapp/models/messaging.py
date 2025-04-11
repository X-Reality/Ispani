import os
from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from .authentication import CustomUser, StudentProfile

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

class UserStatus(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='status')
    is_online = models.BooleanField(default=False)
    last_active = models.DateTimeField(auto_now=True)
    status_message = models.CharField(max_length=100, blank=True, default="Available")

    def __str__(self):
        return f"{self.user.username} - {'Online' if self.is_online else 'Offline'}"
