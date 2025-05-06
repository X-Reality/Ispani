from datetime import timedelta, timezone
from rest_framework import viewsets, status
from rest_framework.response import Response
from ..models.tutoring import Notification, TutorEarning, Booking, Review
from ..models.authentication import TutorProfile, StudentProfile
from ..serializers.tutoring import NotificationSerializer, ReviewSerializer, TutorEarningSerializer
from ..serializers.authentication import TutorProfileSerializer, StudentProfileSerializer
from ..serializers import BookingSerializer
from rest_framework.decorators import action
from django.db import models
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
import stripe
import requests

stripe.api_key = settings.STRIPE_SECRET_KEY

class TutorProfileViewSet(viewsets.ModelViewSet):
    queryset = TutorProfile.objects.all()
    serializer_class = TutorProfileSerializer

class StudentProfileViewSet(viewsets.ModelViewSet):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET  # Set this in your .env or settings

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        booking_id = payment_intent['metadata'].get('booking_id')
        
        # Fixed import statement to avoid circular imports
        from ..models.tutoring import Booking

        try:
            booking = Booking.objects.get(id=booking_id)
            booking.is_paid = True
            booking.save()
        except Booking.DoesNotExist:
            pass

    return HttpResponse(status=200)

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    @action(detail=True, methods=['post'])
    def create_payment_intent(self, request, pk=None):
        booking = self.get_object()
        amount = 10000  # R100 in cents
        commission = amount * 0.2  # 20% commission
        earning = amount - commission

        booking.commission_amount = commission / 100
        booking.tutor_earning = earning / 100
        booking.save()

        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='zar',
            metadata={'booking_id': booking.id},
        )

        return Response({'client_secret': intent.client_secret})

    @action(detail=True, methods=['post'])
    def confirm_payment(self, request, pk=None):
        booking = self.get_object()
        payment_intent_id = request.data.get('payment_intent_id')

        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        if intent.status == 'succeeded':
            booking.is_paid = True
            booking.meeting_link = f"https://calendly.com/tutor/{booking.tutor.user.username}/session"
            booking.scheduled_time = intent.created  # placeholder
            booking.save()
            return Response({'message': 'Payment confirmed, booking updated', 'meeting_link': booking.meeting_link})
        return Response({'error': 'Payment not successful'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def tutor_earnings(self, request):
        tutor = request.user.tutorprofile
        bookings = Booking.objects.filter(tutor=tutor, is_paid=True)
        total_earning = sum(b.tutor_earning for b in bookings)
        return Response({'total_earning': total_earning})


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

class TutorEarningViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TutorEarning.objects.all()
    serializer_class = TutorEarningSerializer

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'tutorprofile'):
            return TutorEarning.objects.filter(tutor=user.tutorprofile)
        return TutorEarning.objects.none()

    @action(detail=False, methods=['get'])
    def summary(self, request):
        tutor = request.user.tutorprofile
        now = timezone.now()
        start_of_week = now - timedelta(days=now.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        total_earnings = TutorEarning.objects.filter(tutor=tutor).aggregate(models.Sum('amount'))['amount__sum'] or 0
        weekly_earnings = TutorEarning.objects.filter(tutor=tutor, week_start=start_of_week.date()).aggregate(models.Sum('amount'))['amount__sum'] or 0

        return Response({
            'total_earnings': total_earnings,
            'weekly_earnings': weekly_earnings
        })