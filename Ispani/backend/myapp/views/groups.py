from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status,generics

from ..models.groups import GroupChat
from ..serializers import GroupChatSerializer,GroupCreateSerializer

class CreateGroupView(APIView):
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

    def post(self, request, group_id):
        try:
            group = GroupChat.objects.get(id=group_id)
            group.members.add(request.user)
            return Response({"message": "Joined group successfully."}, status=status.HTTP_200_OK)
        except GroupChat.DoesNotExist:
            return Response({"error": "Group not found."}, status=status.HTTP_404_NOT_FOUND)

class LeaveGroupView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, group_id):
        try:
            group = GroupChat.objects.get(id=group_id)
            group.members.remove(request.user)
            return Response({"message": "Left group successfully."}, status=status.HTTP_200_OK)
        except GroupChat.DoesNotExist:
            return Response({"error": "Group not found."}, status=status.HTTP_404_NOT_FOUND)

class InstitutionGroupsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        institution = getattr(request.user.studentprofile, 'institution', None)
        if not institution:
            return Response({"error": "No institution linked to your profile."}, status=status.HTTP_400_BAD_REQUEST)

        groups = GroupChat.objects.filter(institution=institution)
        return Response(GroupChatSerializer(groups, many=True).data)

class CityHobbyGroupsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = request.user.studentprofile if hasattr(request.user, 'studentprofile') else None
        city = profile.city if profile else None
        hobbies = profile.hobbies.all() if profile else []

        if not city:
            return Response({"error": "No city linked to your profile."}, status=status.HTTP_400_BAD_REQUEST)

        groups = GroupChat.objects.filter(city=city, hobbies__in=hobbies).distinct()
        return Response(GroupChatSerializer(groups, many=True).data)
    
class GroupSuggestionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get the user's profile and hobbies/interests
        profile = request.user.studentprofile if hasattr(request.user, 'studentprofile') else None
        if not profile:
            return Response({"error": "No profile found for user."}, status=status.HTTP_400_BAD_REQUEST)

        user_hobbies = profile.hobbies.all()

        if not user_hobbies:
            return Response({"error": "No hobbies linked to your profile."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch all groups that the user is not a member of
        user_groups = request.user.groupchat_set.all()
        all_groups = GroupChat.objects.exclude(id__in=[group.id for group in user_groups])

        # Calculate the similarity score for each group based on common hobbies
        group_scores = []
        for group in all_groups:
            common_hobbies = set(group.hobbies.all()) & set(user_hobbies)
            score = len(common_hobbies)
            group_scores.append((group, score))

        # Sort groups by score (descending order)
        group_scores.sort(key=lambda x: x[1], reverse=True)

        # Serialize and return the top suggestions
        suggested_groups = [group for group, score in group_scores if score > 0]
        return Response(GroupChatSerializer(suggested_groups, many=True).data, status=status.HTTP_200_OK)
