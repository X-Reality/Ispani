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

    path('tutor/availability/', views.TutorAvailabilityView.as_view(), name='tutor-availability'),
    path('bookings/', views.BookingView.as_view(), name='bookings'),
    path('bookings/<int:pk>/', views.BookingDetailView.as_view(), name='booking-detail'),
    path('webhook/', views.WebhookView.as_view(), name='stripe-webhook'),
    
]

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<group_id>\d+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/private-chat/(?P<chat_id>\d+)/$',consumers.PrivateChatConsumer.as_asgi()),
    
]