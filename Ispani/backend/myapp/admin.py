from django.contrib import admin
from .models import Group, StudentProfile

admin.site.register(StudentProfile)

class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'year_of_study', 'course']
    filter_horizontal = ['members']  # To easily add members from the admin UI

admin.site.register(Group, GroupAdmin)