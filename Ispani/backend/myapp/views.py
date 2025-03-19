import string
import random
import uuid
from django.contrib.auth import authenticate, login, logout
from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status, generics
from rest_framework.decorators import api_view,permission_classes
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import StudentProfile, Group, Message
from .serializers import StudentProfileSerializer, GroupSerializer, MessageSerializer, JoinGroupSerializer,PrivateMessageSerializer
from django.core.cache import cache
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
import logging

logger = logging.getLogger(__name__)

class StudentProfileListCreate(generics.ListCreateAPIView):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer
    permission_classes = [AllowAny]


class SignUpView(APIView):
    permission_classes = [AllowAny]


    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if StudentProfile.objects.filter(email=email).exists():
            return Response({"error": "Email already in use"}, status=status.HTTP_400_BAD_REQUEST)

        otp = get_random_string(6, allowed_chars=string.digits)
        cache.set(email, otp, timeout=300)  # Store OTP for 5 minutes

        send_mail(
            "Your OTP Code",
            f"Your OTP code is {otp}. It expires in 5 minutes.",
            "noreply@example.com",  # Change to your sender email
            [email],
            fail_silently=False,
        )
        
        return Response({"message": "OTP sent to email"}, status=status.HTTP_200_OK)
    
class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")
        password = request.data.get("password")
        
        stored_otp = cache.get(email)
        if stored_otp and stored_otp == otp:
            cache.delete(email)  # Remove OTP after successful verification
            temp_token = str(uuid.uuid4())  # Generate a temporary token
            cache.set(temp_token, email, timeout=600) 
            cache.set(f"{temp_token}_password", password, timeout=600)  

            return Response({
                "message": "OTP verified.",
                "temp_token": temp_token  # Ensure temp_token is returned
            }, status=status.HTTP_200_OK)
        
        return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)
    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Optionally, you can add token invalidation logic here
        return Response({"message": "Logout successful. Please delete the token on the client side."})
    

class UserDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        user = request.user
        student_profile = StudentProfile.objects.get(user=user)
        serializer = StudentProfileSerializer(student_profile)
        return Response(serializer.data)


