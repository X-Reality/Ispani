import uuid
from django.conf import settings
from django.http import JsonResponse
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action

from ..models import (
    CalendlyEvent, CustomUser, ExternalCalendarConnection, 
    MeetingProvider,TutorAvailability,Booking,Payment
)
from ..serializers import (
    TutorAvailabilitySerializer, ExternalCalendarConnectionSerializer, MeetingProviderSerializer,
    BookingSerializer,CalendlyConnectionSerializer, CalendlyOAuthCallbackSerializer,
    JoinGroupSessionSerializer
)

from datetime import datetime, timedelta, timezone
from requests import Response
from .. import models


class TutorAvailabilityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get tutor ID from query params or use current user
        tutor_id = request.query_params.get('tutor_id', request.user.id)
        
        if tutor_id != str(request.user.id) and not request.user.is_staff:
            return Response({"error": "You can only view your own availabilities"}, status=403)
        
        availabilities = TutorAvailability.objects.filter(
            tutor_id=tutor_id,
            end_time__gt=timezone.now()
        ).order_by('start_time')
        
        serializer = TutorAvailabilitySerializer(availabilities, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.user.role != 'tutor':
            return Response({"error": "Only tutors can set availability"}, status=403)
        
        # Expecting list of time slots
        time_slots = request.data.get('time_slots', [])
        created_slots = []
        
        for slot in time_slots:
            serializer = TutorAvailabilitySerializer(data={
                'tutor': request.user.id,
                'start_time': slot['start_time'],
                'end_time': slot['end_time']
            })
            
            if serializer.is_valid():
                serializer.save()
                created_slots.append(serializer.data)
            else:
                # If one slot fails, delete all created slots in this batch
                TutorAvailability.objects.filter(id__in=[s['id'] for s in created_slots]).delete()
                return Response(serializer.errors, status=400)
        
        return Response(created_slots, status=201)

class ExternalCalendarConnectionViewSet(viewsets.ModelViewSet):
    serializer_class = ExternalCalendarConnectionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ExternalCalendarConnection.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def connect_calendly(self, request):
        serializer = CalendlyConnectionSerializer({})
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def fetch_availability(self, request, pk=None):
        connection = self.get_object()

        if connection.provider != 'calendly':
            return Response({'error': 'This endpoint only works with Calendly connections'}, 
                            status=status.HTTP_400_BAD_REQUEST)
    
        # Get Calendly user URI
        user_uri = connection.provider_user_id
        
        # Get current date in ISO format
        today = datetime.now().date().isoformat()
        two_months_later = (datetime.now() + timedelta(days=60)).date().isoformat()
        
        # Call Calendly API to get available time slots
        headers = {
            'Authorization': f'Bearer {connection.access_token}',
            'Content-Type': 'application/json'
        }
        
        # Get user's event types
        event_types_url = f"https://api.calendly.com/event_types?user={user_uri}"
        event_types_response = requests.get(event_types_url, headers=headers)
        
        if event_types_response.status_code != 200:
            return Response({'error': 'Failed to fetch Calendly event types'}, 
                            status=status.HTTP_400_BAD_REQUEST)
    
        event_types = event_types_response.json().get('collection', [])
        
        # Return data that can be used to display availability or redirect to Calendly
        return Response({
            'event_types': event_types,
            'calendly_user': connection.calendly_username,
            'booking_url': f"https://calendly.com/{connection.calendly_username}"
        })

class CalendlyOAuthCallbackView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = CalendlyOAuthCallbackSerializer(data=request.query_params)
        if serializer.is_valid():
            code = serializer.validated_data['code']
            
            # Exchange code for token
            token_url = 'https://auth.calendly.com/oauth/token'
            payload = {
                'client_id': settings.CALENDLY_CLIENT_ID,
                'client_secret': settings.CALENDLY_CLIENT_SECRET,
                'code': code,
                'redirect_uri': settings.CALENDLY_REDIRECT_URI,
                'grant_type': 'authorization_code'
            }
            
            response = requests.post(token_url, data=payload)
            if response.status_code == 200:
                token_data = response.json()
                
                # Get user info
                user_url = 'https://api.calendly.com/users/me'
                headers = {
                    'Authorization': f"Bearer {token_data['access_token']}"
                }
                
                user_response = requests.get(user_url, headers=headers)
                if user_response.status_code == 200:
                    user_data = user_response.json()
                    
                    # Create or update connection
                    connection, created = ExternalCalendarConnection.objects.update_or_create(
                        user=request.user,
                        provider='calendly',
                        defaults={
                            'provider_user_id': user_data['resource']['uri'],
                            'access_token': token_data['access_token'],
                            'refresh_token': token_data.get('refresh_token'),
                            'token_expires_at': datetime.now() + timedelta(seconds=token_data['expires_in']),
                            'calendly_username': user_data['resource']['name'],
                            'calendly_uri': user_data['resource']['uri'],
                            'is_active': True
                        }
                    )
                    
                    return Response({
                        'message': 'Calendly account connected successfully',
                        'username': user_data['resource']['name']
                    })
            
            return Response({'error': 'Failed to connect Calendly account'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MeetingProviderViewSet(viewsets.ModelViewSet):
    serializer_class = MeetingProviderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return MeetingProvider.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # If this is set as default, unset other defaults
        if serializer.validated_data.get('is_default', False):
            MeetingProvider.objects.filter(user=self.request.user, is_default=True).update(is_default=False)
        
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        provider = self.get_object()
        MeetingProvider.objects.filter(user=request.user, is_default=True).update(is_default=False)
        provider.is_default = True
        provider.save()
        return Response({'status': 'Default meeting provider set'})

class CalendlyWebhookView(APIView):
    permission_classes = []  # No authentication needed for webhooks
    
    def post(self, request):
        payload = request.data
        event_type = payload.get('event')
        
        if event_type == 'invitee.created':
            # Someone booked a time through Calendly
            return self.handle_invitee_created(payload)
        elif event_type == 'invitee.canceled':
            # Someone canceled their booking
            return self.handle_invitee_canceled(payload)
        
        return Response({'status': 'ignore'})
    
    def handle_invitee_created(self, payload):
        # Extract the needed data from Calendly webhook
        event_data = payload.get('payload', {}).get('event', {})
        invitee_data = payload.get('payload', {}).get('invitee', {})
        
        # Find associated tutor by URI
        calendly_uri = event_data.get('uri', '').split('/')[4]  # Extract user ID from URI
        
        try:
            calendar_connection = ExternalCalendarConnection.objects.get(
                provider='calendly',
                provider_user_id__contains=calendly_uri
            )
            
            tutor = calendar_connection.user
            
            # Create calendly event
            calendly_event = CalendlyEvent.objects.create(
                tutor=tutor,
                calendly_event_id=event_data.get('uuid'),
                calendly_event_uri=event_data.get('uri'),
                event_type_name=event_data.get('name', 'Session'),
                start_time=event_data.get('start_time'),
                end_time=event_data.get('end_time'),
                invitee_email=invitee_data.get('email'),
                invitee_name=invitee_data.get('name'),
                location=event_data.get('location', {}).get('join_url'),
                cancellation_url=invitee_data.get('cancel_url'),
                reschedule_url=invitee_data.get('reschedule_url'),
                is_group_event=False,  # Assuming default is one-on-one
            )
            
            # Try to find or create the student
            student, created = CustomUser.objects.get_or_create(
                email=invitee_data.get('email'),
                defaults={
                    'username': invitee_data.get('email').split('@')[0],
                    'role': 'student'
                }
            )
            
            # Calculate duration in minutes
            start = datetime.fromisoformat(event_data.get('start_time').replace('Z', '+00:00'))
            end = datetime.fromisoformat(event_data.get('end_time').replace('Z', '+00:00'))
            duration = int((end - start).total_seconds() / 60)
            
            # Calculate price based on tutor's hourly rate
            hourly_rate = tutor.tutor_profile.hourly_rate
            price = float(hourly_rate) * (duration / 60)
            
            # Create booking
            booking = Booking.objects.create(
                student=student,
                tutor=tutor,
                subject=event_data.get('name', 'Tutoring Session'),
                notes=invitee_data.get('questions_and_answers', [{}])[0].get('answer', ''),
                status='pending',
                booking_source='calendly',
                meeting_link=event_data.get('location', {}).get('join_url'),
                price=price,
                duration_minutes=duration,
                calendly_event=calendly_event
            )
            
            # Create payment record
            Payment.objects.create(
                booking=booking,
                student=student,
                amount=price,
                payment_intent_id=f"calendly_{uuid.uuid4()}",
                status='pending'
            )
            
            # TODO: Send email to student about payment
            
            return Response({'status': 'success'})
        
        except ExternalCalendarConnection.DoesNotExist:
            return Response({'status': 'error', 'message': 'No matching tutor found'}, 
                            status=status.HTTP_404_NOT_FOUND)
    
    def handle_invitee_canceled(self, payload):
        event_uuid = payload.get('payload', {}).get('event', {}).get('uuid')
        
        try:
            calendly_event = CalendlyEvent.objects.get(calendly_event_id=event_uuid)
            calendly_event.status = 'cancelled'
            calendly_event.save()
            
            # Update related booking
            bookings = Booking.objects.filter(calendly_event=calendly_event)
            for booking in bookings:
                booking.status = 'cancelled'
                booking.save()
            
            return Response({'status': 'success'})
        
        except CalendlyEvent.DoesNotExist:
            return Response({'status': 'error', 'message': 'Event not found'}, 
                            status=status.HTTP_404_NOT_FOUND)

class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'tutor':
            return Booking.objects.filter(tutor=user)
        else:
            return Booking.objects.filter(student=user)
    
    @action(detail=True, methods=['post'])
    def confirm_payment(self, request, pk=None):
        booking = self.get_object()
        
        # Check if the user is the student in this booking
        if request.user != booking.student:
            return Response({'error': 'You can only confirm payments for your own bookings'}, 
                           status=status.HTTP_403_FORBIDDEN)
        
        # In a real implementation, you would process payment here
        # For this example, we'll just mark the payment as completed
        payment = Payment.objects.filter(booking=booking, student=request.user).first()
        
        if payment:
            payment.status = 'completed'
            payment.paid_at = datetime.now()
            payment.save()
            
            # If this is a group session, update participant's payment status
            if booking.is_group_session:
                participant = GroupSessionParticipant.objects.filter(
                    booking=booking, student=request.user
                ).first()
                
                if participant:
                    participant.payment_status = 'completed'
                    participant.save()
            
            # Set booking to confirmed
            booking.status = 'confirmed'
            booking.save()
            
            return Response({
                'status': 'success',
                'meeting_link': booking.meeting_link
            })
        
        return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def get_meeting_link(self, request, pk=None):
        booking = self.get_object()
        
        # Check if the user is part of this booking
        if request.user != booking.student and request.user != booking.tutor:
            return Response({'error': 'You are not authorized to access this booking'}, 
                           status=status.HTTP_403_FORBIDDEN)
        
        # If user is a tutor, provide the link immediately
        if request.user.role == 'tutor':
            return Response({'meeting_link': booking.meeting_link})
        
        # If user is a student, check payment status
        if booking.is_group_session:
            participant = GroupSessionParticipant.objects.filter(
                booking=booking, student=request.user
            ).first()
            
            if participant and participant.payment_status == 'completed':
                return Response({'meeting_link': booking.meeting_link})
        else:
            payment = Payment.objects.filter(
                booking=booking, student=request.user, status='completed'
            ).exists()
            
            if payment:
                return Response({'meeting_link': booking.meeting_link})
        
        return Response({'error': 'Payment required before accessing meeting link'}, 
                       status=status.HTTP_402_PAYMENT_REQUIRED)

def get_calendly_event_types(request):
    headers = {
        "Authorization": f"Bearer {settings.CALENDLY_API_KEY}",
        "Content-Type": "application/json"
    }

    # First get your user URI
    user_response = requests.get("https://api.calendly.com/users/me", headers=headers)
    user_uri = user_response.json().get("resource", {}).get("uri")

    # Now fetch event types
    event_types_response = requests.get(
        f"https://api.calendly.com/event_types?user={user_uri}",
        headers=headers
    )
    return JsonResponse(event_types_response.json())

class GroupSessionViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        # List available group sessions
        group_sessions = Booking.objects.filter(
            is_group_session=True,
            status='confirmed',
            start_time__gt=datetime.now(),
            current_participants__lt=models.F('max_participants')
        )
        
        serializer = BookingSerializer(group_sessions, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def join(self, request):
        serializer = JoinGroupSessionSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            participant = serializer.save()
            return Response({
                'status': 'success',
                'message': 'You have joined this group session',
                'payment_required': True,
                'booking_id': serializer.validated_data['booking_id']
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

