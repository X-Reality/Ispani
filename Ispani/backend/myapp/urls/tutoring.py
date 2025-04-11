from django.urls import path

from ..views import BookingViewSet, CalendlyOAuthCallbackView, CalendlyWebhookView, ExternalCalendarConnectionViewSet, GroupSessionViewSet, MeetingProviderViewSet, TutorAvailabilityView, get_calendly_event_types
from ..views import *


urlpatterns = [

     # TutorAvailabilityView
    path('tutor-availability/', TutorAvailabilityView.as_view(), name='tutor-availability'),
    
    # ExternalCalendarConnectionViewSet
    path('calendar-connections/', ExternalCalendarConnectionViewSet.as_view({'get': 'list', 'post': 'create'}), name='calendar-connections-list'),
    path('calendar-connections/<int:pk>/', ExternalCalendarConnectionViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='calendar-connections-detail'),
    path('calendar-connections/connect-calendly/', ExternalCalendarConnectionViewSet.as_view({'get': 'connect_calendly'}), name='connect-calendly'),
    
    # MeetingProviderViewSet
    path('meeting-providers/', MeetingProviderViewSet.as_view({'get': 'list', 'post': 'create'}), name='meeting-providers-list'),
    path('meeting-providers/<int:pk>/', MeetingProviderViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='meeting-providers-detail'),
    path('meeting-providers/<int:pk>/set-default/', MeetingProviderViewSet.as_view({'post': 'set_default'}), name='meeting-provider-set-default'),
    
    # BookingViewSet
    path('bookings/', BookingViewSet.as_view({'get': 'list', 'post': 'create'}), name='bookings-list'),
    path('bookings/<int:pk>/', BookingViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='bookings-detail'),
    path('bookings/<int:pk>/confirm-payment/', BookingViewSet.as_view({'post': 'confirm_payment'}), name='booking-confirm-payment'),
    path('bookings/<int:pk>/get-meeting-link/', BookingViewSet.as_view({'get': 'get_meeting_link'}), name='booking-get-meeting-link'),
    
    # GroupSessionViewSet
    path('group-sessions/', GroupSessionViewSet.as_view({'get': 'list'}), name='group-sessions-list'),
    path('group-sessions/join/', GroupSessionViewSet.as_view({'post': 'join'}), name='group-session-join'),
    
    # Calendly endpoints
    path('calendly/callback/', CalendlyOAuthCallbackView.as_view(), name='calendly-callback'),
    path('calendly/webhook/', CalendlyWebhookView.as_view(), name='calendly-webhook'),
    path('calendly/event-types/', get_calendly_event_types, name='calendly-event-types'),

]