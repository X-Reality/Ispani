from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Q

from .authentication import UserSerializer

from ..models import CustomUser, Group, GroupMembership
from ..serializers import GroupSerializer, GroupMembershipSerializer

class GroupListCreate(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class CreateGroupView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        name = request.data.get('name')
        description = request.data.get('description', '')
        group_type = request.data.get('group_type', '')
        course = request.data.get('course')
        year_of_study = request.data.get('year_of_study')
        hobbies = request.data.get('hobbies')

        if not name:
            return Response({"error": "Group name is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if group_type == 'study' and not (course and year_of_study):
            return Response({"error": "Both course and year of study are required for study groups"}, 
                             status=status.HTTP_400_BAD_REQUEST)

        if group_type == 'hobby' and not hobbies:
            return Response({"error": "Hobbies are required for hobby groups"}, 
                             status=status.HTTP_400_BAD_REQUEST)

        group = Group.objects.create(
            name=name,
            description=description,
            group_type=group_type,
            course=course if group_type == 'study' else '',
            year_of_study=year_of_study if group_type == 'study' else None,
            hobbies=hobbies if group_type == 'hobby' else '',
            admin=request.user,
            invite_link=get_random_string(20)
        )

        group.members.add(request.user)

        serializer = GroupSerializer(group)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_group(request):
    group_id = request.data.get('group_id')
    
    if not group_id:
        return Response({"error": "group_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    group = get_object_or_404(Group, id=group_id)

    if group.members.filter(id=request.user.id).exists():
        return Response({"error": "You are already a member of this group"}, status=status.HTTP_400_BAD_REQUEST)

    group.members.add(request.user)

    return Response({"message": "You have successfully joined the group."}, status=status.HTTP_200_OK)

@api_view(['GET'])
def study_groups(request):
    study_groups = Group.objects.filter(group_type='study')
    serializer = GroupSerializer(study_groups, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def hobby_groups(request):
    hobby_groups = Group.objects.filter(group_type='hobby')
    serializer = GroupSerializer(hobby_groups, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_group_by_invite(request):
    invite_link = request.data.get('invite_link')

    if not invite_link:
        return Response({"error": "invite_link is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        group = Group.objects.get(invite_link=invite_link)
    except Group.DoesNotExist:
        return Response({"error": "Invalid invite link"}, status=status.HTTP_404_NOT_FOUND)

    if group.members.filter(id=request.user.id).exists():
        return Response({"error": "You are already a member of this group"}, status=status.HTTP_400_BAD_REQUEST)

    group.members.add(request.user)
    GroupMembership.objects.create(user=request.user, group=group)

    return Response({
        "message": f"You have joined the group: {group.name}",
        "group_id": group.id
    }, status=status.HTTP_200_OK)

class GroupManagementView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, group_id):
        group = get_object_or_404(Group, id=group_id)

        if not group.admin == request.user:
            return Response({"error": "Only admins can add members"}, status=status.HTTP_403_FORBIDDEN)

        user_id = request.data.get('user_id')
        role = request.data.get('role', 'MEMBER')

        if not user_id:
            return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(CustomUser, id=user_id)

        if group.members.filter(id=user.id).exists():
            return Response({"error": "User is already a member of this group"}, status=status.HTTP_400_BAD_REQUEST)

        group.members.add(user)
        membership, created = GroupMembership.objects.get_or_create(
            user=user,
            group=group,
            defaults={'role': role}
        )

        return Response(GroupMembershipSerializer(membership).data, status=status.HTTP_201_CREATED)
    
class FindStudentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('q', '')

        if len(query) < 3:
            return Response({"error": "Query must be at least 3 characters"}, status=status.HTTP_400_BAD_REQUEST)

        students = CustomUser.objects.filter(
            Q(username__icontains=query) |
            Q(student_profile__course__icontains=query) |
            Q(student_profile__hobbies__icontains=query),
            role='student'
        ).exclude(id=request.user.id).distinct()

        serializer = UserSerializer(students, many=True)
        return Response(serializer.data)



    # Rest of the methods (delete, patch, etc.)