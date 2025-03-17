import email
from rest_framework import viewsets, status
from rest_framework.views import APIView

from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser 
from rest_framework.decorators import action
from .utils import generate_otp
from django.contrib.auth import authenticate,login,logout
from django.db import transaction
from .models import (
    CustomUser , OTP, Registration, Group, Message,
    SubjectSpecialization, TutorProfile, TutoringSession, Booking,
    Hobby, PieceJob, DirectMessage
)
from .serializers import (
    CustomUserSerializer, RegistrationSerializer, 
    GroupSerializer, MessageSerializer, SubjectSpecializationSerializer, OTPSerializer, TutorProfileSerializer, 
    TutoringSessionSerializer, BookingSerializer,
    HobbySerializer, PieceJobSerializer, generate_otp,
    add_user_to_qualification_group, add_user_to_year_group,
    add_user_to_hobby_group, add_user_to_piecejob_group, DirectMessageSerializer
)


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser .objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can access this view

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]  # Allow any authenticated user to view
        return super().get_permissions()
    
class SignUpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

           
        otp = generate_otp(email)  # This function should create an OTP and send it via email

        if otp:
            return Response({'message': 'OTP sent to your email, please verify it.'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Error generating OTP, please try again.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

               

            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        return Response({"detail": "This endpoint only supports POST requests to register a new user."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    


    
class OTPViewSet(viewsets.ModelViewSet):
    queryset = OTP.objects.all()
    serializer_class = OTPSerializer
    permission_classes = [AllowAny]  # Allow any user to access OTP endpoints

    def create(self, request, *args, **kwargs):
        # Custom logic for creating an OTP can be added here
        return super().create(request, *args, **kwargs)

# User Registration View
class RegistrationView(APIView):
    permission_classes = [AllowAny]  # Ensure the user is authenticated

    def post(self, request):
        # Get the user's email and password from the request data   
        
        print(f"User authenticated: {request.user.is_authenticated}")
        print(f"User: {request.user.username}")

        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            # Pass the authenticated user to the serializer
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# User Login View
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return Response({"message": "Login successful", "role": user.role})
        return Response({"error": "Invalid credentials"}, status=400)
   

# User Logout View
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Implement logout logic if needed (e.g., token blacklisting)
        logout(request)
        return Response({"message": "Logged out successfully"}, status=200)
    
class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = CustomUserSerializer(user)
        return Response(serializer.data)
    

# OTP Verification View
class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        otp = request.data.get('otp')
        email = request.data.get('email')
        password = request.data.get('password')

        if not otp or not email or not password:
            return Response({
                'message': 'OTP, email, and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if OTP is valid
        otp_instance = OTP.objects.filter(email=email, code=otp).first()
        
        if not otp_instance:
            return Response({
                'message': 'Invalid OTP.'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        if otp_instance.is_expired():
            return Response({
                'message': 'OTP has expired.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create the user after OTP verification
        user = CustomUser.objects.create_user(
            username=email,  # Use email as username
            email=email,
            password=password,
            is_active=True
        )
        
        # Automatically log in the user
        login(request, user)
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        tokens = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        
        # Delete the used OTP
        otp_instance.delete()
        
        return Response({
            'message': 'User registered and logged in successfully!',
            'user_id': user.id,
            'tokens': tokens
        }, status=status.HTTP_201_CREATED)
# Group ViewSet
class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser ()]  # Only admins can create/update/delete groups
        return [AllowAny()]  # Any authenticated user can view groups

    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """Add a user to a group (admin function)"""
        group = self.get_object()
        user_id = request.data.get('user_id')

        if not user_id:
            return Response({'error': 'User  ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser .objects.get(pk=user_id)
            group.members.add(user)
            return Response({'message': f'User  {user.username} added to group {group.name}'}, status=status.HTTP_200_OK)
        except CustomUser .DoesNotExist:
            return Response({'error': 'User  not found'}, status=status.HTTP_404_NOT_FOUND)

# Message ViewSet
class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        # Set the sender to the current user
        request.data['sender'] = request.user.id
        return super().create(request, *args, **kwargs)

# Direct Message ViewSet
class DirectMessageViewSet(viewsets.ModelViewSet):
    queryset = DirectMessage.objects.all()
    serializer_class = DirectMessageSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Set the sender to the current user
        request.data['sender'] = request.user.id
        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread messages for current user"""
        count = DirectMessage.objects.filter(recipient=request.user, read=False).count()
        return Response({'unread_count': count})

# Additional ViewSets for other models can be added similarly...
class SubjectSpecializationViewSet(viewsets.ModelViewSet):
    queryset = SubjectSpecialization.objects.all()
    serializer_class = SubjectSpecializationSerializer
    permission_classes = [AllowAny]

class TutorProfileViewSet(viewsets.ModelViewSet):
    queryset = TutorProfile.objects.all()
    serializer_class = TutorProfileSerializer
    permission_classes = [AllowAny] 

class TutoringSessionViewSet(viewsets.ModelViewSet):
    queryset = TutoringSession.objects.all()
    serializer_class = TutoringSessionSerializer
    permission_classes = [IsAuthenticated] 

class BookingViewSet(viewsets.ModelViewSet):
    queryset = TutoringSession.objects.all()
    serializer_class = TutoringSessionSerializer
    permission_classes = [IsAuthenticated] 

class HobbyViewSet(viewsets.ModelViewSet):
    queryset = Hobby.objects.all()
    serializer_class = HobbySerializer
    permission_classes = [AllowAny] 

class PieceJobViewSet(viewsets.ModelViewSet):
    queryset = PieceJob.objects.all()
    serializer_class = PieceJobSerializer
    permission_classes = [AllowAny]