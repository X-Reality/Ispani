from django.urls import path
from .. import views
from ..views import GroupListCreate


urlpatterns = [
    path('', GroupListCreate.as_view(), name='group-list-create'),
    path('groups/create/', views.CreateGroupView.as_view(), name='create-group'),
    path('groups/join/', views.join_group, name='join-group'),
    path('groups/join-by-invite/', views.join_group_by_invite, name='join-group-by-invite'),
    path('groups/study/', views.study_groups, name='study-groups'),
    path('groups/hobby/', views.hobby_groups, name='hobby-groups'),
    path('groups/<int:group_id>/manage/', views.GroupManagementView.as_view(), name='group-management'),

    # Search URL
    path('find-students/', views.FindStudentsView.as_view(), name='find-students'),
]