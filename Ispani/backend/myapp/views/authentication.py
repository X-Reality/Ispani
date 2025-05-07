from django.core.cache import cache
import uuid
import stripe

from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_decode
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from myapp.utils import assign_user_to_dynamic_group, create_temp_jwt

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

        # Generate a 6-digit OTP
        otp = str(uuid.uuid4().int)[:6]
        
        # Store user registration data and OTP in cache
        cache.set(f"otp_{email}", {
            "otp": otp, 
            "password": password, 
            "username": username
        }, timeout=3600)  # OTP valid for 1 hour

        # Send the OTP via email
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
        otp = request.data.get("otp")
        
        if not email or not otp:
            return Response({"error": "Email and OTP are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Retrieve stored data from cache
        cached_data = cache.get(f"otp_{email}")
        
        if not cached_data:
            return Response({"error": "OTP has expired or email is invalid"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify OTP
        if cached_data["otp"] != otp:
            return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
        
        # OTP verified, generate temp token for registration completion
        temp_token = str(uuid.uuid4())
        
        # Store validated data for registration completion
        cache.set(f"reg_{temp_token}", {
            'email': email,
            'username': cached_data["username"],
            'password': cached_data["password"],
            'auth_type': 'email'
        }, timeout=3600)
        
        # Clear the OTP from cache to prevent reuse
        cache.delete(f"otp_{email}")

        return Response({
            "message": "OTP verified successfully. Ready to complete registration",
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

                city = request.data.get('city', '')
                qualification = request.data.get('qualification', '')
                institution = request.data.get('institution', '')

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
                    assign_user_to_dynamic_group(user, role, city, institution, qualification)

                elif role == 'tutor':
                    TutorProfile.objects.create(
                        user=user,
                        about=request.data.get('about', ''),
                        city=request.data.get('city', ''),
                        phone_number=request.data.get('phone_number', ''),
                        hourly_rate=request.data.get('hourly_rate', 0),
                        qualification=request.data.get('qualification', '')
                    )
                    assign_user_to_dynamic_group(user, role, city)

                elif role == 'hs student':
                    HStudents.objects.create(
                        user=user,
                        schoolName=request.data.get('schoolName', ''),
                        studyLevel=request.data.get('studyLevel', ''),
                        city=request.data.get('city', ''),
                        subjects=request.data.get(' subjects', []),
                        hobbies=request.data.get('hobbies', [])
                    )                        
                    assign_user_to_dynamic_group(user, role, city)

                elif role == 'service provider':
                    ServiceProvider.objects.create(
                        user=user,
                        company=request.data.get('company', ''),
                        about=request.data.get('about', ''),
                        city=request.data.get('city', ''),
                        usageType=request.data.get('typeofservice', ''),
                        sectors =request.data.get('sectors ', []),
                        hobbies=request.data.get('hobbies', []),
                        serviceNeeds=request.data.get('serviceNeeds', [])
                    )
                    assign_user_to_dynamic_group(user, role, city)

                elif role == 'jobseeker':
                    ServiceProvider.objects.create(
                        user=user,
                        cellnumber=request.data.get('cellnumber', ''),
                        status=request.data.get('status',  []),
                        city=request.data.get('city', ''),
                        usage=request.data.get('usage', []),
                        hobbies=request.data.get('hobbies', []),
                    )
                    assign_user_to_dynamic_group(user, role, city)


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

class PasswordResetRequestView(APIView):
    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({'error': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({"message": "If an account with that email exists, we've sent a reset link."}, status=status.HTTP_200_OK)

        # Generate token and uid
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # Build reset link
        reset_link = f"{settings.FRONTEND_RESET_URL}?uid={uid}&token={token}"

        # Send the email
        send_mail(
            subject='Reset your password',
            message=f"Click the link to reset your password: {reset_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        return Response({"message": "If an account with that email exists, we've sent a reset link."}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    def post(self, request):
        uidb64 = request.data.get('uid')
        token = request.data.get('token')
        new_password = request.data.get('new_password')

        if not uidb64 or not token or not new_password:
            return Response({"error": "All fields (uid, token, new_password) are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = CustomUser.objects.get(pk=uid)
        except (CustomUser.DoesNotExist, ValueError, TypeError, OverflowError):
            return Response({"error": "Invalid user ID."}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)
    
class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data) 