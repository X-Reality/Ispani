from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from .authentication import CustomUser, StudentProfile, TutorProfile

class Booking(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    tutor = models.ForeignKey(TutorProfile, on_delete=models.CASCADE)
    topic = models.CharField(max_length=200)
    date = models.DateTimeField()
    paid = models.BooleanField(default=False)
    meeting_link = models.URLField(null=True, blank=True)
    commission_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    tutor_earning = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    status = models.CharField(max_length=50, choices=[
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("completed", "Completed")
    ], default="pending")

    def __str__(self):
        return f"{self.student} - {self.tutor} on {self.date}"

# -----------------------------
# Payment Model
# -----------------------------
class Payment(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    is_successful = models.BooleanField(default=False)
    payment_date = models.DateTimeField(default=timezone.now)
    payment_gateway_id = models.CharField(max_length=255)  # Stripe session ID, etc.


# -----------------------------
# Payout Model
# -----------------------------
class TutorEarning(models.Model):
    tutor = models.ForeignKey(TutorProfile, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    related_bookings = models.ManyToManyField(Booking)
    week_start = models.DateField()
    week_end = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Use this instead of direct reference to User model
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.message[:30]}"
class Review(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.booking}"
