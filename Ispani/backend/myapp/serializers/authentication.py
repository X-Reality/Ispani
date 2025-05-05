from rest_framework import serializers
from ..models import CustomUser, StudentProfile, TutorProfile, HStudents, ServiceProvider

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'password', 'roles')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            roles=validated_data.get('roles', 'student')
        )
        return user

class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        exclude = ('user',)

class TutorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TutorProfile
        exclude = ('user',)

class HStudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = HStudents
        exclude = ('user',)

class ServiceProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceProvider
        exclude = ('user',)

class UserRegistrationSerializer(serializers.Serializer):
    role = serializers.CharField(required=True)
    # Common fields
    # Student fields
    year_of_study = serializers.IntegerField(required=False)
    course = serializers.CharField(required=False)
    hobbies = serializers.CharField(required=False)
    qualification = serializers.CharField(required=False)
    institution = serializers.CharField(required=False)
    # Tutor fields
    about = serializers.CharField(required=False)
    phone_number = serializers.IntegerField(required=False)
    hourly_rate = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    qualifications = serializers.CharField(required=False)
    # Service Provider fields
    company_name = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    typeofservice = serializers.CharField(required=False)
    interests = serializers.CharField(required=False)