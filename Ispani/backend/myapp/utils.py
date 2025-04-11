from django.core.mail import send_mail
from django.conf import settings

def send_otp_email(email, otp):
    """
    Send OTP verification code to user's email
    """
    subject = "Your OTP Code"
    message = f"Your OTP code is {otp}. It expires in 5 minutes."
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]
    
    return send_mail(
        subject,
        message,
        from_email,
        recipient_list,
        fail_silently=False,
    )

def send_booking_confirmation(booking):
    """
    Send booking confirmation email to student and tutor
    """
    # Student email
    student_subject = f"Booking Confirmation: {booking.subject}"
    student_message = f"""
    Hi {booking.student.username},
    
    Your booking with {booking.tutor.username} has been confirmed.
    
    Details:
    Subject: {booking.subject}
    Date: {booking.start_time.strftime('%A, %B %d, %Y')}
    Time: {booking.start_time.strftime('%I:%M %p')} - {booking.end_time.strftime('%I:%M %p')}
    
    Meeting link: {booking.meeting_link}
    
    Thank you for using our platform!
    """
    
    send_mail(
        student_subject,
        student_message,
        settings.DEFAULT_FROM_EMAIL,
        [booking.student.email],
        fail_silently=False,
    )
    
    # Tutor email
    tutor_subject = f"New Booking: {booking.subject}"
    tutor_message = f"""
    Hi {booking.tutor.username},
    
    You have a new confirmed booking.
    
    Details:
    Student: {booking.student.username}
    Subject: {booking.subject}
    Date: {booking.start_time.strftime('%A, %B %d, %Y')}
    Time: {booking.start_time.strftime('%I:%M %p')} - {booking.end_time.strftime('%I:%M %p')}
    
    Meeting link: {booking.meeting_link}
    
    Thank you for using our platform!
    """
    
    send_mail(
        tutor_subject,
        tutor_message,
        settings.DEFAULT_FROM_EMAIL,
        [booking.tutor.email],
        fail_silently=False,
    )