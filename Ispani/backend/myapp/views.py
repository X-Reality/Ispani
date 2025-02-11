from django.contrib.auth import login, authenticate, logout
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .models import Profile, Group
from .serializers import SignUpSerializer, ProfileSerializer, GroupSerializer

# Sign Up view (Handles registration of Interns and Job Hosts)
class SignUpView(APIView):
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            preferences = request.data.get('preferences', '')
            groups = Group.objects.filter(name__icontains=preferences)  # Match the group name with preferences

            profile = Profile.objects.create(user=user)
            profile.groups.set(groups)
            profile.save()

            return Response({"detail": "User created and assigned to groups."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Sign In view (Handles login of both Interns and Job Hosts)
class SignInView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)  # Log the user in
            # Return basic user data
            user_data = {
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
            return Response(user_data, status=status.HTTP_200_OK)
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

# Log out view (Logs out the user)
class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'detail': 'Successfully logged out'}, status=status.HTTP_200_OK)

# Profile Edit View (For editing Intern and Job Host profile)
class EditProfileView(APIView):
    def get(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)  # Allow partial updates
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Group List View (Allow students to browse through groups)
class GroupListView(generics.ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


# views.py
class EditProfileView(APIView):
    def put(self, request):
        profile = Profile.objects.get(user=request.user)
        preferences = request.data.get('preferences', '')
        profile.preferences = preferences

        # If the student wants to join a new group
        if 'join_groups' in request.data:
            group_names = request.data['join_groups']
            groups = Group.objects.filter(name__in=group_names)
            profile.groups.add(*groups)

        profile.save()
        return Response({"detail": "Profile updated."}, status=status.HTTP_200_OK)
