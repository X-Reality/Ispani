from django.urls import path, re_path
from myapp.views import * 
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
    path('interest-groups/', hobby_groups, name='interest-groups'),
    path('messages/', MessageListCreate.as_view(), name='message-list-create'),
    path('join-group/', join_group, name='join-group'),
]

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<group_id>\d+)/$', consumers.ChatConsumer.as_asgi()),
]