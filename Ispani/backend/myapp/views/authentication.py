from django.core.cache import cache
import string
import uuid
import stripe

from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.conf import settings

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

from myapp.utils import create_temp_jwt

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
                    temp_token = create_temp_jwt({
                        'email': email,
                        'auth_type': auth_type
                    })

                    
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

        temp_token = create_temp_jwt({
            'email': email,
            'username': username,
            'auth_type': 'email'
        })


        cache.delete(email)

        return Response({
            "message": "OTP verified.",
            "temp_token": temp_token,
        }, status=status.HTTP_200_OK)

class CompleteRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print("Incoming data:", request.data)  
        
        temp_token = request.data.get("temp_token")
        print("Temp token received:", temp_token)
        
        if not temp_token:
            return Response({"error": "Missing registration token"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Parse token
            token = UntypedToken(temp_token)
            token_payload = token.payload
            
            # Debug token payload
            print("Token payload:", token_payload)
            
            # Get required fields
            email = token_payload.get('email')
            username = token_payload.get('username')
            
            if not email or not username:
                return Response({"error": "Invalid token: missing required fields"}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            # Get user if exists or create a new one
            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                # Create a new user if they don't exist
                user = CustomUser.objects.create_user(
                    email=email,
                    username=username,
                    password=token_payload.get('password') or CustomUser.objects.make_random_password()
                )
            
            # Get role and other required data
            role = request.data.get('role')
            if not role:
                return Response({"error": "Role is required"}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            # Update user role
            user.role = role
            user.save()
            
            # Process profile specific data
            if role == 'student':
                StudentProfile.objects.create(
                    user=user,
                    city=request.data.get('city'),
                    year_of_study=request.data.get('year_of_study'),
                    course=request.data.get('course'),
                    hobbies=request.data.get('hobbies'),
                    qualification=request.data.get('qualification'),
                    institution=request.data.get('institution')
                )
            elif role == 'tutor':
                TutorProfile.objects.create(
                    user=user,
                    city=request.data.get('city'),
                    about=request.data.get('about'),
                    phone_number=request.data.get('phone_number'),
                    hourly_rate=request.data.get('hourly_rate'),
                    qualification=request.data.get('qualification')
                )
            elif role == 'hs student':
                HStudents.objects.create(
                    user=user
                )
            elif role == 'service provider':
                ServiceProvider.objects.create(
                    user=user,
                    city=request.data.get('city'),
                    company_name=request.data.get('company_name'),
                    description=request.data.get('description'),
                    typeofservice=request.data.get('typeofservice'),
                    qualification=request.data.get('qualification'),
                    interests=request.data.get('interests'),
                    hobbies=request.data.get('hobbies')
                )
            
            # Generate authentication tokens for immediate login
            refresh = RefreshToken.for_user(user)
            
            return Response({
                "message": "Profile completed successfully",
                "user": UserSerializer(user).data,
                "token": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }
            }, status=status.HTTP_200_OK)
                
        except (TokenError, InvalidToken) as e:
            return Response({"error": f"Invalid token: {str(e)}"}, 
                         status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Registration error: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({"error": f"Registration error: {str(e)}"}, 
                         status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
