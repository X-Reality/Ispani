from rest_framework import serializers
from ..models import (
    StudentProfile, TutorProfile,CustomUser, UserStatus
)
from django.contrib.auth.hashers import make_password

class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = ['year_of_study', 'course', 'hobbies', 'piece_jobs', 'institution']

class TutorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TutorProfile
        fields = ['subject_expertise', 'hourly_rate', 'qualifications', 'availability', 'verification_status']

class UserStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStatus
        fields = ['is_online', 'last_active', 'status_message']

class UserSerializer(serializers.ModelSerializer):
    student_profile = StudentProfileSerializer(required=False)
    tutor_profile = TutorProfileSerializer(required=False)
    status = UserStatusSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role', 'student_profile', 'tutor_profile', 'status']
        extra_kwargs = {'password': {'write_only': True}}

class UserRegistrationSerializer(serializers.ModelSerializer):
    student_profile = StudentProfileSerializer(required=False)
    tutor_profile = TutorProfileSerializer(required=False)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'role', 'student_profile', 'tutor_profile']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        student_profile_data = validated_data.pop('student_profile', None)
        tutor_profile_data = validated_data.pop('tutor_profile', None)
        
        # Hash password
        validated_data['password'] = make_password(validated_data['password'])
        
        user = CustomUser.objects.create(**validated_data)
        
        if user.role == 'student' and student_profile_data:
            StudentProfile.objects.create(user=user, **student_profile_data)
        elif user.role == 'tutor' and tutor_profile_data:
            TutorProfile.objects.create(user=user, **tutor_profile_data)
        
        return user
