from django.urls import path, re_path,include
from . import views
from .views import * 
from . import consumers
from .consumers import PrivateChatConsumer, ChatConsumer 


urlpatterns = [
    # Authentication URLs
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('verify-otp/', views.VerifyOTPView.as_view(), name='verify-otp'),
    path('complete-registration/', views.CompleteRegistrationView.as_view(), name='complete-registration'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # User Profile URLs
    path('user/', views.UserDetailView.as_view(), name='user-detail'),
    path('user/status/', views.UpdateUserStatusView.as_view(), name='user-status'),
    path('user/switch-role/', views.SwitchRoleView.as_view(), name='switch-role'),
    
    # Group URLs
    path('groups/create/', views.CreateGroupView.as_view(), name='create-group'),
    path('groups/join/', views.join_group, name='join-group'),
    path('groups/join-by-invite/', views.join_group_by_invite, name='join-group-by-invite'),
    path('groups/study/', views.study_groups, name='study-groups'),
    path('groups/hobby/', views.hobby_groups, name='hobby-groups'),
    path('groups/<int:group_id>/manage/', views.GroupManagementView.as_view(), name='group-management'),
    
    # Chat URLs
    path('chat/rooms/', views.ChatRoomListCreateView.as_view(), name='chat-room-list'),
    path('chat/rooms/<int:room_id>/messages/', views.ChatMessageListView.as_view(), name='room-messages'),
    path('chat/rooms/<int:room_id>/send/', views.SendMessageView.as_view(), name='send-message'),
    
    # Private Chat URLs
    path('chat/private/', views.PrivateChatListCreateView.as_view(), name='private-chat'),
    path('chat/private/<int:chat_id>/messages/', views.PrivateMessageListView.as_view(), name='private-messages'),
    path('chat/private/<int:chat_id>/send/', views.SendPrivateMessageView.as_view(), name='send-private-message'),
    
    # Search URL
    path('find-students/', views.FindStudentsView.as_view(), name='find-students'),

    
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

    # Event URLs
    path('events/', EventListCreateView.as_view(), name='event-list-create'),
    path('events/<int:pk>/', EventDetailView.as_view(), name='event-detail'),
    path('events/<int:pk>/participate/', EventParticipationView.as_view(), name='event-participate'),
    path('events/<int:pk>/invite/', EventInviteView.as_view(), name='event-invite'),
    path('events/<int:pk>/comments/', EventCommentView.as_view(), name='event-comments'),
    path('events/<int:pk>/media/', EventMediaView.as_view(), name='event-media'),
    path('events/tags/', EventTagsView.as_view(), name='event-tags'),
    path('events/invite/<str:invite_link>/', join_event_by_invite, name='join-event-by-invite'),
    path('events/upcoming/', upcoming_events, name='upcoming-events'),
    path('events/recommended/', recommended_events, name='recommended-events'),

    #APIs
    path('api/calendly/event-types/', get_calendly_event_types),
    
]

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<group_id>\d+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/private-chat/(?P<chat_id>\d+)/$',consumers.PrivateChatConsumer.as_asgi()),
    
]