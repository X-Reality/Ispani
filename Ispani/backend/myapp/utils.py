# utils.py
import random
from django.core.mail import send_mail
from django.utils import timezone
from .models import OTP
from django.conf import settings

def generate_otp(email):
    otp_code = str(random.randint(100000, 999999))  # Generate a 6-digit OTP
    # Ensure to provide user_data when creating OTP
    otp = OTP.objects.create(email=email, code=otp_code, user_data='some_value')  # Replace 'some_value' with the actual user data if needed
    send_mail(
        'Your OTP Code',
        f'Your OTP code is: {otp_code}',
        settings.DEFAULT_FROM_EMAIL,
        [email],
    )
    return otp

def verify_otp(email, otp_code):
    otp = OTP.objects.filter(email=email, code=otp_code).first()
    if otp and not otp.is_expired():
        return True
    return False
