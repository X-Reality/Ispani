from django.urls import path, re_path
from . import views
from .views import * 
from . import consumers


urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
     path('users/', StudentProfileListCreate.as_view(), name='users'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('register/', CompleteRegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),


    path('groups/', GroupListCreate.as_view(), name='group-list-create'),
    path('study-groups/', study_groups, name='study-groups'),
    path('hobby-groups/', hobby_groups, name='hobby-groups'),
    path('join-group/', join_group, name='join-group'),
    path('groups/<int:group_id>/', views.group_detail, name='group-detail'),
    path('groups/<int:group_id>/messages/', views.group_messages, name='group-messages'),
    path('leave-group/', views.leave_group, name='leave-group'),

    path('messages/', MessageListCreate.as_view(), name='message-list-create'),
    path('messages/private/', SendPrivateMessageView.as_view(), name='send_private_message'),
    path('messages/private/inbox/', PrivateMessageListView.as_view(), name='private_message_list'),
    path('mark-messages-read/', views.mark_messages_read, name='mark-messages-read'),
]

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<group_id>\d+)/$', consumers.ChatConsumer.as_asgi()),
]