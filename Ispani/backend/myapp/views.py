from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status, generics
from rest_framework.decorators import api_view
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from .models import StudentProfile, Group, Message
from .serializers import StudentProfileSerializer, GroupSerializer, MessageSerializer, JoinGroupSerializer
import logging

logger = logging.getLogger(__name__)

class StudentProfileListCreate(generics.ListCreateAPIView):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer
    permission_classes = [AllowAny]


class SignUpView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        # Extracting data from request
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        name = request.data.get('name')
        role = request.data.get('role', 'student') 
        year_of_study = request.data.get('year_of_study')
        field_of_study = request.data.get('field_of_study')
        interests = request.data.get('interests')
        desired_jobs = request.data.get('desired_jobs')

        # Check if the username already exists
        if StudentProfile.objects.filter(username=username).exists():
            return Response({"detail": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)

        # Create the StudentProfile (user)
        user = StudentProfile.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=name,  # Use first_name for the name field
            role=role,
            year_of_study=year_of_study,
            field_of_study=field_of_study,
            interests=interests,
            desired_jobs=desired_jobs
        )
        user.is_active = True
        user.save()

        # Generate JWT tokens for the new user
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user_id': user.id,
            'username': user.username
        }, status=status.HTTP_201_CREATED)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"message": "Logout successful"})
    

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

        print(f"Username: {username}, Password: {password}")  # Debugging

        if not username or not password:
            return Response({"error": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Authenticate the user
        user = authenticate(username=username, password=password)
        print(f"Authenticated User: {user}")  # Debugging

        if user is not None and user.is_active:
            login(request, user)
            print(f"User logged in: {user}")  # Debugging
            # Directly access the role field from the authenticated user (StudentProfile)
            return Response({"message": "Login successful", "role": user.role})
        else:
            print("Authentication failed")  # Debugging
            return Response({"error": "Invalid credentials or user is not active"}, status=status.HTTP_400_BAD_REQUEST)
