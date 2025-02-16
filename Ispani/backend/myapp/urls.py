from django.urls import path, re_path
from myapp.views import * 
from . import consumers


urlpatterns = [
    path('signup/', StudentProfileListCreate.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('groups/', GroupListCreate.as_view(), name='group-list-create'),
    path('messages/', MessageListCreate.as_view(), name='message-list-create'),
    path('join-group/', join_group, name='join-group'),
]

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<group_id>\d+)/$', consumers.ChatConsumer.as_asgi()),
]
