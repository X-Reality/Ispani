from django.core.cache import cache
import uuid
import stripe

from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from myapp.utils import create_temp_jwt

from ..models import CustomUser, StudentProfile, TutorProfile, HStudents, ServiceProvider
from ..serializers import UserSerializer, UserRegistrationSerializer

stripe.api_key = settings.STRIPE_SECRET_KEY

class SignUpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        username = request.data.get("username")

        if not email or not password or not username:
            return Response({"error": "Email, password and username are required"}, status=status.HTTP_400_BAD_REQUEST)

        if CustomUser.objects.filter(email=email).exists():
            return Response({"error": "Email already in use"}, status=status.HTTP_400_BAD_REQUEST)

        otp = str(uuid.uuid4().int)[:6]  # Just a dummy OTP logic, replace with proper OTP generator
        cache.set(email, {"otp": otp, "password": password, "username": username}, timeout=3600)

        # Here you would send the OTP via email
        send_mail(
            subject="Your OTP Code",
            message=f"Use this OTP to continue your registration: {otp}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        return Response({"message": "OTP sent to email"}, status=status.HTTP_200_OK)

class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        username = request.data.get("username")
        # otp = request.data.get("otp")  # Omitted for now

        temp_token = str(uuid.uuid4())

        cache.set(f"reg_{temp_token}", {
            'email': email,
            'username': username,
            'auth_type': 'email'
        }, timeout=3600)

        return Response({
            "message": "Ready to complete registration",
            "temp_token": temp_token,
        }, status=status.HTTP_200_OK)

class CompleteRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            print("Incoming data:", request.data)

            temp_token = request.data.get("temp_token")
            if not temp_token:
                return Response({"error": "Missing registration token"}, status=status.HTTP_400_BAD_REQUEST)

            temp_data = cache.get(f"reg_{temp_token}")
            if not temp_data:
                return Response({"error": "Invalid or expired registration token"}, status=status.HTTP_400_BAD_REQUEST)

            email = temp_data['email']
            username = temp_data['username']
            password = request.data.get('password') or temp_data.get('password')

            if CustomUser.objects.filter(email=email).exists():
                user = CustomUser.objects.get(email=email)
            else:
                user = CustomUser.objects.create_user(email=email, username=username, password=password)

            # Get roles as a list (could be multiple roles selected)
            roles = request.data.get("roles", [])
            if not roles:
                return Response({"error": "Missing roles"}, status=status.HTTP_400_BAD_REQUEST)

            valid_roles = ['student', 'tutor', 'hs student', 'service provider']
            invalid_roles = [role for role in roles if role not in valid_roles]
            
            if invalid_roles:
                return Response({"error": f"Invalid roles: {', '.join(invalid_roles)}"}, status=status.HTTP_400_BAD_REQUEST)

            # Assign roles to the user (store multiple roles)
            user.role = roles  # Assign multiple roles to the user (store as list)
            user.save()

            # Create profiles based on the selected roles
            for role in roles:
                if role == 'student':
                    StudentProfile.objects.create(
                        user=user,
                        city=request.data.get('city', ''),
                        year_of_study=request.data.get('year_of_study'),
                        course=request.data.get('course', ''),
                        hobbies=request.data.get('hobbies', []),
                        qualification=request.data.get('qualification', ''),
                        institution=request.data.get('institution', '')
                    )
                elif role == 'tutor':
                    TutorProfile.objects.create(
                        user=user,
                        about=request.data.get('about', ''),
                        phone_number=request.data.get('phone_number', ''),
                        hourly_rate=request.data.get('hourly_rate', 0),
                        qualification=request.data.get('qualification', '')
                    )
                elif role == 'hs student':
                    HStudents.objects.create(user=user)
                elif role == 'service provider':
                    ServiceProvider.objects.create(
                        user=user,
                        company_name=request.data.get('company_name', ''),
                        description=request.data.get('description', ''),
                        typeofservice=request.data.get('typeofservice', ''),
                        qualification=request.data.get('qualification', ''),
                        interests=request.data.get('interests', []),
                        hobbies=request.data.get('hobbies', [])
                    )

            refresh = RefreshToken.for_user(user)
            cache.delete(f"reg_{temp_token}")

            return Response({
                "message": "Profile completed successfully",
                "user": UserSerializer(user).data,
                "token": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({"error": f"Registration error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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

                return Response({
                    "message": "Login successful",
                    "user": UserSerializer(authenticated_user).data,
                    "token": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    }
                }, status=status.HTTP_200_OK)

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
