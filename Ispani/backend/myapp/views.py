from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.decorators import action
from .models import (
    CustomUser, OTP, Registration, Group, Message,
    SubjectSpecialization, TutorProfile, TutoringSession, Booking,
    Hobby, PieceJob,DirectMessage
)
from .serializers import (
    CustomUserSerializer, RegistrationSerializer, 
    GroupSerializer, MessageSerializer, SubjectSpecializationSerializer, 
    LoginSerializer, OTPSerializer, TutorProfileSerializer, 
    TutoringSessionSerializer, BookingSerializer, SignupSerializer,
    HobbySerializer, PieceJobSerializer, generate_otp,
    add_user_to_qualification_group, add_user_to_year_group,
    add_user_to_hobby_group, add_user_to_piecejob_group,DirectMessageSerializer
)
from django.contrib.auth import authenticate
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction
from django.db.models import Q
from rest_framework.exceptions import ValidationError

# Utility function to verify OTP
def verify_otp(email, otp_code):
    try:
        otp = OTP.objects.get(email=email, code=otp_code)
        if otp.is_expired():
            return False
        return True
    except OTP.DoesNotExist:
        return False

# Hobby Views
class HobbyViewSet(viewsets.ModelViewSet):
    queryset = Hobby.objects.all()
    serializer_class = HobbySerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAdminUser()]  # Only admins can create/update/delete hobbies

# PieceJob Views
class PieceJobViewSet(viewsets.ModelViewSet):
    queryset = PieceJob.objects.all()
    serializer_class = PieceJobSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAdminUser()]  # Only admins can create/update/delete piece jobs

# CustomUser Views
class CustomUserViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    
    @action(detail=True, methods=['get'])
    def groups(self, request, pk=None):
        """Get all groups for a specific user"""
        user = self.get_object()
        groups = user.user_groups.all()
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data)

class OTPViewSet(viewsets.ModelViewSet):
    queryset = OTP.objects.all()
    serializer_class = OTPSerializer
    permission_classes = [IsAuthenticated]

# Registration Views
class RegistrationViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Registration.objects.all()
    serializer_class = RegistrationSerializer

    def get_permissions(self):
        if self.action in ['create']:  # Allow registration
            return [IsAuthenticated()]
        return [IsAuthenticated()]

