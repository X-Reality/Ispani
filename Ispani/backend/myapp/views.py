import string
import random
import requests
import json
import uuid
import os
import logging
import stripe


from django.contrib.auth import authenticate, login, logout
from django.forms import ValidationError
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.core.mail import send_mail
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta
from django.http import Http404, JsonResponse
from django.utils.crypto import get_random_string
from django.db.models import Q, Count
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from datetime import datetime, timedelta

from rest_framework import viewsets, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework_simplejwt.tokens import RefreshToken


from .models import (
    CalendlyEvent, CustomUser, ExternalCalendarConnection, MeetingProvider, StudentProfile, TutorProfile, Group, Event,
    EventParticipant, EventTag, EventComment, EventMedia,
    ChatRoom, ChatMessage, UserStatus, GroupMembership,
    PrivateChat, PrivateMessage,TutorAvailability,Booking,Payment
)
from .serializers import (
    UserSerializer, UserRegistrationSerializer,
    ChatMessageSerializer, ChatRoomSerializer,
    JoinGroupSerializer, UserStatusSerializer,EventSerializer,
    EventDetailSerializer,EventParticipantSerializer,
    EventCommentSerializer, EventMediaSerializer, EventTagSerializer,
    GroupSerializer, GroupMembershipSerializer,
    PrivateChatSerializer, PrivateMessageSerializer,
    TutorProfileSerializer, StudentProfileSerializer,
    TutorAvailabilitySerializer, ExternalCalendarConnectionSerializer, MeetingProviderSerializer,
    CalendlyEventSerializer, BookingSerializer, GroupSessionParticipantSerializer,
    PaymentSerializer, CalendlyConnectionSerializer, CalendlyOAuthCallbackSerializer,
    JoinGroupSessionSerializer

)
from Ispani.Ispani.backend.myapp import models

logger = logging.getLogger(__name__)

# ------------------- User Registration and Authentication -------------------
stripe.api_key = settings.STRIPE_SECRET_KEY


class SignUpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        role = request.data.get("role", "student")

        if not email or not password:
            return Response({"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        if CustomUser.objects.filter(email=email).exists():
            return Response({"error": "Email already in use"}, status=status.HTTP_400_BAD_REQUEST)

        otp = get_random_string(6, allowed_chars=string.digits)
        cache.set(email, {'otp': otp, 'password': password, 'role': role}, timeout=300)

        send_mail(
            "Your OTP Code",
            f"Your OTP code is {otp}. It expires in 5 minutes.",
            "noreply@example.com",
            [email],
            fail_silently=False,
        )

        return Response({"message": "OTP sent to email"}, status=status.HTTP_200_OK)

class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")

        cached_data = cache.get(email)
        if not cached_data or cached_data.get('otp') != otp:
            return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)

        temp_token = str(uuid.uuid4())
        cache.set(temp_token, {
            'email': email,
            'password': cached_data['password'],
            'role': cached_data['role']
        }, timeout=600)

        cache.delete(email)

        return Response({
            "message": "OTP verified.",
            "temp_token": temp_token,
            "role": cached_data['role']
        }, status=status.HTTP_200_OK)

class CompleteRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        temp_token = request.data.get("temp_token")
        temp_data = cache.get(temp_token)

        if not temp_data:
            return Response({"error": "Invalid or expired session."}, status=status.HTTP_400_BAD_REQUEST)

        registration_data = {
            'username': request.data.get("username"),
            'email': temp_data['email'],
            'password': temp_data['password'],
            'role': temp_data['role']
        }

        if temp_data['role'] == 'student':
            registration_data['student_profile'] = {
                'year_of_study': request.data.get("year_of_study"),
                'course': request.data.get("course"),
                'hobbies': request.data.get("hobbies"),
                'piece_jobs': request.data.get("piece_jobs"),
                'communication_preference': request.data.get("communication_preference")
            }
        elif temp_data['role'] == 'tutor':
            registration_data['tutor_profile'] = {
                'subject_expertise': request.data.get('subject_expertise'),
                'hourly_rate': request.data.get('hourly_rate'),
                'qualifications': request.data.get('qualifications'),
                'availability': request.data.get('availability')
            }

        serializer = UserRegistrationSerializer(data=registration_data)
        if serializer.is_valid():
            user = serializer.save()
            cache.delete(temp_token)

            authenticated_user = authenticate(username=user.username, password=temp_data['password'])
            if authenticated_user:
                login(request, authenticated_user)
                refresh = RefreshToken.for_user(authenticated_user)

                response_data = {
                    "message": "Registration completed successfully",
                    "user": UserSerializer(authenticated_user).data,
                    "token": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    }
                }

                return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
            authenticated_user = authenticate(username=user.username, password=password)

            if authenticated_user and authenticated_user.is_active:
                login(request, authenticated_user)
                refresh = RefreshToken.for_user(authenticated_user)

                response_data = {
                    "message": "Login successful",
                    "user": UserSerializer(authenticated_user).data,
                    "token": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    }
                }

                return Response(response_data, status=status.HTTP_200_OK)

        except CustomUser.DoesNotExist:
            pass

        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"message": "Logout successful. Please delete the token on the client side."})

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class UpdateUserStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        status_message = request.data.get('status_message')

        user_status, created = UserStatus.objects.get_or_create(user=request.user)

        if status_message is not None:
            user_status.status_message = status_message

        user_status.is_online = True
        user_status.save()

        return Response(UserStatusSerializer(user_status).data)

    def delete(self, request):
        user_status, created = UserStatus.objects.get_or_create(user=request.user)
        user_status.is_online = False
        user_status.save()

        return Response({"message": "Status updated to offline"})

class SwitchRoleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        target_role = request.data.get('role')
        
        if target_role not in ['student', 'tutor']:
            return Response({"error": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST)

        if target_role == 'tutor':
            if not hasattr(request.user, 'tutor_profile'):
                return Response({
                    "message": "Please complete your tutor profile first",
                    "status": "profile_incomplete"
                }, status=status.HTTP_400_BAD_REQUEST)
                
            if request.user.tutor_profile.verification_status != 'approved':
                return Response({
                    "message": "Tutor application pending approval",
                    "status": request.user.tutor_profile.verification_status
                }, status=status.HTTP_200_OK)
        
        request.user.role = target_role
        request.user.save()
        
        return Response({
            "message": f"Switched to {target_role} role",
            "role": target_role
        })

# ------------------- Group Management -------------------

class GroupListCreate(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class CreateGroupView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        name = request.data.get('name')
        description = request.data.get('description', '')
        group_type = request.data.get('group_type', '')
        course = request.data.get('course')
        year_of_study = request.data.get('year_of_study')
        hobbies = request.data.get('hobbies')

        if not name:
            return Response({"error": "Group name is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if group_type == 'study' and not (course and year_of_study):
            return Response({"error": "Both course and year of study are required for study groups"}, 
                             status=status.HTTP_400_BAD_REQUEST)

        if group_type == 'hobby' and not hobbies:
            return Response({"error": "Hobbies are required for hobby groups"}, 
                             status=status.HTTP_400_BAD_REQUEST)

        group = Group.objects.create(
            name=name,
            description=description,
            group_type=group_type,
            course=course if group_type == 'study' else '',
            year_of_study=year_of_study if group_type == 'study' else None,
            hobbies=hobbies if group_type == 'hobby' else '',
            admin=request.user,
            invite_link=get_random_string(20)
        )

        group.members.add(request.user)

        serializer = GroupSerializer(group)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_group(request):
    group_id = request.data.get('group_id')
    
    if not group_id:
        return Response({"error": "group_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    group = get_object_or_404(Group, id=group_id)

    if group.members.filter(id=request.user.id).exists():
        return Response({"error": "You are already a member of this group"}, status=status.HTTP_400_BAD_REQUEST)

    group.members.add(request.user)

    return Response({"message": "You have successfully joined the group."}, status=status.HTTP_200_OK)

@api_view(['GET'])
def study_groups(request):
    study_groups = Group.objects.filter(group_type='study')
    serializer = GroupSerializer(study_groups, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def hobby_groups(request):
    hobby_groups = Group.objects.filter(group_type='hobby')
    serializer = GroupSerializer(hobby_groups, many=True)
    return Response(serializer.data)

# ------------------- Messaging -------------------

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

# ------------------- Group Management by Admin -------------------

class GroupManagementView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, group_id):
        group = get_object_or_404(Group, id=group_id)

        if not group.admin == request.user:
            return Response({"error": "Only admins can add members"}, status=status.HTTP_403_FORBIDDEN)

        user_id = request.data.get('user_id')
        role = request.data.get('role', 'MEMBER')

        if not user_id:
            return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(CustomUser, id=user_id)

        if group.members.filter(id=user.id).exists():
            return Response({"error": "User is already a member of this group"}, status=status.HTTP_400_BAD_REQUEST)

        group.members.add(user)
        membership, created = GroupMembership.objects.get_or_create(
            user=user,
            group=group,
            defaults={'role': role}
        )

        return Response(GroupMembershipSerializer(membership).data, status=status.HTTP_201_CREATED)

    def delete(self, request, group_id):
        group = get_object_or_404(Group, id=group_id)
        user_id = request.data.get('user_id')

        if not user_id:
            return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(CustomUser, id=user_id)

        if user.id != request.user.id and not group.admin == request.user:
            return Response({"error": "Only admins can remove other members"}, status=status.HTTP_403_FORBIDDEN)

        group.members.remove(user)
        GroupMembership.objects.filter(user=user, group=group).delete()

        return Response({"message": "Member removed successfully"}, status=status.HTTP_200_OK)

    def patch(self, request, group_id):
        group = get_object_or_404(Group, id=group_id)

        if not group.admin == request.user:
            return Response({"error": "Only admins can update roles"}, status=status.HTTP_403_FORBIDDEN)

        user_id = request.data.get('user_id')
        role = request.data.get('role')

        if not user_id or not role:
            return Response({"error": "user_id and role are required"}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(CustomUser, id=user_id)

        try:
            membership = GroupMembership.objects.get(user=user, group=group)
            membership.role = role
            membership.save()

            return Response(GroupMembershipSerializer(membership).data)
        except GroupMembership.DoesNotExist:
            return Response({"error": "User is not a member of this group"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_group_by_invite(request):
    invite_link = request.data.get('invite_link')

    if not invite_link:
        return Response({"error": "invite_link is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        group = Group.objects.get(invite_link=invite_link)
    except Group.DoesNotExist:
        return Response({"error": "Invalid invite link"}, status=status.HTTP_404_NOT_FOUND)

    if group.members.filter(id=request.user.id).exists():
        return Response({"error": "You are already a member of this group"}, status=status.HTTP_400_BAD_REQUEST)

    group.members.add(request.user)
    GroupMembership.objects.create(user=request.user, group=group)

    return Response({
        "message": f"You have joined the group: {group.name}",
        "group_id": group.id
    }, status=status.HTTP_200_OK)

# ------------------- Find Students -------------------

class FindStudentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('q', '')

        if len(query) < 3:
            return Response({"error": "Query must be at least 3 characters"}, status=status.HTTP_400_BAD_REQUEST)

        students = CustomUser.objects.filter(
            Q(username__icontains=query) |
            Q(student_profile__course__icontains=query) |
            Q(student_profile__hobbies__icontains=query),
            role='student'
        ).exclude(id=request.user.id).distinct()

        serializer = UserSerializer(students, many=True)
        return Response(serializer.data)





class TutorAvailabilityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get tutor ID from query params or use current user
        tutor_id = request.query_params.get('tutor_id', request.user.id)
        
        if tutor_id != str(request.user.id) and not request.user.is_staff:
            return Response({"error": "You can only view your own availabilities"}, status=403)
        
        availabilities = TutorAvailability.objects.filter(
            tutor_id=tutor_id,
            end_time__gt=timezone.now()
        ).order_by('start_time')
        
        serializer = TutorAvailabilitySerializer(availabilities, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.user.role != 'tutor':
            return Response({"error": "Only tutors can set availability"}, status=403)
        
        # Expecting list of time slots
        time_slots = request.data.get('time_slots', [])
        created_slots = []
        
        for slot in time_slots:
            serializer = TutorAvailabilitySerializer(data={
                'tutor': request.user.id,
                'start_time': slot['start_time'],
                'end_time': slot['end_time']
            })
            
            if serializer.is_valid():
                serializer.save()
                created_slots.append(serializer.data)
            else:
                # If one slot fails, delete all created slots in this batch
                TutorAvailability.objects.filter(id__in=[s['id'] for s in created_slots]).delete()
                return Response(serializer.errors, status=400)
        
        return Response(created_slots, status=201)

class ExternalCalendarConnectionViewSet(viewsets.ModelViewSet):
    serializer_class = ExternalCalendarConnectionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ExternalCalendarConnection.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def connect_calendly(self, request):
        serializer = CalendlyConnectionSerializer({})
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def fetch_availability(self, request, pk=None):
        connection = self.get_object()

        if connection.provider != 'calendly':
            return Response({'error': 'This endpoint only works with Calendly connections'}, 
                            status=status.HTTP_400_BAD_REQUEST)
    
        # Get Calendly user URI
        user_uri = connection.provider_user_id
        
        # Get current date in ISO format
        today = datetime.now().date().isoformat()
        two_months_later = (datetime.now() + timedelta(days=60)).date().isoformat()
        
        # Call Calendly API to get available time slots
        headers = {
            'Authorization': f'Bearer {connection.access_token}',
            'Content-Type': 'application/json'
        }
        
        # Get user's event types
        event_types_url = f"https://api.calendly.com/event_types?user={user_uri}"
        event_types_response = requests.get(event_types_url, headers=headers)
        
        if event_types_response.status_code != 200:
            return Response({'error': 'Failed to fetch Calendly event types'}, 
                            status=status.HTTP_400_BAD_REQUEST)
    
        event_types = event_types_response.json().get('collection', [])
        
        # Return data that can be used to display availability or redirect to Calendly
        return Response({
            'event_types': event_types,
            'calendly_user': connection.calendly_username,
            'booking_url': f"https://calendly.com/{connection.calendly_username}"
        })

class CalendlyOAuthCallbackView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        serializer = CalendlyOAuthCallbackSerializer(data=request.query_params)
        if serializer.is_valid():
            code = serializer.validated_data['code']
            
            # Exchange code for token
            token_url = 'https://auth.calendly.com/oauth/token'
            payload = {
                'client_id': settings.CALENDLY_CLIENT_ID,
                'client_secret': settings.CALENDLY_CLIENT_SECRET,
                'code': code,
                'redirect_uri': settings.CALENDLY_REDIRECT_URI,
                'grant_type': 'authorization_code'
            }
            
            response = requests.post(token_url, data=payload)
            if response.status_code == 200:
                token_data = response.json()
                
                # Get user info
                user_url = 'https://api.calendly.com/users/me'
                headers = {
                    'Authorization': f"Bearer {token_data['access_token']}"
                }
                
                user_response = requests.get(user_url, headers=headers)
                if user_response.status_code == 200:
                    user_data = user_response.json()
                    
                    # Create or update connection
                    connection, created = ExternalCalendarConnection.objects.update_or_create(
                        user=request.user,
                        provider='calendly',
                        defaults={
                            'provider_user_id': user_data['resource']['uri'],
                            'access_token': token_data['access_token'],
                            'refresh_token': token_data.get('refresh_token'),
                            'token_expires_at': datetime.now() + timedelta(seconds=token_data['expires_in']),
                            'calendly_username': user_data['resource']['name'],
                            'calendly_uri': user_data['resource']['uri'],
                            'is_active': True
                        }
                    )
                    
                    return Response({
                        'message': 'Calendly account connected successfully',
                        'username': user_data['resource']['name']
                    })
            
            return Response({'error': 'Failed to connect Calendly account'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MeetingProviderViewSet(viewsets.ModelViewSet):
    serializer_class = MeetingProviderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return MeetingProvider.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # If this is set as default, unset other defaults
        if serializer.validated_data.get('is_default', False):
            MeetingProvider.objects.filter(user=self.request.user, is_default=True).update(is_default=False)
        
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        provider = self.get_object()
        MeetingProvider.objects.filter(user=request.user, is_default=True).update(is_default=False)
        provider.is_default = True
        provider.save()
        return Response({'status': 'Default meeting provider set'})

class CalendlyWebhookView(APIView):
    permission_classes = []  # No authentication needed for webhooks
    
    def post(self, request):
        payload = request.data
        event_type = payload.get('event')
        
        if event_type == 'invitee.created':
            # Someone booked a time through Calendly
            return self.handle_invitee_created(payload)
        elif event_type == 'invitee.canceled':
            # Someone canceled their booking
            return self.handle_invitee_canceled(payload)
        
        return Response({'status': 'ignore'})
    
    def handle_invitee_created(self, payload):
        # Extract the needed data from Calendly webhook
        event_data = payload.get('payload', {}).get('event', {})
        invitee_data = payload.get('payload', {}).get('invitee', {})
        
        # Find associated tutor by URI
        calendly_uri = event_data.get('uri', '').split('/')[4]  # Extract user ID from URI
        
        try:
            calendar_connection = ExternalCalendarConnection.objects.get(
                provider='calendly',
                provider_user_id__contains=calendly_uri
            )
            
            tutor = calendar_connection.user
            
            # Create calendly event
            calendly_event = CalendlyEvent.objects.create(
                tutor=tutor,
                calendly_event_id=event_data.get('uuid'),
                calendly_event_uri=event_data.get('uri'),
                event_type_name=event_data.get('name', 'Session'),
                start_time=event_data.get('start_time'),
                end_time=event_data.get('end_time'),
                invitee_email=invitee_data.get('email'),
                invitee_name=invitee_data.get('name'),
                location=event_data.get('location', {}).get('join_url'),
                cancellation_url=invitee_data.get('cancel_url'),
                reschedule_url=invitee_data.get('reschedule_url'),
                is_group_event=False,  # Assuming default is one-on-one
            )
            
            # Try to find or create the student
            student, created = CustomUser.objects.get_or_create(
                email=invitee_data.get('email'),
                defaults={
                    'username': invitee_data.get('email').split('@')[0],
                    'role': 'student'
                }
            )
            
            # Calculate duration in minutes
            start = datetime.fromisoformat(event_data.get('start_time').replace('Z', '+00:00'))
            end = datetime.fromisoformat(event_data.get('end_time').replace('Z', '+00:00'))
            duration = int((end - start).total_seconds() / 60)
            
            # Calculate price based on tutor's hourly rate
            hourly_rate = tutor.tutor_profile.hourly_rate
            price = float(hourly_rate) * (duration / 60)
            
            # Create booking
            booking = Booking.objects.create(
                student=student,
                tutor=tutor,
                subject=event_data.get('name', 'Tutoring Session'),
                notes=invitee_data.get('questions_and_answers', [{}])[0].get('answer', ''),
                status='pending',
                booking_source='calendly',
                meeting_link=event_data.get('location', {}).get('join_url'),
                price=price,
                duration_minutes=duration,
                calendly_event=calendly_event
            )
            
            # Create payment record
            Payment.objects.create(
                booking=booking,
                student=student,
                amount=price,
                payment_intent_id=f"calendly_{uuid.uuid4()}",
                status='pending'
            )
            
            # TODO: Send email to student about payment
            
            return Response({'status': 'success'})
        
        except ExternalCalendarConnection.DoesNotExist:
            return Response({'status': 'error', 'message': 'No matching tutor found'}, 
                            status=status.HTTP_404_NOT_FOUND)
    
    def handle_invitee_canceled(self, payload):
        event_uuid = payload.get('payload', {}).get('event', {}).get('uuid')
        
        try:
            calendly_event = CalendlyEvent.objects.get(calendly_event_id=event_uuid)
            calendly_event.status = 'cancelled'
            calendly_event.save()
            
            # Update related booking
            bookings = Booking.objects.filter(calendly_event=calendly_event)
            for booking in bookings:
                booking.status = 'cancelled'
                booking.save()
            
            return Response({'status': 'success'})
        
        except CalendlyEvent.DoesNotExist:
            return Response({'status': 'error', 'message': 'Event not found'}, 
                            status=status.HTTP_404_NOT_FOUND)

class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'tutor':
            return Booking.objects.filter(tutor=user)
        else:
            return Booking.objects.filter(student=user)
    
    @action(detail=True, methods=['post'])
    def confirm_payment(self, request, pk=None):
        booking = self.get_object()
        
        # Check if the user is the student in this booking
        if request.user != booking.student:
            return Response({'error': 'You can only confirm payments for your own bookings'}, 
                           status=status.HTTP_403_FORBIDDEN)
        
        # In a real implementation, you would process payment here
        # For this example, we'll just mark the payment as completed
        payment = Payment.objects.filter(booking=booking, student=request.user).first()
        
        if payment:
            payment.status = 'completed'
            payment.paid_at = datetime.now()
            payment.save()
            
            # If this is a group session, update participant's payment status
            if booking.is_group_session:
                participant = GroupSessionParticipant.objects.filter(
                    booking=booking, student=request.user
                ).first()
                
                if participant:
                    participant.payment_status = 'completed'
                    participant.save()
            
            # Set booking to confirmed
            booking.status = 'confirmed'
            booking.save()
            
            return Response({
                'status': 'success',
                'meeting_link': booking.meeting_link
            })
        
        return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def get_meeting_link(self, request, pk=None):
        booking = self.get_object()
        
        # Check if the user is part of this booking
        if request.user != booking.student and request.user != booking.tutor:
            return Response({'error': 'You are not authorized to access this booking'}, 
                           status=status.HTTP_403_FORBIDDEN)
        
        # If user is a tutor, provide the link immediately
        if request.user.role == 'tutor':
            return Response({'meeting_link': booking.meeting_link})
        
        # If user is a student, check payment status
        if booking.is_group_session:
            participant = GroupSessionParticipant.objects.filter(
                booking=booking, student=request.user
            ).first()
            
            if participant and participant.payment_status == 'completed':
                return Response({'meeting_link': booking.meeting_link})
        else:
            payment = Payment.objects.filter(
                booking=booking, student=request.user, status='completed'
            ).exists()
            
            if payment:
                return Response({'meeting_link': booking.meeting_link})
        
        return Response({'error': 'Payment required before accessing meeting link'}, 
                       status=status.HTTP_402_PAYMENT_REQUIRED)

def get_calendly_event_types(request):
    headers = {
        "Authorization": f"Bearer {settings.CALENDLY_API_KEY}",
        "Content-Type": "application/json"
    }

    # First get your user URI
    user_response = requests.get("https://api.calendly.com/users/me", headers=headers)
    user_uri = user_response.json().get("resource", {}).get("uri")

    # Now fetch event types
    event_types_response = requests.get(
        f"https://api.calendly.com/event_types?user={user_uri}",
        headers=headers
    )
    return JsonResponse(event_types_response.json())

class GroupSessionViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request):
        # List available group sessions
        group_sessions = Booking.objects.filter(
            is_group_session=True,
            status='confirmed',
            start_time__gt=datetime.now(),
            current_participants__lt=models.F('max_participants')
        )
        
        serializer = BookingSerializer(group_sessions, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def join(self, request):
        serializer = JoinGroupSessionSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            participant = serializer.save()
            return Response({
                'status': 'success',
                'message': 'You have joined this group session',
                'payment_required': True,
                'booking_id': serializer.validated_data['booking_id']
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EventListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        List all events the user can access (public events and private events they're invited to)
        Supports filtering by various parameters
        """
        # Get query parameters
        event_type = request.query_params.get('event_type')
        tag = request.query_params.get('tag')
        search = request.query_params.get('search')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        my_events = request.query_params.get('my_events') == 'true'
        participating = request.query_params.get('participating') == 'true'
        
        # Base queryset
        if my_events:
            # Events created by current user
            queryset = Event.objects.filter(creator=request.user)
        elif participating:
            # Events the user is participating in
            user_events = EventParticipant.objects.filter(
                user=request.user,
                status='going'
            ).values_list('event_id', flat=True)
            queryset = Event.objects.filter(id__in=user_events)
        else:
            # All events user can access
            queryset = Event.objects.filter(
                Q(is_public=True) | 
                Q(participants__user=request.user)
            ).distinct()
        
        # Apply filters
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        
        if tag:
            queryset = queryset.filter(tags__name=tag)
        
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(location__icontains=search)
            )
        
        if date_from:
            queryset = queryset.filter(start_time__gte=date_from)
        
        if date_to:
            queryset = queryset.filter(start_time__lte=date_to)
        
        # Order by start time (upcoming first)
        queryset = queryset.filter(end_time__gte=timezone.now()).order_by('start_time')
        
        serializer = EventSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    def post(self, request):
        """Create a new event"""
        serializer = EventSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EventDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk):
        """Get event or return 404"""
        event = get_object_or_404(Event, pk=pk)
        
        # Check if user can access this event
        if not event.is_public:
            if not EventParticipant.objects.filter(event=event, user=self.request.user).exists():
                # If private event and user is not a participant, deny access
                raise Http404("Event not found")
        
        return event
    
    def get(self, request, pk):
        """Get event details"""
        event = self.get_object(pk)
        serializer = EventDetailSerializer(event, context={'request': request})
        return Response(serializer.data)
    
    def put(self, request, pk):
        """Update event"""
        event = self.get_object(pk)
        
        # Only the creator can update the event
        if event.creator != request.user:
            return Response(
                {"detail": "You don't have permission to edit this event"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = EventSerializer(event, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        """Delete event"""
        event = self.get_object(pk)
        
        # Only the creator can delete the event
        if event.creator != request.user:
            return Response(
                {"detail": "You don't have permission to delete this event"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class EventParticipationView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        """Join an event or update participation status"""
        event = get_object_or_404(Event, pk=pk)
        
        # Check if event is full
        if (event.participants.filter(status='going').count() >= event.max_participants and 
            not EventParticipant.objects.filter(event=event, user=request.user).exists()):
            return Response(
                {"detail": "This event has reached its maximum capacity"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get participation status
        status_value = request.data.get('status', 'going')
        if status_value not in [s[0] for s in EventParticipant.STATUS_CHOICES]:
            return Response(
                {"detail": f"Invalid status. Must be one of: {', '.join([s[0] for s in EventParticipant.STATUS_CHOICES])}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create or update participant
        participant, created = EventParticipant.objects.update_or_create(
            event=event,
            user=request.user,
            defaults={'status': status_value}
        )
        
        # If user is the creator, make sure they're an organizer
        if event.creator == request.user:
            participant.role = 'organizer'
            participant.save()
        
        serializer = EventParticipantSerializer(participant)
        return Response(serializer.data)
    
    def delete(self, request, pk):
        """Leave an event"""
        event = get_object_or_404(Event, pk=pk)
        
        # Creator can't leave their own event
        if event.creator == request.user:
            return Response(
                {"detail": "As the creator, you cannot leave your own event. You may delete it instead."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Remove participation
        EventParticipant.objects.filter(event=event, user=request.user).delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)

class EventInviteView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        """Invite users to an event"""
        event = get_object_or_404(Event, pk=pk)
        
        # Check if user has permission to invite (must be a participant)
        try:
            participant = EventParticipant.objects.get(event=event, user=request.user)
        except EventParticipant.DoesNotExist:
            return Response(
                {"detail": "You must be a participant to invite others"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get user IDs to invite
        user_ids = request.data.get('user_ids', [])
        if not user_ids:
            return Response(
                {"detail": "No users specified to invite"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Invite users
        invited_count = 0
        for user_id in user_ids:
            try:
                user = CustomUser.objects.get(id=user_id)
                if not EventParticipant.objects.filter(event=event, user=user).exists():
                    EventParticipant.objects.create(
                        event=event,
                        user=user,
                        status='invited'
                    )
                    invited_count += 1
                    
                    # Send notification/email here
                    
            except CustomUser.DoesNotExist:
                pass
        
        return Response({"invited_count": invited_count})

class EventCommentView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        """Get comments for an event"""
        event = get_object_or_404(Event, pk=pk)
        comments = EventComment.objects.filter(event=event).order_by('created_at')
        serializer = EventCommentSerializer(comments, many=True)
        return Response(serializer.data)
    
    def post(self, request, pk):
        """Add a comment to an event"""
        event = get_object_or_404(Event, pk=pk)
        
        # Check if user is a participant
        if not EventParticipant.objects.filter(event=event, user=request.user).exists():
            return Response(
                {"detail": "You must be a participant to comment"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = EventCommentSerializer(data={
            'content': request.data.get('content')
        })
        
        if serializer.is_valid():
            comment = serializer.save(event=event, user=request.user)
            return Response(EventCommentSerializer(comment).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EventMediaView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        """Get media for an event"""
        event = get_object_or_404(Event, pk=pk)
        media = EventMedia.objects.filter(event=event)
        serializer = EventMediaSerializer(media, many=True)
        return Response(serializer.data)
    
    def post(self, request, pk):
        """Add media to an event"""
        event = get_object_or_404(Event, pk=pk)
        
        # Check if user is a participant
        if not EventParticipant.objects.filter(event=event, user=request.user).exists():
            return Response(
                {"detail": "You must be a participant to add media"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = EventMediaSerializer(data={
            'file': request.data.get('file'),
            'media_type': request.data.get('media_type'),
            'title': request.data.get('title', '')
        })
        
        if serializer.is_valid():
            media = serializer.save(event=event, uploaded_by=request.user)
            return Response(EventMediaSerializer(media).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EventTagsView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get popular event tags"""
        tags = EventTag.objects.annotate(
            usage_count=Count('events')
        ).order_by('-usage_count')[:20]  # Top 20 tags
        
        serializer = EventTagSerializer(tags, many=True)
        return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def join_event_by_invite(request, invite_link):
    """Join an event using an invite link"""
    try:
        event = Event.objects.get(invite_link=invite_link)
    except Event.DoesNotExist:
        return Response({"detail": "Invalid invite link"}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if event is full
    if event.participants.filter(status='going').count() >= event.max_participants:
        return Response(
            {"detail": "This event has reached its maximum capacity"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Add user as participant
    participant, created = EventParticipant.objects.get_or_create(
        event=event,
        user=request.user,
        defaults={'status': 'going'}
    )
    
    if not created:
        participant.status = 'going'
        participant.save()
    
    serializer = EventDetailSerializer(event, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def upcoming_events(request):
    """Get upcoming events the user is participating in"""
    now = timezone.now()
    
    # Get events where the user is participating with status "going"
    user_events = EventParticipant.objects.filter(
        user=request.user,
        status='going',
        event__start_time__gt=now
    ).values_list('event_id', flat=True)
    
    events = Event.objects.filter(
        id__in=user_events
    ).order_by('start_time')[:5]  # Get next 5 events
    
    serializer = EventSerializer(events, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommended_events(request):
    """Get recommended events based on user interests and past participation"""
    now = timezone.now()
    user = request.user
    
    # Get user's past events
    past_events = EventParticipant.objects.filter(
        user=user,
        status='going',
        event__end_time__lt=now
    ).values_list('event_id', flat=True)
    
    # Get event types user has participated in
    event_types = Event.objects.filter(
        id__in=past_events
    ).values_list('event_type', flat=True).distinct()
    
    # Get tags from events user has participated in
    tags = Event.objects.filter(
        id__in=past_events
    ).values_list('tags__name', flat=True).distinct()
    
    # Find upcoming events that match user interests
    if hasattr(user, 'student_profile'):
        hobbies = user.student_profile.hobbies
    else:
        hobbies = ""
    
    recommended = Event.objects.filter(
        Q(is_public=True) &
        Q(end_time__gt=now) &
        (
            Q(event_type__in=event_types) |
            Q(tags__name__in=tags) |
            Q(description__icontains=hobbies) |
            Q(title__icontains=hobbies)
        )
    ).exclude(
        participants__user=user  # Exclude events user is already participating in
    ).distinct().order_by('start_time')[:10]
    
    serializer = EventSerializer(recommended, many=True, context={'request': request})
    return Response(serializer.data)