import string
import uuid
import stripe

from django.contrib.auth import authenticate, login, logout
from django.core.cache import cache
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.conf import settings

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from ..models import CustomUser, StudentProfile, TutorProfile, HStudents, ServiceProvider
from ..serializers import UserSerializer, UserRegistrationSerializer

# ------------------- User Registration and Authentication -------------------
stripe.api_key = settings.STRIPE_SECRET_KEY

class SignUpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        username = request.data.get("username")

        
        # Check if auth_type is provided for social auth
        auth_type = request.data.get("auth_type", "email")  # Default to email auth
        
        # For regular email signup
        if auth_type == "email":
            # Validate required fields
            if not email or not password or not username:
                return Response({"error": "Email, password and usernameare required"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate password confirmation
           # if password != confirm_password:
                return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate email uniqueness
            if CustomUser.objects.filter(email=email).exists():
                return Response({"error": "Email already in use"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Generate and send OTP
            otp = get_random_string(6, allowed_chars=string.digits)
            cache.set(email, {'otp': otp, 'password': password}, timeout=300)
            
            send_mail(
                "Your OTP Code",
                f"Your OTP code is {otp}. It expires in 5 minutes.",
                "noreply@example.com",
                [email],
                fail_silently=False,
            )
            
            return Response({"message": "OTP sent to email"}, status=status.HTTP_200_OK)
        
        # For social authentication
        elif auth_type in ["google", "facebook", "instagram"]:
            # Handle social auth token validation
            social_token = request.data.get("social_token")
            
            if not social_token:
                return Response({"error": "Social authentication token is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Here you would validate the social token with the respective provider
            # This is a placeholder for the actual social auth logic
            try:
                # Your social auth validation logic would go here
                # For now, we'll just check if email exists
                if CustomUser.objects.filter(email=email).exists():
                    # For social auth, you might want to just log the user in
                    # if their email already exists
                    user = CustomUser.objects.get(email=email)
                    refresh = RefreshToken.for_user(user)
                    
                    return Response({
                        "message": "Social login successful",
                        "user": UserSerializer(user).data,
                        "token": {
                            "refresh": str(refresh),
                            "access": str(refresh.access_token),
                        }
                    }, status=status.HTTP_200_OK)
                else:
                    # Create a temp token for completing registration
                    temp_token = str(uuid.uuid4())
                    # For social auth, we don't need to store a password
                    cache.set(temp_token, {
                        'email': email,

                        'auth_type': auth_type
                    }, timeout=600)
                    
                    return Response({
                        "message": "Please complete your registration",
                        "temp_token": temp_token
                    }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": f"Social authentication failed: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Invalid authentication type"}, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        username= request.data.get("username")
        otp = request.data.get("otp")

        cached_data = cache.get(email)
        if not cached_data or cached_data.get('otp') != otp:
            return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)

        temp_token = str(uuid.uuid4())
        cache.set(temp_token, {
            'email': email,
            'username': username,
        }, timeout=600)

        cache.delete(email)

        return Response({
            "message": "OTP verified.",
            "temp_token": temp_token,
        }, status=status.HTTP_200_OK)

class CompleteRegistrationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        temp_token = request.data.get("temp_token")
        temp_data = cache.get(temp_token)
        data = request.data
        role = data.get('role')
        user = request.user

        if not user or not user.pk:
            user = CustomUser.objects.create_user(
            email=temp_data['email'],
            username=temp_data.get('username', temp_data['email'].split('@')[0]),
            password=temp_data.get('password') or CustomUser.objects.make_random_password()
    )
        if not temp_data:
            return Response({"error": "Invalid or expired session."}, status=status.HTTP_400_BAD_REQUEST)
        
        auth_type = temp_data.get('auth_type', 'email')

        if not role:
            return Response({
                'message': 'Role is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update user role
        user.role = role
        user.save()
        
        try:
            if role == 'student':
                StudentProfile.objects.create(
                    user=user,
                    year_of_study=data.get('year_of_study'),
                    course=data.get('course'),
                    hobbies=data.get('hobbies'),
                    qualification=data.get('qualification'),
                    institution=data.get('institution')
                )
            elif role == 'tutor':
                TutorProfile.objects.create(
                    user=user,
                    about=data.get('about'),
                    phone_number=data.get('phone_number'),
                    hourly_rate=data.get('hourly_rate'),
                    qualifications=data.get('qualifications')
                )
            elif role == 'hs student':
                HStudents.objects.create(
                    user=user
                )
            elif role == 'service provider':
                ServiceProvider.objects.create(
                    user=user,
                    company_name=data.get('company_name'),
                    description=data.get('description'),
                    typeofservice=data.get('typeofservice'),
                    qualification=data.get('qualification'),
                    interests=data.get('interests'),
                    hobbies=data.get('hobbies')
                )
            # Add other role-specific profiles as needed
            
            return Response({
                'message': 'Profile completed successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'message': f'Error completing profile: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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