class GroupListCreate(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class SendPrivateMessageView(generics.CreateAPIView):
    serializer_class = PrivateMessageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

# views.py
class PrivateMessageListView(generics.ListAPIView):
    serializer_class = PrivateMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(recipient=user).order_by('-timestamp')

class MessageListCreate(generics.ListCreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        group = serializer.validated_data['group']
        user = self.request.user  # Directly use request.user (StudentProfile)

        # Ensure the user is a member of the group
        if not group.members.filter(id=user.id).exists():
            raise ValidationError("You are not a member of this group and cannot send messages here.")

        # Automatically set the sender to the currently logged-in user
        serializer.save(sender=user)

@api_view(['POST'])
def join_group(request):
    permission_classes = [AllowAny]

    serializer = JoinGroupSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()  # Add student to group
        return Response({"message": "You have successfully joined the group."}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CompleteRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        temp_token = request.data.get("temp_token")
        email = cache.get(temp_token)  # Retrieve email linked to temp_token
        logger.debug(f"Temp token: {temp_token}, Email: {email}")

        if not email:
            logger.error("Invalid or expired session.")
            return Response({"error": "Invalid or expired session."}, status=status.HTTP_400_BAD_REQUEST)

        password = cache.get(f"{temp_token}_password")
        logger.debug(f"Password for temp token: {password}")

        if not password:
            logger.error("Session data missing or expired.")
            return Response({"error": "Session data missing or expired."}, status=status.HTTP_400_BAD_REQUEST)

        username = request.data.get("username")
        year_of_study = request.data.get("year_of_study")
        course = request.data.get("course")
        hobbies = request.data.get("hobbies")
        piece_jobs = request.data.get("piece_jobs")
        communication_preference=request.data.get('communication_preference')

        if not StudentProfile.objects.filter(email=email).exists():
            user = StudentProfile.objects.create_user(
                username=username,
                email=email,  
                password=password, 
                year_of_study=year_of_study,
                course=course,
                hobbies=hobbies,
                piece_jobs=piece_jobs,
                communication_preference=communication_preference
            )
            user.is_active = True
            user.save()
            cache.delete(temp_token)  # Remove temp_token after use

            authenticated_user = authenticate(username=username, password=password)
            if authenticated_user is not None:
                login(request, authenticated_user)
                
                # Generate token for JWT authentication
                refresh = RefreshToken.for_user(authenticated_user)
                
                return Response({
                    "message": "Registration completed successfully",
                    "user": {
                        "username": authenticated_user.username,
                        "email": authenticated_user.email,
                    },
                    "token": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    }
                }, status=status.HTTP_201_CREATED)
            else:
                # This should rarely happen since we just created the user
                logger.error(f"Failed to authenticate newly created user: {username}")
                return Response({"message": "Registration completed successfully, but auto-login failed. Please log in manually."}, 
                               status=status.HTTP_201_CREATED)
        
        return Response({"error": "Email is already registered."}, status=status.HTTP_400_BAD_REQUEST)



class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        logger.debug(f"Login attempt with email: {email}")  # Better to use logger than print

        if not email or not password:
            return Response({"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Find the user by email first
            student = StudentProfile.objects.get(email=email)
            # Then authenticate with the correct credentials
            user = authenticate(username=student.username, password=password)
            
            if user is not None and user.is_active:
                login(request, user)
                logger.debug(f"User logged in: {user}")
                
                # Generate token for JWT authentication
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    "message": "Login successful",
                    "user": {
                        "username": user.username,
                        "email": user.email,
                    },
                    "token": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    }
                }, status=status.HTTP_200_OK)
            else:
                logger.debug("Authentication failed")
                return Response({"error": "Invalid credentials or user is not active"}, status=status.HTTP_401_UNAUTHORIZED)
                
        except StudentProfile.DoesNotExist:
            logger.warning(f"Login attempt with non-existent email: {email}")
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        
        
@api_view(['GET'])
def study_groups(request):
    """
    Returns only study-related groups.
    """
    # Filter groups that have both `field_of_study` and `year_of_study` set.
    study_groups = Group.objects.filter(course__isnull=False, year_of_study__isnull=False)
    serializer = GroupSerializer(study_groups, many=True)
    
    return Response(serializer.data)

@api_view(['GET'])
def hobby_groups(request):
    """
    Returns only interest-related groups.
    """
    # Filter groups that have `field_of_study` and `year_of_study` set to None.
    hobby_groups = Group.objects.filter(course__isnull=True, year_of_study__isnull=True)
    serializer = GroupSerializer(hobby_groups, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def group_messages(request, group_id):
    """
    Get all messages for a specific group.
    """
    group = get_object_or_404(Group, id=group_id)
    
    # Check if the user is a member of the group
    if not group.members.filter(id=request.user.id).exists():
        return Response(
            {"error": "You are not a member of this group"}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get the messages for the group, ordered by timestamp
    messages = Message.objects.filter(group=group).order_by('timestamp')
    serializer = MessageSerializer(messages, many=True, context={'request': request})
    
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def group_detail(request, group_id):
    """
    Get detailed information about a specific group.
    """
    group = get_object_or_404(Group, id=group_id)
    
    # Check if the user is a member of the group
    is_member = group.members.filter(id=request.user.id).exists()
    
    serializer = GroupSerializer(group, context={'request': request})
    
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def leave_group(request):
    """
    Leave a group.
    """
    group_id = request.data.get('group_id')
    if not group_id:
        return Response({"error": "group_id is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    group = get_object_or_404(Group, id=group_id)
    
    # Check if the user is a member of the group
    if not group.members.filter(id=request.user.id).exists():
        return Response(
            {"error": "You are not a member of this group"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Remove the user from the group
    group.members.remove(request.user)
    
    return Response({"message": "You have left the group"}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_messages_read(request):
    """
    Mark all messages in a group as read.
    This is a placeholder - you'll need to implement your own read/unread tracking.
    """
    group_id = request.data.get('group_id')
    if not group_id:
        return Response({"error": "group_id is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    group = get_object_or_404(Group, id=group_id)
    
    # Check if the user is a member of the group
    if not group.members.filter(id=request.user.id).exists():
        return Response(
            {"error": "You are not a member of this group"}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Implement read/unread tracking here
    # This is a placeholder - you'll need to create a model to track read/unread status
    
    return Response({"message": "Messages marked as read"}, status=status.HTTP_200_OK)
