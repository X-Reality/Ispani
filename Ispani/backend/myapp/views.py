from django.contrib.auth import authenticate, login, logout
from django.forms import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status, generics
from rest_framework.decorators import api_view
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from .models import StudentProfile, Group, Message, TutorProfile, TutoringSession, Booking, SubjectSpecialization, Interest
from .serializers import StudentProfileSerializer, GroupSerializer, MessageSerializer, JoinGroupSerializer, TutoringSessionSerializer, TutorProfileSerializer, BookingSerializer, TutorSignupSerializer, InterestSerializer
import logging
from rest_framework.exceptions import PermissionDenied

logger = logging.getLogger(__name__)

class StudentProfileListCreate(generics.ListCreateAPIView):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer
    permission_classes = [AllowAny]

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import StudentProfile, Interest
from .serializers import StudentProfileSerializer
from django.contrib.auth import get_user_model

class SignUpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Get the data for creating a new user (sign-up)
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        first_name = request.data.get('first_name')
        interests = request.data.get('interests', [])  # List of interest IDs or names
        
        # Check if the username already exists
        if StudentProfile.objects.filter(username=username).exists():
            return Response({"detail": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)

        # Create the new student user (StudentProfile) using the information
        user = StudentProfile.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
        )
        user.save()

        # If the user provided interests, associate them with the user
        if interests:
            user_interests = Interest.objects.filter(name__in=interests)
            user.interests.set(user_interests)

        return Response({"message": "Signup successful", "user_id": user.id}, status=status.HTTP_201_CREATED)

        # Generate JWT tokens for the new user
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user_id': user.id,
            'username': user.username
        }, status=status.HTTP_201_CREATED)

class InterestView(APIView):
    permission_classes = [IsAuthenticated]  # Or AllowAny if you want everyone to access the interests

    def get(self, request):
        # Retrieve all interests (both predefined and custom)
        interests = Interest.objects.all()
        serializer = InterestSerializer(interests, many=True)
        return Response({"interests": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        # Extracting custom interests from the request
        other_interests = request.data.get('other_interests', [])  # List of custom interests
        
        # Handle custom interests (add them if they don't exist)
        for interest_name in other_interests:
            interest_name = interest_name.strip().lower()  # Normalize interest name
            
            # Check if the interest already exists
            existing_interest = Interest.objects.filter(name__iexact=interest_name).first()

            if not existing_interest:
                # If the interest doesn't exist, create a new one
                Interest.objects.create(name=interest_name, is_custom=True)

        return Response({"detail": "Interests updated successfully"}, status=status.HTTP_200_OK)

class UpdateUserInterestsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Get the current user
        user = request.user
        
        # Extract the interest IDs (both predefined and custom interests)
        selected_interests = request.data.get('interests', [])

        # Convert interest names/IDs to actual Interest objects
        interests = Interest.objects.filter(name__in=selected_interests)

        # Update the user's interests
        user.profile.interests.set(interests)

        return Response({"detail": "Interests updated successfully"}, status=status.HTTP_200_OK)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Optionally, you can add token invalidation logic here
        return Response({"message": "Logout successful. Please delete the token on the client side."})
    

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        student_profile = StudentProfile.objects.get(user=user)
        serializer = StudentProfileSerializer(student_profile)
        return Response(serializer.data)


class GroupListCreate(generics.ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class MessageListCreate(generics.ListCreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

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
    serializer = JoinGroupSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()  # Add student to group
        return Response({"message": "You have successfully joined the group."}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({"error": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Authenticate the user
        user = authenticate(username=username, password=password)

        if user is not None and user.is_active:
            login(request, user)
            # Directly access the role field from the authenticated user (StudentProfile)
            return Response({"message": "Login successful", "role": user.role})
        else:
            return Response({"error": "Invalid credentials or user is not active"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def study_groups(request):
    """
    Returns only study-related groups.
    """
    # Filter groups that have both `field_of_study` and `year_of_study` set.
    study_groups = Group.objects.filter(field_of_study__isnull=False, year_of_study__isnull=False)
    serializer = GroupSerializer(study_groups, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def interest_groups(request):
    """
    Returns only interest-related groups.
    """
    # Filter groups that have `field_of_study` and `year_of_study` set to None.
    interest_groups = Group.objects.filter(field_of_study__isnull=True, year_of_study__isnull=True)
    serializer = GroupSerializer(interest_groups, many=True)
    return Response(serializer.data)

class TutorSignupView(APIView):
    def post(self, request):
        serializer = TutorSignupSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # Create the tutor profile
            tutor_profile = serializer.save()
            return Response({
                "message": "Tutor registration successful",
                "data": {
                    "available_times": tutor_profile.available_times,
                    "subjects": [subject.name for subject in tutor_profile.subjects.all()]
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TutorSessionCreateView(APIView):
    def post(self, request, *args, **kwargs):
        tutor_profile = request.user.tutor_profile  # Assuming user is a StudentProfile with TutorProfile

        # Check if the tutor is approved
        if not tutor_profile.is_approved:
            raise PermissionDenied("Your tutor profile is awaiting admin approval.")

# View for listing available tutors
class AvailableTutorsView(generics.ListAPIView):
    queryset = TutorProfile.objects.all()
    serializer_class = TutorProfileSerializer
    permission_classes = [IsAuthenticated]

# View for booking a tutor
class BookTutorView(generics.CreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

# View for viewing all booked sessions
class StudentSessionsView(generics.ListAPIView):
    queryset = TutoringSession.objects.all()
    serializer_class = TutoringSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(student=self.request.user)
