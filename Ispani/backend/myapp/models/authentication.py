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
    roles = models.JSONField(default=list) 
    email = models.EmailField(unique=True)
    active_role = models.CharField(max_length=30, blank=True, null=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    username = models.CharField(max_length=150, unique=True)
    
    REQUIRED_FIELDS = ['email']
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def has_student_profile(self):
        return hasattr(self, 'studentprofile')

    def has_tutor_profile(self):
        return hasattr(self, 'tutorprofile')

    def has_jobseeker_profile(self):
        return hasattr(self, 'jobseeker')

    def __str__(self):
        return self.username

class StudentProfile(models.Model):

    REQUIRED_FIELDS = ['email'] 
    REQUIRED_FIELDS = ['username']

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student_profile',unique=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    year_of_study = models.IntegerField(null=True, blank=True)
    course = models.CharField(max_length=100, null=True, blank=True)
    hobbies = models.TextField(null=True, blank=True)
    qualification = models.TextField(null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    institution = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"Student Profile: {self.user.username}"
    
class HStudents(models.Model):

    REQUIRED_FIELDS = ['email'] 
    REQUIRED_FIELDS = ['username']

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='hstudent_profile')
    city = models.CharField(max_length=100, null=True, blank=True)
    hobbies = models.TextField(null=True, blank=True)
    schoolName = models.CharField(max_length=100, null=True, blank=True)
    studyLevel = models.CharField(max_length=100, null=True, blank=True)
    subjects = models.TextField(null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    def __str__(self):
        return f"HStudents Profile: {self.user.username}"


class TutorProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='tutor_profile')
    place = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.IntegerField()
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    cv = models.FileField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    calendly_id = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return f"Tutor Profile: {self.user.username}"
    
class ServiceProvider(models.Model):
     user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='serviceprovider_profile')
     city = models.CharField(max_length=100, null=True, blank=True)
     company = models.CharField(max_length=100)  
     about = models.CharField(max_length=100)  
     usageType = models.TextField()
     sectors = models.TextField()
     hobbies= models.TextField()
     bio = models.TextField(blank=True, null=True)
     profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
     serviceNeeds=models.TextField()

     def __str__(self):
        return f"ServiceProvider Profile: {self.user.username}"
     
class JobSeeker(models.Model):

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='jobseeker_profile',unique=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    cellnumber = models.IntegerField(null=True, blank=True)
    status = models.TextField(null=True, blank=True)
    usage = models.TextField(null=True, blank=True)
    hobbies= models.TextField()
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)


    def __str__(self):
        return f"JobSeeker Profile: {self.user.username}"
    
