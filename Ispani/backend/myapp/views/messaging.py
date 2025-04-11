from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from ..models import CustomUser,ChatRoom, ChatMessage, PrivateChat, PrivateMessage
from ..serializers import ChatMessageSerializer, ChatRoomSerializer,PrivateChatSerializer, PrivateMessageSerializer

class ChatRoomListCreateView(generics.ListCreateAPIView):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]

class ChatMessageListView(generics.ListAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        room_id = self.kwargs['room_id']
        return ChatMessage.objects.filter(room_id=room_id).order_by('timestamp')

class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        room = get_object_or_404(ChatRoom, id=room_id)
        serializer = ChatMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(sender=request.user, room=room)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class PrivateChatListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user1 = request.user
        user2_id = request.data.get("user2_id")
        user2 = get_object_or_404(CustomUser, id=user2_id)

        chat, created = PrivateChat.objects.get_or_create(
            user1=min(user1, user2, key=lambda u: u.id),
            user2=max(user1, user2, key=lambda u: u.id)
        )
        serializer = PrivateChatSerializer(chat)
        return Response(serializer.data, status=201 if created else 200)

class PrivateMessageListView(generics.ListAPIView):
    serializer_class = PrivateMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        chat_id = self.kwargs['chat_id']
        return PrivateMessage.objects.filter(chat_id=chat_id).order_by('timestamp')

class SendPrivateMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, chat_id):
        chat = get_object_or_404(PrivateChat, id=chat_id)
        serializer = PrivateMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(sender=request.user, chat=chat)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)