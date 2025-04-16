from rest_framework import serializers
from ..models import ChatMessage, MessageAttachment,ChatRoom,PrivateChat,PrivateMessage
from ..serializers import UserSerializer

class ChatRoomSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True, read_only=True)

    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'chat_type', 'members', 'created_at']

class MessageAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageAttachment
        fields = ['id', 'file', 'attachment_type', 'thumbnail']

class ChatMessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    attachments = MessageAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = ChatMessage
        fields = ['id', 'room', 'sender', 'content', 'attachments', 'timestamp']
        read_only_fields = ['sender', 'timestamp']

class PrivateChatSerializer(serializers.ModelSerializer):
    user1 = UserSerializer(read_only=True)
    user2 = UserSerializer(read_only=True)

    class Meta:
        model = PrivateChat
        fields = ['id', 'user1', 'user2', 'created_at']

class PrivateMessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = PrivateMessage
        fields = ['id', 'chat', 'sender', 'content', 'timestamp']
        read_only_fields = ['sender', 'timestamp']
