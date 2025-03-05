from django.urls import path
from .views import (
    CustomUserViewSet, VerifyOTPView, RegistrationViewSet, GroupViewSet,
    MessageViewSet, SubjectSpecializationViewSet, TutorProfileViewSet,
    TutoringSessionViewSet, BookingViewSet, SignUpView, LoginView, LogoutView
)

urlpatterns = [
    # Authentication Views
     path('signup/', SignUpView.as_view(), name='signup'),  # Sign up endpoint
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),  # Verify OTP endpoint
    path('login/', LoginView.as_view(), name='login'),  # Login endpoint
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # API Endpoints
    path('users/', CustomUserViewSet.as_view({'get': 'list', 'post': 'create'}), name='users'),
    path('registration/', RegistrationViewSet.as_view({'get': 'list', 'post': 'create'}), name='registration'),
    path('groups/', GroupViewSet.as_view({'get': 'list', 'post': 'create'}), name='groups'),
    path('messages/', MessageViewSet.as_view({'get': 'list', 'post': 'create'}), name='messages'),
    path('subject-specializations/', SubjectSpecializationViewSet.as_view({'get': 'list', 'post': 'create'}), name='subject_specializations'),
    path('tutor-profiles/', TutorProfileViewSet.as_view({'get': 'list', 'post': 'create'}), name='tutor_profiles'),
    path('tutoring-sessions/', TutoringSessionViewSet.as_view({'get': 'list', 'post': 'create'}), name='tutoring_sessions'),
    path('bookings/', BookingViewSet.as_view({'get': 'list', 'post': 'create'}), name='bookings'),
]
