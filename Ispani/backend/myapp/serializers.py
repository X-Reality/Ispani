from rest_framework import serializers
from .models import (
    CustomUser, OTP, Registration, Group, Message, 
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
    class Meta:
        model = CustomUser
        fields = ['id', 'email']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
        )
        return user

class SignupSerializer(serializers.ModelSerializer):
    otp = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'otp']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        otp_code = validated_data.pop('otp')
        email = validated_data.get('email')

        # Find OTP record for the provided email and code
        otp_instance = OTP.objects.filter(email=email, code=otp_code).first()
        if not otp_instance:
            raise serializers.ValidationError("Invalid OTP.")
        if otp_instance.is_expired():
            raise serializers.ValidationError("OTP has expired.")

        # If OTP is valid, create the user
        user = CustomUser.objects.create_user(
            username=email,  # Use email as username
            email=email,
            password=validated_data['password'],
            is_active=True
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


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            # Try to find the user by email
            try:
                user_obj = CustomUser.objects.get(email=email)
                # Authenticate with username field (which we set to email)
                user = authenticate(username=user_obj.username, password=password)
                
                if user:
                    if not user.is_active:
                        raise serializers.ValidationError('User account is disabled.')
                    data['user'] = user
                else:
                    raise serializers.ValidationError('Invalid email or password.')
            except CustomUser.DoesNotExist:
                raise serializers.ValidationError('Invalid email or password.')
        else:
            raise serializers.ValidationError('Must include "email" and "password".')

        return data


class OTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTP
        fields = ['email', 'code', 'user_data', 'created_at']
        read_only_fields = ['created_at']


class RegistrationSerializer(serializers.ModelSerializer):
    hobbies = serializers.PrimaryKeyRelatedField(
        queryset=Hobby.objects.all(),
        many=True,
        required=False
    )
    piece_jobs = serializers.PrimaryKeyRelatedField(
        queryset=PieceJob.objects.all(),
        many=True,
        required=False
    )
    user = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all()
    )
    
    class Meta:
        model = Registration
        fields = ['id', 'user', 'course', 'qualification', 'year_of_study', 'piece_jobs', 'hobbies', 'communication_preference']

    def create(self, validated_data):
        hobbies = validated_data.pop('hobbies', [])
        piece_jobs = validated_data.pop('piece_jobs', [])
        user = validated_data.get('user')
        
        with transaction.atomic():
            # Create the registration
            registration = Registration.objects.create(**validated_data)
            
            # Add hobbies and piece_jobs
            registration.hobbies.set(hobbies)
            registration.piece_jobs.set(piece_jobs)
            
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
            for hobby in hobbies:
                add_user_to_hobby_group(user, hobby)
            
            # Add user to piece job groups
            for job in piece_jobs:
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
    student = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    
    class Meta:
        model = TutoringSession
        fields = ['id', 'tutor', 'student', 'subject', 'date', 'duration', 'status']


class BookingSerializer(serializers.ModelSerializer):
    session = serializers.PrimaryKeyRelatedField(queryset=TutoringSession.objects.all())
    student = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
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