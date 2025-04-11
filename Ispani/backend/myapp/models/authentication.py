from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractUser


ROLE_CHOICES = (
    ('tutor', 'Tutor'),
    ('student', 'Student'),
    ('hs student', 'HS Student'),
    ('service provider', 'Service Provider'),
    ('job seeker', 'Job Seeker'),

)

class CustomUser(AbstractUser):
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='student')
    email = models.EmailField(unique=True)

    REQUIRED_FIELDS = ['email']
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username

class StudentProfile(models.Model):

    REQUIRED_FIELDS = ['email'] 
    REQUIRED_FIELDS = ['username']

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student_profile')
    year_of_study = models.IntegerField(null=True, blank=True)
    course = models.CharField(max_length=100, null=True, blank=True)
    hobbies = models.TextField(null=True, blank=True)
    piece_jobs = models.TextField(null=True, blank=True)
    institution = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"Student Profile: {self.user.username}"
    
class HStudents(models.Model):

     REQUIRED_FIELDS = ['email'] 
     REQUIRED_FIELDS = ['username']

     user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='hstudent_profile')



class TutorProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='tutor_profile')
    about= models.CharField(max_length=100, null=True, blank=True)
    subject_expertise = models.TextField()
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    qualifications = models.TextField()
    verification_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='pending')
    
    def __str__(self):
        return f"Tutor Profile: {self.user.username}"
    
class ServiceProvider(models.Model):
     user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='serviceprovider_profile')
     company_name = models.CharField(max_length=100)  
     service = models.CharField(max_length=100)  
     typeofservice = models.TextField()
     qualification = models.TextField()
     interests = models.TextField()

     def __str__(self):
        return f"ServiceProvider Profile: {self.user.username}"