# Group Views
class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]  # Only admins can create/update/delete groups
        return [IsAuthenticated()]  # Any authenticated user can view groups
    
    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """Add a user to a group"""
        group = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = CustomUser.objects.get(pk=user_id)
            group.members.add(user)
            return Response({'message': f'User {user.username} added to group {group.name}'}, 
                           status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def remove_member(self, request, pk=None):
        """Remove a user from a group"""
        group = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = CustomUser.objects.get(pk=user_id)
            if user in group.members.all():
                group.members.remove(user)
                return Response({'message': f'User {user.username} removed from group {group.name}'}, 
                               status=status.HTTP_200_OK)
            else:
                return Response({'error': 'User is not a member of this group'}, 
                               status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get all messages for a specific group"""
        group = self.get_object()
        messages = group.messages.all().order_by('timestamp')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def course_groups(self, request):
        """Get all course groups"""
        groups = Group.objects.filter(group_type='Course')
        serializer = self.get_serializer(groups, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def qualification_groups(self, request):
        """Get all qualification groups"""
        groups = Group.objects.filter(group_type='Qualification')
        serializer = self.get_serializer(groups, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def year_groups(self, request):
        """Get all year groups"""
        groups = Group.objects.filter(group_type='Year')
        serializer = self.get_serializer(groups, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def hobby_groups(self, request):
        """Get all hobby groups"""
        groups = Group.objects.filter(group_type='Hobby')
        serializer = self.get_serializer(groups, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def piecejob_groups(self, request):
        """Get all piece job groups"""
        groups = Group.objects.filter(group_type='Piece Job')
        serializer = self.get_serializer(groups, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        # Add the creating user as created_by
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['created_by'] = request.user
        
        # Handle course group creation
        if serializer.validated_data.get('group_type') == 'Course':
            course_code = serializer.validated_data.get('name')
            # Example: Search for users enrolled in this course and add them
            # This would need to be adjusted based on how course information is stored
            # For now, create an empty group
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

# Message Views
class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        # Set the sender to the current user
        request.data['sender'] = request.user.id
        return super().create(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter by group if group_id is provided
        group_id = self.request.query_params.get('group_id', None)
        if group_id is not None:
            queryset = queryset.filter(group_id=group_id)
        return queryset

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
        
        if not email or not password:
            return Response({
                'message': 'Email and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user with this email already exists
        if CustomUser.objects.filter(email=email).exists():
            return Response({
                'message': 'A user with this email already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # Generate and send OTP to the email
        otp = generate_otp(email)
        
        if otp:
            return Response({
                'message': 'OTP sent to your email, please verify it.'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'message': 'Error generating OTP, please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        is_valid_otp = verify_otp(email, otp)
        
        if is_valid_otp:
            # If OTP is valid, create user with email as username
            user = CustomUser.objects.create_user(
                username=email,  # Using email as username
                email=email,
                password=password,
                is_active=True
            )
            
            # Generate tokens for immediate login
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'User created successfully!',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'email': user.email
                }
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'message': 'Invalid OTP, please try again.'
            }, status=status.HTTP_400_BAD_REQUEST)



# Login View
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']

            if not user.is_active:
                return Response({
                    'message': 'Your account is inactive. Please contact support.'
                }, status=status.HTTP_400_BAD_REQUEST)
                
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

class DirectMessageViewSet(viewsets.ModelViewSet):
    queryset = DirectMessage.objects.all()
    serializer_class = DirectMessageSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        # Set the sender to the current user
        request.data['sender'] = request.user.id
        return super().create(request, *args, **kwargs)
    
    def get_queryset(self):
        """
        Filter messages to only include those where the current user
        is either the sender or recipient
        """
        user = self.request.user
        return DirectMessage.objects.filter(
            Q(sender=user) | Q(recipient=user)
        ).order_by('timestamp')
    
    @action(detail=False, methods=['get'])
    def with_user(self, request):
        """Get all messages between current user and another user"""
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            other_user = CustomUser.objects.get(id=user_id)
            messages = DirectMessage.objects.filter(
                (Q(sender=request.user) & Q(recipient=other_user)) |
                (Q(sender=other_user) & Q(recipient=request.user))
            ).order_by('timestamp')
            
            # Mark all messages from other user as read
            unread_messages = messages.filter(sender=other_user, recipient=request.user, read=False)
            for msg in unread_messages:
                msg.read = True
                msg.save()
                
            serializer = self.get_serializer(messages, many=True)
            return Response(serializer.data)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread messages for current user"""
        count = DirectMessage.objects.filter(recipient=request.user, read=False).count()
        return Response({'unread_count': count})
    
    @action(detail=False, methods=['get'])
    def recent_contacts(self, request):
        """Get list of users the current user has recently messaged with"""
        user = request.user
        
        # Get unique users from recent conversations
        # First, get all messages where the current user is involved
        messages = DirectMessage.objects.filter(
            Q(sender=user) | Q(recipient=user)
        ).order_by('-timestamp')
        
        # Extract unique users from these messages
        contacts = set()
        contacts_data = []
        
        for msg in messages:
            contact = msg.recipient if msg.sender == user else msg.sender
            if contact.id not in contacts:
                contacts.add(contact.id)
                # Get unread count for this contact
                unread = DirectMessage.objects.filter(
                    sender=contact, recipient=user, read=False
                ).count()
                
                contacts_data.append({
                    'id': contact.id,
                    'username': contact.username,
                    'unread_count': unread,
                    'last_message_time': msg.timestamp
                })
                
                # Limit to 10 recent contacts
                if len(contacts_data) >= 10:
                    break
        
        return Response(contacts_data)