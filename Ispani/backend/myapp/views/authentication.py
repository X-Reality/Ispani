import string
import uuid
import logging
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

from ..models import CustomUser
from ..serializers import UserSerializer, UserRegistrationSerializer

# ------------------- User Registration and Authentication -------------------
stripe.api_key = settings.STRIPE_SECRET_KEY

class SignUpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        confirm_password = request.data.get("confirm_password")
        role = request.data.get("role", "student")
        
        # Check if auth_type is provided for social auth
        auth_type = request.data.get("auth_type", "email")  # Default to email auth
        
        # For regular email signup
        if auth_type == "email":
            # Validate required fields
            if not email or not password or not confirm_password:
                return Response({"error": "Email, password, and password confirmation are required"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate password confirmation
            if password != confirm_password:
                return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate email uniqueness
            if CustomUser.objects.filter(email=email).exists():
                return Response({"error": "Email already in use"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Generate and send OTP
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
                        'role': role,
                        'auth_type': auth_type
                    }, timeout=600)
                    
                    return Response({
                        "message": "Please complete your registration",
                        "temp_token": temp_token,
                        "role": role
                    }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": f"Social authentication failed: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Invalid authentication type"}, status=status.HTTP_400_BAD_REQUEST)

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
        
        auth_type = temp_data.get('auth_type', 'email')

        registration_data = {
            'username': request.data.get("username"),
            'email': temp_data['email'],
            'role': temp_data['role']
        }

        # Only set password for email registration
        if auth_type == 'email':
            registration_data['password'] = temp_data['password']
        else:
            # For social auth, generate a secure random password
            # The user won't need this password as they'll login via social auth
            registration_data['password'] = get_random_string(20)

        if temp_data['role'] == 'student':
            registration_data['student_profile'] = {
                'year_of_study': request.data.get("year_of_study"),
                'course': request.data.get("course"),
                'hobbies': request.data.get("hobbies"),
                'piece_jobs': request.data.get("piece_jobs"),
                'institution': request.data.get("institution")
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

            # For social auth, we don't need to authenticate with password
            if auth_type == 'email':
                authenticated_user = authenticate(username=user.username, password=temp_data['password'])
            else:
                # For social auth, we can just use the user object directly
                authenticated_user = user

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