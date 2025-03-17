from rest_framework import serializers
from .models import (
    CustomUser , OTP, Registration, Group, Message, 
    SubjectSpecialization, TutorProfile, TutoringSession, Booking,
    Hobby, PieceJob, DirectMessage
)
import random
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db import transaction

class HobbySerializer(serializers.ModelSerializer):
    class Meta:
        model = Hobby
        fields = ['id', 'name']


class PieceJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = PieceJob
        fields = ['id', 'name']


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'password']

    def create(self, validated_data):
        # Create a new user with a hashed password
        user = CustomUser.objects.create_user(
            email=validated_data.get('email'), 
            password=validated_data['password'],
        )
        return user


def generate_otp(email):
    otp_code = str(random.randint(100000, 999999))  # Generate a 6-digit OTP
    
    # Delete any existing OTP for this email
    OTP.objects.filter(email=email).delete()
    
    # Create new OTP
    otp = OTP.objects.create(
        email=email, 
        code=otp_code,
        user_data={}  # Empty dict as placeholder
    )
    
    # Send email
    send_mail(
        'Your OTP Code',
        f'Your OTP code is: {otp_code}',
        settings.DEFAULT_FROM_EMAIL,
        [email],
    )
    return otp

        


class OTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTP
        fields = ['email', 'code', 'user_data', 'created_at']
        read_only_fields = ['created_at']


class RegistrationSerializer(serializers.ModelSerializer):
    hobbies = serializers.ListField(child=serializers.CharField(), write_only=True)
    piece_jobs = serializers.ListField(child=serializers.CharField(), write_only=True)
    year_of_study = serializers.IntegerField()  # Ensure year_of_study is an integer

    class Meta:
        model = Registration
        fields = ['id', 'user', 'course', 'qualification', 'year_of_study', 'piece_jobs', 'hobbies', 'communication_preference']

    def create(self, validated_data):
        hobbies_data = validated_data.pop('hobbies', [])
        piece_jobs_data = validated_data.pop('piece_jobs', [])
        user = validated_data.get('user')

        with transaction.atomic():
            # Create the registration
            registration = Registration.objects.create(**validated_data)

            # Create or associate PieceJob instances
            for job in piece_jobs_data:
                piece_job, created = PieceJob.objects.get_or_create(name=job)
                registration.piece_jobs.add(piece_job)

            # Create or associate Hobby instances
            for hobby in hobbies_data:
                hobby_instance, created = Hobby.objects.get_or_create(name=hobby)
                registration.hobbies.add(hobby_instance)

            # Update user qualification and year if not already set
            if not user.qualification and validated_data.get('qualification'):
                user.qualification = validated_data['qualification']
            
            if not user.year_of_study and validated_data.get('year_of_study'):
                user.year_of_study = validated_data['year_of_study']
            
            user.save()
            
            # Add user to appropriate groups
            if validated_data.get('qualification'):
                add_user_to_qualification_group(user, validated_data['qualification'])
            
            if validated_data.get('year_of_study'):
                add_user_to_year_group(user, validated_data['year_of_study'])
            
            # Add user to hobby groups
            for hobby in registration.hobbies.all():
                add_user_to_hobby_group(user, hobby)
            
            # Add user to piece job groups
            for job in registration.piece_jobs.all():
                add_user_to_piecejob_group(user, job)
                
            return registration


def add_user_to_qualification_group(user, qualification):
    group_name = f"Qualification: {qualification}"
    group, created = Group.objects.get_or_create(
        name=group_name,
        group_type='Qualification',
        defaults={'is_auto_group': True}
    )
    group.members.add(user)


def add_user_to_year_group(user, year_of_study):
    group_name = f"Year: {year_of_study}"
    group, created = Group.objects.get_or_create(
        name=group_name, 
        group_type='Year',
        defaults={'is_auto_group': True}
    )
    group.members.add(user)


def add_user_to_hobby_group(user, hobby):
    group_name = f"Hobby: {hobby.name}"
    group, created = Group.objects.get_or_create(
        name=group_name,
        group_type='Hobby',
        defaults={'is_auto_group': True}
    )
    group.members.add(user)


def add_user_to_piecejob_group(user, job):
    group_name = f"Piece Job: {job.name}"
    group, created = Group.objects.get_or_create(
        name=group_name, 
        group_type='Piece Job',
        defaults={'is_auto_group': True}
    )
    group.members.add(user)


class GroupSerializer(serializers.ModelSerializer):
    members_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Group
        fields = ['id', 'name', 'members', 'group_type', 'created_at', 'created_by', 'is_auto_group', 'members_count']
        read_only_fields = ['is_auto_group', 'members_count']
    
    def get_members_count(self, obj):
        return obj.members.count()


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = ['id', 'group', 'sender', 'sender_name', 'content', 'timestamp', 'read']
        read_only_fields = ['sender_name']
    
    def get_sender_name(self, obj):
        return obj.sender.username if obj.sender else "Unknown"


class SubjectSpecializationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectSpecialization
        fields = ['id', 'name']


class TutorProfileSerializer(serializers.ModelSerializer):
    subjects = SubjectSpecializationSerializer(many=True, read_only=True)

    class Meta:
        model = TutorProfile
        fields = ['id', 'tutor', 'subjects', 'available_times', 'is_approved']


class TutoringSessionSerializer(serializers.ModelSerializer):
    tutor = serializers.PrimaryKeyRelatedField(queryset=TutorProfile.objects.all())
    student = serializers.PrimaryKeyRelatedField(queryset=CustomUser .objects.all())
    
    class Meta:
        model = TutoringSession
        fields = ['id', 'tutor', 'student', 'subject', 'date', 'duration', 'status']


class BookingSerializer(serializers.ModelSerializer):
    session = serializers.PrimaryKeyRelatedField(queryset=TutoringSession.objects.all())
    student = serializers.PrimaryKeyRelatedField(queryset=CustomUser .objects.all())
    tutor = serializers.PrimaryKeyRelatedField(queryset=TutorProfile.objects.all())

    class Meta:
        model = Booking
        fields = ['id', 'student', 'tutor', 'session', 'status']


class DirectMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    recipient_name = serializers.SerializerMethodField()
    
    class Meta:
        model = DirectMessage
        fields = ['id', 'sender', 'recipient', 'sender_name', 'recipient_name', 'content', 'timestamp', 'read']
        read_only_fields = ['sender_name', 'recipient_name']
    
    def get_sender_name(self, obj):
        return obj.sender.username if obj.sender else "Unknown"
        
    def get_recipient_name(self, obj):
        return obj.recipient.username if obj.recipient else "Unknown"