from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Profile, Group,Project

# User serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'is_staff')

# Profile serializer
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('bio', 'skills', 'company_name', 'company_description')

# Registration serializer (SignUp)
class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    is_intern = serializers.BooleanField(required=True)  # True for Intern, False for Job Host

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name', 'is_intern')

    def create(self, validated_data):
        # Create the User instance
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        
        # Check if the user is an intern or job host
        is_intern = validated_data.get('is_intern')
        
        if is_intern:
            # Create an Intern Profile with no skills initially
            Profile.objects.create(user=user)
        else:
            # Set the user as a Job Host (admin)
            user.is_staff = True
            user.save()
            Profile.objects.create(user=user)

        return user

# Group serializer
class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name', 'description']

# serializers.py
class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'user', 'participants']
