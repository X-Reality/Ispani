from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CustomUserViewSet, OTPViewSet, VerifyOTPView, RegistrationView, GroupViewSet,
    MessageViewSet, SubjectSpecializationViewSet, TutorProfileViewSet,
    TutoringSessionViewSet, BookingViewSet, SignUpView, LoginView, LogoutView,
    HobbyViewSet, PieceJobViewSet, DirectMessageViewSet
)

urlpatterns = [
    # Authentication Views
    path('signup/', SignUpView.as_view(), name='signup'),  # Sign up endpoint
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),  # Verify OTP endpoint
    path('login/', LoginView.as_view(), name='login'),  # Login endpoint
    path('logout/', LogoutView.as_view(), name='logout'),  # Logout endpoint
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API Endpoints - List and Create
    path('users/', CustomUserViewSet.as_view({'get': 'list', 'post': 'create'}), name='users'),
    path('registration/', RegistrationView.as_view(), name='registration'),
    
    # Group endpoints
    path('groups/', GroupViewSet.as_view({'get': 'list', 'post': 'create'}), name='group-list'),
    path('groups/<int:pk>/', GroupViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='group-detail'),
    path('groups/<int:pk>/join/', GroupViewSet.as_view({'post': 'join_group'}), name='join-group'),
    path('groups/<int:pk>/add_member/', GroupViewSet.as_view({'post': 'add_member'}), name='group-add-member'),
    path('groups/<int:pk>/remove_member/', GroupViewSet.as_view({'post': 'remove_member'}), name='group-remove-member'),
    path('groups/<int:pk>/messages/', GroupViewSet.as_view({'get': 'messages'}), name='group-messages'),
    path('groups/filter/', GroupViewSet.as_view({'get': 'filter_groups'}), name='group-filter'),
    path('groups/announcements/', GroupViewSet.as_view({'get': 'announcements'}), name='group-announcements'),
    path('groups/course/', GroupViewSet.as_view({'get': 'course_groups'}), name='course-groups'),
    path('groups/qualification/', GroupViewSet.as_view({'get': 'qualification_groups'}), name='qualification-groups'),
    path('groups/year/', GroupViewSet.as_view({'get': 'year_groups'}), name='year-groups'),
    path('groups/hobby/', GroupViewSet.as_view({'get': 'hobby_groups'}), name='hobby-groups'),
    path('groups/piecejob/', GroupViewSet.as_view({'get': 'piecejob_groups'}), name='piecejob-groups'),
    
    # Direct Message Endpoints
    path('direct-messages/', DirectMessageViewSet.as_view({'get': 'list', 'post': 'create'}), name='direct-message-list-create'),
    path('direct-messages/<int:pk>/', DirectMessageViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='direct-message-detail'),
    path('direct-messages/with-user/', DirectMessageViewSet.as_view({'get': 'with_user'}), name='direct-messages-with-user'),
    path('direct-messages/unread-count/', DirectMessageViewSet.as_view({'get': 'unread_count'}), name='direct-messages-unread-count'),
    path('direct-messages/recent-contacts/', DirectMessageViewSet.as_view({'get': 'recent_contacts'}), name='direct-messages-recent-contacts'),

    # MessageViewSet URLs
    path('messages/', MessageViewSet.as_view({'get': 'list', 'post': 'create'}), name='message-list-create'),
    path('messages/<int:pk>/', MessageViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='message-detail'),

    # Subject and Tutor Endpoints
    path('subject-specializations/', SubjectSpecializationViewSet.as_view({'get': 'list', 'post': 'create'}), name='subject_specializations'),
    path('tutor-profiles/', TutorProfileViewSet.as_view({'get': 'list', 'post': 'create'}), name='tutor_profiles'),
    path('tutoring-sessions/', TutoringSessionViewSet.as_view({'get': 'list', 'post': 'create'}), name='tutoring_sessions'),
    path('bookings/', BookingViewSet.as_view({'get': 'list', 'post': 'create'}), name='bookings'),

    # Hobby and Piece Job Endpoints
    path('hobbies/', HobbyViewSet.as_view({'get': 'list', 'post': 'create'}), name='hobbies'),
    path('piecejobs/', PieceJobViewSet.as_view({'get': 'list', 'post': 'create'}), name='piecejobs'),
]