from django.contrib import admin
from .models import Group, StudentProfile, Message

# Register StudentProfile model
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'year_of_study', 'course']
    search_fields = ['username', 'email', 'course']
    list_filter = ['year_of_study', 'course']

admin.site.register(StudentProfile, StudentProfileAdmin)

# Register Group model
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'year_of_study', 'course']
    filter_horizontal = ['members']  # To easily add members from the admin UI
    search_fields = ['name', 'course']
    list_filter = ['year_of_study']

admin.site.register(Group, GroupAdmin)

# Register Message model
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'recipient', 'group', 'timestamp', 'content_preview']
    list_filter = ['timestamp', 'group']
    search_fields = ['content', 'sender__username', 'recipient__username']
    date_hierarchy = 'timestamp'
    
    def content_preview(self, obj):
        # Return a preview of the message content (first 50 characters)
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    
    content_preview.short_description = 'Content'

admin.site.register(Message, MessageAdmin)