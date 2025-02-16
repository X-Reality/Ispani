from rest_framework import serializers
from .models import StudentProfile, Group, Message
from rest_framework.exceptions import ValidationError

class StudentProfileSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = StudentProfile
        fields = ['id', 'username', 'email', 'password', 'year_of_study', 'field_of_study', 'interests', 'desired_jobs', 'role']

    def create(self, validated_data):
        # Create a new user with a hashed password
        user = StudentProfile.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password'],
            role=validated_data.get('role', 'student'),
            year_of_study=validated_data.get('year_of_study'),
            field_of_study=validated_data.get('field_of_study'),
            interests=validated_data.get('interests'),
            desired_jobs=validated_data.get('desired_jobs'),
        )
        return user

class GroupSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(queryset=StudentProfile.objects.all(), many=True, required=False)

    class Meta:
        model = Group
        fields = ['id', 'name', 'year_of_study', 'field_of_study', 'members']

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'group', 'sender', 'content', 'timestamp']
        read_only_fields = ['sender', 'timestamp']

    def create(self, validated_data):
        # Automatically set the sender to the currently logged-in user
        validated_data['sender'] = self.context['request'].user.studentprofile
        return super().create(validated_data)

class JoinGroupSerializer(serializers.Serializer):
    group_id = serializers.IntegerField()

    def validate(self, attrs):
        try:
            group = Group.objects.get(id=attrs['group_id'])
        except Group.DoesNotExist:
            raise ValidationError("Group does not exist.")

        student = self.context['request'].user.studentprofile

        # Check if the student's year and field match the group's
        if group.year_of_study != student.year_of_study or group.field_of_study != student.field_of_study:
            raise ValidationError("You cannot join this group because your year of study or field of study doesn't match.")

        # Check if the student is already a member of the group
        if group.members.filter(id=student.id).exists():
            raise ValidationError("You are already a member of this group.")

        return attrs

    def save(self):
        group = Group.objects.get(id=self.validated_data['group_id'])
        student = self.context['request'].user.studentprofile

        # Add the student to the group
        group.members.add(student)
        return group
