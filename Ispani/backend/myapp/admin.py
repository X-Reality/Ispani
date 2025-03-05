from django.contrib import admin
from .models import (
    CustomUser, OTP, Registration, Group, Message,
    SubjectSpecialization, TutorProfile, TutoringSession, Booking
)

# Register CustomUser
admin.site.register(CustomUser)






