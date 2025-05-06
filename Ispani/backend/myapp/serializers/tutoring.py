from rest_framework import serializers
from ..models.tutoring import Notification, TutorEarning, Review, Booking
from ..models import TutorProfile, StudentProfile

class TutorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TutorProfile
        fields = '__all__'

class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = '__all__'

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'

class TutorEarningSerializer(serializers.ModelSerializer):
    class Meta:
        model = TutorEarning
        fields = '__all__'