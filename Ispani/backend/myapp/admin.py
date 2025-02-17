from django.contrib import admin
from .models import Group, StudentProfile, TutorProfile

admin.site.register(StudentProfile)

class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'year_of_study', 'field_of_study']
    filter_horizontal = ['members']  # To easily add members from the admin UI

admin.site.register(Group, GroupAdmin)

class TutorProfileAdmin(admin.ModelAdmin):
    list_display = ('tutor', 'is_approved', 'available_times')
    list_filter = ('is_approved',)
    search_fields = ('tutor__username',)

    # Provide a custom action to approve multiple tutors
    actions = ['approve_tutors']

    def approve_tutors(self, request, queryset):
        # This custom action will allow an admin to approve selected tutors
        queryset.update(is_approved=True)

    approve_tutors.short_description = "Approve selected tutors"

admin.site.register(TutorProfile, TutorProfileAdmin)