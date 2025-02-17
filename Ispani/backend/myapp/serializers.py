from rest_framework import serializers
from .models import StudentProfile, Group, Message, TutorProfile, TutoringSession, Booking,SubjectSpecialization
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
            password=validated_data['password'],
            email=validated_data.get('email'),
           
            role=validated_data.get('role', 'student'),
            year_of_study=validated_data.get('year_of_study'),
            field_of_study=validated_data.get('field_of_study'),
            interests=validated_data.get('interests'),
            desired_jobs=validated_data.get('desired_jobs'),
        )
        user.is_active = True
        user.save()

        # Automatically assign the user to groups
        self.assign_to_study_groups(user)
        self.assign_to_interest_groups(user)

        return user

    def assign_to_study_groups(self, user):
        field_of_study = user.field_of_study
        year_of_study = user.year_of_study

        if field_of_study and year_of_study:
            group, created = Group.objects.get_or_create(
                name=f"{field_of_study} - Year {year_of_study}",
                field_of_study=field_of_study,
                year_of_study=year_of_study,
            )
            group.members.add(user)

    def assign_to_interest_groups(self, user):
        interests = user.interests
        if interests:
            for interest in interests.split(','):
                interest = interest.strip()
                if interest:
                    group, created = Group.objects.get_or_create(
                        name=f"{interest} Community",
                        field_of_study=None,
                        year_of_study=None,
                    )
                    group.members.add(user)

class GroupSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(queryset=StudentProfile.objects.all(), many=True, required=False)

    class Meta:
        model = Group
        fields = ['id', 'name', 'year_of_study', 'field_of_study', 'members']

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(read_only=True)
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())

    class Meta:
        model = Message
        fields = ['id', 'group', 'sender', 'content', 'timestamp']
        read_only_fields = ['sender', 'timestamp']

    def validate(self, attrs):
        group = attrs['group']
        sender = self.context['request'].user  # Directly use request.user (StudentProfile)

        if not group.members.filter(id=sender.id).exists():
            raise ValidationError("You are not a member of this group and cannot send messages here.")

        return attrs

    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)

class JoinGroupSerializer(serializers.Serializer):
    group_id = serializers.IntegerField()

    def validate(self, attrs):
        try:
            group = Group.objects.get(id=attrs['group_id'])
        except Group.DoesNotExist:
            raise ValidationError("Group does not exist.")

        student = self.context['request'].user

        if group.field_of_study and group.year_of_study:
            if group.year_of_study != student.year_of_study or group.field_of_study != student.field_of_study:
                raise ValidationError("You cannot join this group because your year of study or field of study doesn't match.")

        if group.members.filter(id=student.id).exists():
            raise ValidationError("You are already a member of this group.")

        return attrs

    def save(self):
        group = Group.objects.get(id=self.validated_data['group_id'])
        student = self.context['request'].user
        group.members.add(student)
        return group
    

class TutorSignupSerializer(serializers.ModelSerializer):
    subject_specializations = serializers.ListField(
        child=serializers.CharField(max_length=100), required=True
    )
    available_times = serializers.CharField(required=True)
    
    class Meta:
        model = TutorProfile
        fields = ['subject_specializations', 'available_times']

    def validate(self, data):
        # Ensure the user is not already a tutor
        user = self.context['request'].user
        if hasattr(user, 'tutor_profile'):
            raise ValidationError("You are already a tutor.")
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        # Create the tutor profile
        tutor_profile = TutorProfile.objects.create(
            tutor=user,
            available_times=validated_data['available_times']
        )
        
        # Create and add subjects
        subject_names = validated_data['subject_specializations']
        subjects = []
        for subject_name in subject_names:
            subject, created = SubjectSpecialization.objects.get_or_create(name=subject_name)
            subjects.append(subject)
        tutor_profile.subjects.set(subjects)

        return tutor_profile
    
class TutorProfileSerializer(serializers.ModelSerializer):
    tutor = serializers.PrimaryKeyRelatedField(queryset=StudentProfile.objects.all())
    subjects = serializers.PrimaryKeyRelatedField(queryset=SubjectSpecialization.objects.all(), many=True)
    available_times = serializers.CharField()
    is_approved = serializers.BooleanField(default=False, read_only=True)  # Not editable by user

    class Meta:
        model = TutorProfile
        fields = ['id', 'tutor', 'subjects', 'available_times', 'is_approved']

    def create(self, validated_data):
        tutor_profile = TutorProfile.objects.create(
            tutor=validated_data['tutor'],
            available_times=validated_data['available_times'],
            is_approved=False,  # New tutors are not approved by default
        )
        tutor_profile.subjects.set(validated_data['subjects'])
        return tutor_profile


# TutoringSession Serializer
class TutoringSessionSerializer(serializers.ModelSerializer):
    tutor = TutorProfileSerializer(read_only=True)
    student = serializers.PrimaryKeyRelatedField(queryset=StudentProfile.objects.all())
    
    class Meta:
        model = TutoringSession
        fields = ['id', 'tutor', 'student', 'subject', 'date', 'duration', 'status']

    def create(self, validated_data):
        tutor_profile = validated_data.get('tutor')
        student = validated_data.get('student')

        # Ensure the student isn't booking a session with themselves
        if tutor_profile.tutor == student:
            raise ValidationError("A student cannot book a session with themselves.")

        return super().create(validated_data)

# Booking Serializer
class BookingSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=StudentProfile.objects.all())
    tutor = serializers.PrimaryKeyRelatedField(queryset=TutorProfile.objects.all())
    session = serializers.PrimaryKeyRelatedField(queryset=TutoringSession.objects.all())

    class Meta:
        model = Booking
        fields = ['id', 'student', 'tutor', 'session', 'status']

    def create(self, validated_data):
        # Ensure the session is available for booking (not already booked)
        session = validated_data.get('session')
        if session.status == 'completed':
            raise ValidationError("This session has already been completed.")

        # Ensure the tutor is available for the session
        if validated_data.get('tutor').tutor != session.tutor.tutor:
            raise ValidationError("This tutor is not available for the selected session.")

        return super().create(validated_data)