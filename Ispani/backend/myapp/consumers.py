
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Group, Message, CustomUser, DirectMessage
from django.utils import timezone

class GroupChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_id = self.scope['url_route']['kwargs']['group_id']
        self.room_group_name = f'chat_group_{self.group_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        user_id = text_data_json['user_id']

        # Save message to database
        message_obj = await self.save_message(user_id, message)
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user_id': user_id,
                'username': message_obj['username'],
                'timestamp': message_obj['timestamp'].isoformat(),
                'message_id': message_obj['id']
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'user_id': event['user_id'],
            'username': event['username'],
            'timestamp': event['timestamp'],
            'message_id': event['message_id']
        }))

    @database_sync_to_async
    def save_message(self, user_id, message):
        user = CustomUser.objects.get(id=user_id)
        group = Group.objects.get(id=self.group_id)
        msg = Message.objects.create(
            group=group,
            sender=user,
            content=message
        )
        return {
            'id': msg.id,
            'username': user.username,
            'timestamp': msg.timestamp
        }


class DirectChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get the recipient user_id from the URL
        self.recipient_id = self.scope['url_route']['kwargs']['user_id']
        self.user = self.scope['user']
        
        # Create a unique room name for the two users
        # We sort the IDs to ensure the same room name regardless of who initiates
        user_ids = sorted([str(self.user.id), self.recipient_id])
        self.room_group_name = f'chat_direct_{user_ids[0]}_{user_ids[1]}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender_id = text_data_json['sender_id']
        recipient_id = text_data_json['recipient_id']

        # Save message to database
        message_obj = await self.save_direct_message(sender_id, recipient_id, message)
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'direct_message',
                'message': message,
                'sender_id': sender_id,
                'recipient_id': recipient_id,
                'sender_username': message_obj['sender_username'],
                'timestamp': message_obj['timestamp'].isoformat(),
                'message_id': message_obj['id']
            }
        )

    # Receive message from room group
    async def direct_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_id': event['sender_id'],
            'recipient_id': event['recipient_id'],
            'sender_username': event['sender_username'],
            'timestamp': event['timestamp'],
            'message_id': event['message_id']
        }))

    @database_sync_to_async
    def save_direct_message(self, sender_id, recipient_id, message):
        sender = CustomUser.objects.get(id=sender_id)
        recipient = CustomUser.objects.get(id=recipient_id)
        
        msg = DirectMessage.objects.create(
            sender=sender,
            recipient=recipient,
            content=message
        )
        
        return {
            'id': msg.id,
            'sender_username': sender.username,
            'timestamp': msg.timestamp
        }