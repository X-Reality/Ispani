from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework import status,generics

from ..models.groups import GroupChat
from ..serializers import GroupChatSerializer,GroupCreateSerializer

class CreateGroupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        name = request.data.get("name")
        city = request.data.get("city")
        institution = request.data.get("institution", "")
        hobbies = request.data.get("hobbies", [])

        if not name or not city:
            return Response({"error": "Name and city are required."}, status=status.HTTP_400_BAD_REQUEST)

        group = GroupChat.objects.create(
            name=name,
            city=city,
            institution=institution,
            created_by=request.user
        )
        group.members.add(request.user)
        group.hobbies.set(hobbies)

        return Response(GroupChatSerializer(group).data, status=status.HTTP_201_CREATED)
    
class GroupListCreate(generics.ListCreateAPIView):
    queryset = GroupChat.objects.all()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return GroupCreateSerializer
        return GroupChatSerializer

    def perform_create(self, serializer):
        serializer.save(admin=self.request.user)

class JoinGroupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, group_id):
        try:
            group = GroupChat.objects.get(id=group_id)
            group.members.add(request.user)
            return Response({"message": "Joined group successfully."}, status=status.HTTP_200_OK)
        except GroupChat.DoesNotExist:
            return Response({"error": "Group not found."}, status=status.HTTP_404_NOT_FOUND)

class LeaveGroupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, group_id):
        try:
            group = GroupChat.objects.get(id=group_id)
            group.members.remove(request.user)
            return Response({"message": "Left group successfully."}, status=status.HTTP_200_OK)
        except GroupChat.DoesNotExist:
            return Response({"error": "Group not found."}, status=status.HTTP_404_NOT_FOUND)

class InstitutionGroupsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        institution = getattr(request.user.studentprofile, 'institution', None)
        if not institution:
            return Response({"error": "No institution linked to your profile."}, status=status.HTTP_400_BAD_REQUEST)

        groups = GroupChat.objects.filter(institution=institution)
        return Response(GroupChatSerializer(groups, many=True).data)

class CityHobbyGroupsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        profile = request.user.studentprofile if hasattr(request.user, 'studentprofile') else None
        city = profile.city if profile else None
        hobbies = profile.hobbies.all() if profile else []

        if not city:
            return Response({"error": "No city linked to your profile."}, status=status.HTTP_400_BAD_REQUEST)

        groups = GroupChat.objects.filter(city=city, hobbies__in=hobbies).distinct()
        return Response(GroupChatSerializer(groups, many=True).data)
    
class GroupSuggestionsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        profile = getattr(request.user, 'studentprofile', None)
        if not profile:
            return Response({"error": "No profile found for user."}, status=status.HTTP_400_BAD_REQUEST)

        user_hobbies = profile.hobbies.all()
        if not user_hobbies:
            return Response({"error": "No hobbies linked to your profile."}, status=status.HTTP_400_BAD_REQUEST)

        user_groups = request.user.groupchat_set.all()
        all_groups = GroupChat.objects.exclude(id__in=user_groups.values_list("id", flat=True))

        suggestions = []

        for group in all_groups:
            score = 0
            group_hobbies = set(group.hobbies.all())
            common_hobbies = set(user_hobbies) & group_hobbies
            score += len(common_hobbies)

            if group.city == profile.city:
                score += 2  # city match is weighted more

            if group.institution == profile.institution:
                score += 2  # institution match is also weighted more

            score += group.members.count() * 0.05  # small boost for popularity

            if score > 0:
                suggestions.append((group, score))

        # Sort by descending score
        suggestions.sort(key=lambda x: x[1], reverse=True)

        # Limit results to top 10
        top_groups = [group for group, score in suggestions[:10]]
        serialized = GroupChatSerializer(top_groups, many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)
    
class JoinedGroupsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        user_groups = request.user.groups_joined.all()
        serializer = GroupChatSerializer(user_groups, many=True)
        return Response(serializer.data)

class JoinableGroupsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        joinable = GroupChat.objects.exclude(members=request.user)
        serializer = GroupChatSerializer(joinable, many=True)
        return Response(serializer.data)

