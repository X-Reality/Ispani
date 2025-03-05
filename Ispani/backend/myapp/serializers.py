from rest_framework import serializers
from .models import (
    CustomUser, OTP, Registration, Group, Message, 
    SubjectSpecialization, TutorProfile, TutoringSession, Booking
)
import random
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

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
        fields = ['username', 'email', 'password', 'otp']

    def create(self, validated_data):
        otp_code = validated_data.get('otp')
        email = validated_data.get('email')

        # Find OTP record for the provided email and code
        otp_instance = OTP.objects.filter(email=email, code=otp_code).first()
        if not otp_instance:
            raise serializers.ValidationError("Invalid OTP.")
        if otp_instance.is_expired():
            raise serializers.ValidationError("OTP has expired.")

        # If OTP is valid, create the user
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            is_active=True
        )
        return user



def generate_otp(email):
    otp_code = str(random.randint(100000, 999999))  # Generate a 6-digit OTP
    otp = OTP.objects.create(email=email, code=otp_code)  # Save OTP to database
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
            user = authenticate(username=email, password=password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError('User account is disabled.')
                data['user'] = user
            else:
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
    class Meta:
        model = Registration
        fields = ['name', 'course', 'qualification', 'year_of_study', 'piece_jobs', 'hobbies', 'communication_preference']


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name', 'members', 'group_type']


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'group', 'sender', 'content', 'timestamp']


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
    tutor = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    student = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    
    class Meta:
        model = TutoringSession
        fields = ['id', 'tutor', 'student', 'subject', 'date', 'duration', 'status']


class BookingSerializer(serializers.ModelSerializer):
    session = serializers.PrimaryKeyRelatedField(queryset=TutoringSession.objects.all())
    student = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    tutor = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())

    class Meta:
        model = Booking
        fields = ['id', 'student', 'tutor', 'session', 'status']
