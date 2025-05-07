from django.urls import path
from ..views import GroupListCreate,CreateGroupView, JoinGroupView,LeaveGroupView, InstitutionGroupsView, CityHobbyGroupsView, GroupSuggestionsView


urlpatterns = [

   # path('groups/<uuid:group_id>/icon/', UploadGroupIconView.as_view(), name='upload-icon'),
   # path('notifications/', GetNotificationsView.as_view(), name='get-notifications'),
    path('groups/', GroupListCreate.as_view(), name='group-list-create'),
    path('groups/create/', CreateGroupView.as_view(), name='create-group'),
    path('groups/<uuid:group_id>/join/', JoinGroupView.as_view(), name='join-group'),
    path('groups/<uuid:group_id>/leave/', LeaveGroupView.as_view(), name='leave-group'),
    path('groups/my-institution/', InstitutionGroupsView.as_view(), name='institution-groups'),
    path('groups/my-city-hobbies/', CityHobbyGroupsView.as_view(), name='city-hobby-groups'),
    path('groups/suggestions/', GroupSuggestionsView.as_view(), name='group-suggestions'),
]
