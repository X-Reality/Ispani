import string
import random
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
from django.utils import timezone
from datetime import timedelta
from django.http import Http404
from django.utils.crypto import get_random_string
from django.db.models import Q
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken

from .models import (
    CustomUser, StudentProfile, TutorProfile, Group, 
    ChatRoom, ChatMessage, UserStatus, GroupMembership,
    PrivateChat, PrivateMessage,TutorAvailability,Booking,Payment
)
from .serializers import (
    UserSerializer, UserRegistrationSerializer,
    ChatMessageSerializer, ChatRoomSerializer,
    JoinGroupSerializer, UserStatusSerializer,
    GroupSerializer, GroupMembershipSerializer,
    PrivateChatSerializer, PrivateMessageSerializer,
    TutorProfileSerializer, StudentProfileSerializer,
    TutorAvailabilitySerializer,CreateBookingSerializer,
    BookingSerializer,PaymentSerializer

)

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

class BookingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        bookings = Booking.objects.filter(
            models.Q(student=request.user) | models.Q(tutor=request.user)
        ).order_by('-created_at')
        
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CreateBookingSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            booking = serializer.save()
            
            # Mark availability as booked
            booking.availability.is_booked = True
            booking.availability.save()
            
            # Create payment intent
            try:
                payment_intent = stripe.PaymentIntent.create(
                    amount=int(booking.price * 100),  # in cents
                    currency='usd',
                    metadata={
                        'booking_id': booking.id,
                        'student_id': booking.student.id,
                        'tutor_id': booking.tutor.id
                    },
                    description=f"Tutoring session for {booking.subject}"
                )
                
                # Create payment record
                Payment.objects.create(
                    booking=booking,
                    amount=booking.price,
                    payment_intent_id=payment_intent.id
                )
                
                # Send notifications
                self.send_notification(booking)
                
                return Response({
                    'booking': BookingSerializer(booking).data,
                    'client_secret': payment_intent.client_secret
                }, status=201)
                
            except Exception as e:
                booking.delete()
                return Response({"error": str(e)}, status=400)
        
        return Response(serializer.errors, status=400)

    def send_notification(self, booking):
        # Implement your notification logic here
        # Could be email, websocket, or push notification
        pass

class BookingDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        booking = self.get_object(pk)
        
        if booking.student != request.user and booking.tutor != request.user:
            return Response({"error": "You don't have permission to view this booking"}, status=403)
        
        serializer = BookingSerializer(booking)
        return Response(serializer.data)

    def patch(self, request, pk):
        booking = self.get_object(pk)
        
        if booking.tutor != request.user:
            return Response({"error": "Only the tutor can update bookings"}, status=403)
        
        serializer = BookingSerializer(booking, data=request.data, partial=True)
        
        if serializer.is_valid():
            updated_booking = serializer.save()
            
            if 'status' in request.data and request.data['status'] == 'confirmed':
                # Send confirmation notification
                self.send_confirmation(updated_booking)
            
            return Response(serializer.data)
        
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        booking = self.get_object(pk)
        
        if booking.student != request.user:
            return Response({"error": "Only the student can cancel bookings"}, status=403)
        
        if booking.status == 'cancelled':
            return Response({"error": "Booking is already cancelled"}, status=400)
        
        booking.status = 'cancelled'
        booking.save()
        
        # Release the time slot
        booking.availability.is_booked = False
        booking.availability.save()
        
        # Refund payment if already paid
        if hasattr(booking, 'payment') and booking.payment.status == 'succeeded':
            self.process_refund(booking.payment)
        
        return Response({"message": "Booking cancelled successfully"})

    def process_refund(self, payment):
        try:
            refund = stripe.Refund.create(
                payment_intent=payment.payment_intent_id,
                reason='requested_by_customer'
            )
            payment.status = 'refunded'
            payment.save()
        except Exception as e:
            # Log error but don't fail the cancellation
            print(f"Refund failed: {str(e)}")

class WebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        except stripe.error.SignatureVerificationError as e:
            return Response({"error": str(e)}, status=400)

        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            self.handle_payment_succeeded(payment_intent)

        return Response({"success": True})

    def handle_payment_succeeded(self, payment_intent):
        try:
            payment = Payment.objects.get(payment_intent_id=payment_intent['id'])
            payment.status = 'succeeded'
            payment.paid_at = timezone.now()
            payment.save()
            
            booking = payment.booking
            booking.status = 'confirmed'
            booking.save()
            
            # Send confirmation emails
            self.send_booking_confirmation(booking)
            
        except Payment.DoesNotExist:
            pass

    def send_booking_confirmation(self, booking):
        # Implement email sending logic
        pass