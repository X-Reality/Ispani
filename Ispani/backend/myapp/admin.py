from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import GroupChat, Hobby
from .models.tutoring import TutorEarning, Review, Booking, Notification
from .models import (
    CustomUser,
    StudentProfile,
    TutorProfile,
    Event, EventParticipant, 
    EventTag, EventComment, EventMedia,
    ChatRoom,
    ChatMessage,
    PrivateChat,
    PrivateMessage,
    UserStatus,
    GroupMembership,
    MessageAttachment,
)
from django.conf import settings

# Custom User Admin
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'display_roles', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff')  # Can't filter JSONField directly
    search_fields = ('username', 'email')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('email', 'roles', 'city')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'roles', 'password1', 'password2'),
        }),
    )

    def display_roles(self, obj):
        return ', '.join(obj.roles)
    display_roles.short_description = 'Roles'

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username',)

class TutorProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username',)

admin.site.register(TutorProfile, TutorProfileAdmin)

# Register Booking
class BookingAdmin(admin.ModelAdmin):
    list_display = ('student', 'tutor', 'topic')
    search_fields = ('student__user__username', 'tutor__user__username', 'topic')

admin.site.register(Booking, BookingAdmin)

# Register TutorEarnings
class TutorEarningsAdmin(admin.ModelAdmin):
    list_display = ('tutor', 'amount', 'created_at')
    search_fields = ('tutor__user__username',)

admin.site.register(TutorEarning, TutorEarningsAdmin)

# Register Review
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('booking', 'rating', 'comment', 'created_at')
    search_fields = ('booking__student__user__username', 'booking__tutor__user__username')
    list_filter = ('rating',)

admin.site.register(Review, ReviewAdmin)

# Register Notification
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'message', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'message')
    list_filter = ('is_read', 'created_at')

admin.site.register(Notification, NotificationAdmin)

# Event scheduling
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'start_time', 'end_time', 'is_public')
    search_fields = ('title', 'creator__username')
    list_filter = ('is_public', 'start_time')
    ordering = ('-start_time',)

@admin.register(EventParticipant)
class EventParticipantAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'role', 'status', 'joined_at')
    search_fields = ('event__title', 'user__username')
    list_filter = ('role', 'status')
    ordering = ('-joined_at',)

@admin.register(EventTag)
class EventTagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(EventComment)
class EventCommentAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'content', 'created_at')
    search_fields = ('event__title', 'user__username', 'content')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

@admin.register(EventMedia)
class EventMediaAdmin(admin.ModelAdmin):
    list_display = ('event', 'media_type', 'title', 'uploaded_by', 'uploaded_at')
    search_fields = ('event__title', 'uploaded_by__username', 'title')
    list_filter = ('media_type', 'uploaded_at')
    ordering = ('-uploaded_at',)

# Existing admin classes (updated with any necessary changes)
@admin.register(GroupChat)
class GroupChatAdmin(admin.ModelAdmin):
    list_display = ('name', 'group_type', 'city', 'institution', 'display_hobbies', 'member_count', 'admin_list', 'created_at')
    search_fields = ('name', 'city', 'institution', 'hobbies__name')
    list_filter = ('group_type', 'city', 'institution', 'hobbies')


    def display_hobbies(self, obj):
        return ', '.join([hobby.name for hobby in obj.hobbies.all()])
    display_hobbies.short_description = 'Hobbies'

    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = 'Total Members'

    def admin_list(self, obj):
        return ', '.join([admin.username for admin in obj.admins.all()])
    admin_list.short_description = 'Admins'

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'chat_type', 'created_at')
    search_fields = ('name',)
    list_filter = ('chat_type',)

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('room', 'sender', 'timestamp', 'short_content')
    search_fields = ('content', 'sender__username')
    list_filter = ('room', 'sender')
    raw_id_fields = ('sender',)
    
    def short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    short_content.short_description = 'Content'

@admin.register(PrivateChat)
class PrivateChatAdmin(admin.ModelAdmin):
    list_display = ('user1', 'user2', 'created_at')
    search_fields = ('user1__username', 'user2__username')
    raw_id_fields = ('user1', 'user2')

@admin.register(PrivateMessage)
class PrivateMessageAdmin(admin.ModelAdmin):
    list_display = ('chat', 'sender', 'timestamp', 'short_content')
    search_fields = ('content', 'sender__username')
    list_filter = ('chat', 'sender')
    raw_id_fields = ('sender',)
    
    def short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    short_content.short_description = 'Content'

@admin.register(UserStatus)
class UserStatusAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_online', 'last_active', 'status_message')
    search_fields = ('user__username',)
    raw_id_fields = ('user',)

@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'role', 'joined_at')
    search_fields = ('user__username', 'group__name')
    list_filter = ('role',)
    raw_id_fields = ('user', 'group')

@admin.register(MessageAttachment)
class MessageAttachmentAdmin(admin.ModelAdmin):
    list_display = ('message', 'attachment_type', 'file')
    search_fields = ('message__content',)
    raw_id_fields = ('message',)