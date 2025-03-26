import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ChatRoom, ChatMessage, PrivateChat, PrivateMessage
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        sender_id = data['sender_id']
        message = data['message']

        user = await User.objects.aget(id=sender_id)
        room = await ChatRoom.objects.aget(id=self.room_id)
        chat_message = await ChatMessage.objects.acreate(room=room, sender=user, content=message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'sender': user.username,
                'message': chat_message.content,
                'timestamp': str(chat_message.timestamp)
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'sender': event['sender'],
            'message': event['message'],
            'timestamp': event['timestamp']
        }))



class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f'private_chat_{self.chat_id}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        sender_id = data['sender_id']
        message = data['message']

        user = await User.objects.aget(id=sender_id)
        chat = await PrivateChat.objects.aget(id=self.chat_id)
        chat_message = await PrivateMessage.objects.acreate(chat=chat, sender=user, content=message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'sender': user.username,
                'message': chat_message.content,
                'timestamp': str(chat_message.timestamp)
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'sender': event['sender'],
            'message': event['message'],
            'timestamp': event['timestamp']
        }))
