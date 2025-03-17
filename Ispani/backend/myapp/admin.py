from django.contrib import admin
from .models import (
    CustomUser, OTP, Registration, Group, Message,
    SubjectSpecialization, TutorProfile, TutoringSession, Booking
)

# Register CustomUser
admin.site.register(CustomUser)

# Register OTP model
admin.site.register(OTP)

# Register Registration model
admin.site.register(Registration)

# Register Group model
admin.site.register(Group)

# Register Message model
admin.site.register(Message)

# Register SubjectSpecialization model
admin.site.register(SubjectSpecialization)

# Register TutorProfile model
admin.site.register(TutorProfile)

# Register TutoringSession model
admin.site.register(TutoringSession)

# Register Booking model
admin.site.register(Booking)
