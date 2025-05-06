from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ..views.tutoring import StudentProfileViewSet, TutorProfileViewSet, stripe_webhook
from ..views.tutoring import  BookingViewSet,NotificationViewSet,ReviewViewSet,TutorEarningViewSet

router = DefaultRouter()
router.register(r'tutors', TutorProfileViewSet)
router.register(r'students', StudentProfileViewSet)
router.register(r'bookings', BookingViewSet)
router.register(r'notifications', NotificationViewSet)
router.register(r'earnings', TutorEarningViewSet, basename='earnings')
router.register(r'reviews', ReviewViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('webhook/', stripe_webhook, name='stripe_webhook'),
]