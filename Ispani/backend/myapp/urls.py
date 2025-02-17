from django.urls import path, re_path
from myapp.views import * 
from . import consumers


urlpatterns = [
    path('signup/', StudentProfileListCreate.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('groups/', GroupListCreate.as_view(), name='group-list-create'),
    path('study-groups/', study_groups, name='study-groups'),
    path('interest-groups/', interest_groups, name='interest-groups'),
    path('messages/', MessageListCreate.as_view(), name='message-list-create'),
    path('join-group/', join_group, name='join-group'),
    path('tutor_signup/', TutorSignupView.as_view(), name='tutor_signup'),
    path('available-tutors/',AvailableTutorsView.as_view(), name='available-tutors'),
    path('book-tutor/', BookTutorView.as_view(), name='book-tutor'),
    path('my-sessions/', StudentSessionsView.as_view(), name='my-sessions'),
]

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<group_id>\d+)/$', consumers.ChatConsumer.as_asgi()),
]
