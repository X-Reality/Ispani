from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import (
    CustomUser, OTP, Registration, Group, Message,
    SubjectSpecialization, TutorProfile, TutoringSession, Booking
)
from .serializers import (
    CustomUserSerializer, RegistrationSerializer, 
    GroupSerializer, MessageSerializer, SubjectSpecializationSerializer, LoginSerializer, OTPSerializer,
    TutorProfileSerializer, TutoringSessionSerializer, BookingSerializer, SignupSerializer,
)
from django.contrib.auth import authenticate
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from .utils import generate_otp, verify_otp  # Assuming you have a verify_otp function in utils

# CustomUser Views
class CustomUserViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    

class OTPViewSet(viewsets.ModelViewSet):
    queryset = OTP.objects.all()
    serializer_class = OTPSerializer
    permission_classes = [IsAuthenticated]

# Registration Views
class RegistrationViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = RegistrationSerializer

    def get_permissions(self):
        if self.action in ['create']:  # Allow registration
            return [AllowAny()]
        return [IsAuthenticated()]


# Group Views
class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]

# Message Views
class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

# SubjectSpecialization Views
class SubjectSpecializationViewSet(viewsets.ModelViewSet):
    queryset = SubjectSpecialization.objects.all()
    serializer_class = SubjectSpecializationSerializer
    permission_classes = [IsAuthenticated]

# TutorProfile Views
class TutorProfileViewSet(viewsets.ModelViewSet):
    queryset = TutorProfile.objects.all()
    serializer_class = TutorProfileSerializer
    permission_classes = [IsAuthenticated]

# TutoringSession Views
class TutoringSessionViewSet(viewsets.ModelViewSet):
    queryset = TutoringSession.objects.all()
    serializer_class = TutoringSessionSerializer
    permission_classes = [IsAuthenticated]

# Booking Views
class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

# Signup View
class SignUpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        # Generate and send OTP to the email
        otp = generate_otp(email)
        
        if otp:
            return Response({'message': 'OTP sent to your email, please verify it.'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Error generating OTP, please try again.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerifyOTPView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        otp = request.data.get('otp')
        email = request.data.get('email')
        
        if not otp or not email:
            return Response({'message': 'OTP and email are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if OTP is valid
        is_valid_otp = verify_otp(email, otp)
        
        if is_valid_otp:
            # If OTP is valid, create user
            password = request.data.get('password')
            user = CustomUser.objects.create_user(
                username=email,
                email=email,
                password=password,
                is_active=True
            )
            return Response({'message': 'User created successfully!'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'Invalid OTP, please try again.'}, status=status.HTTP_400_BAD_REQUEST)

# Login View
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']

            if not user.is_active:
                return Response({'message': 'Your account is inactive. Please contact support.'}, status=status.HTTP_400_BAD_REQUEST)
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'email': user.email
                },
                'message': 'Login successful'
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Logout View
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
