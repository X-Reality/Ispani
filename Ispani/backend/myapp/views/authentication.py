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