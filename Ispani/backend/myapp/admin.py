from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CalendlyEvent,
    CustomUser,
    ExternalCalendarConnection,
    MeetingProvider,
    StudentProfile,
    TutorProfile,
    Group,Event,EventParticipant, 
    EventTag, EventComment, EventMedia,
    ChatRoom,
    ChatMessage,
    PrivateChat,
    PrivateMessage,
    UserStatus,
    GroupMembership,
    MessageAttachment,
    TutorAvailability,
    Booking,
    Payment
)

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

# Student Profile Admin (updated)
@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'year_of_study', 'course')
    search_fields = ('user__username', 'user__email', 'course')
    list_filter = ('year_of_study', 'course')
    raw_id_fields = ('user',)

# Tutor Profile Admin (new)
@admin.register(TutorProfile)
class TutorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'verification_status', 'hourly_rate', 'phone_number')
    search_fields = ('user__username',)
    list_filter = ('verification_status',)
    raw_id_fields = ('user',)

# Tutor Availability Admin (new)
@admin.register(TutorAvailability)
class TutorAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('tutor', 'start_time', 'end_time', 'is_booked')
    list_filter = ('is_booked', 'tutor')
    search_fields = ('tutor__username',)
    date_hierarchy = 'start_time'
    raw_id_fields = ('tutor',)

# Booking Admin (new)
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'tutor', 'status', 'start_time', 'duration_minutes', 'price')
    list_filter = ('status', 'tutor')
    search_fields = ('student__username', 'tutor__username', 'subject')
    raw_id_fields = ('student', 'tutor')

    
    def start_time(self, obj):
        return obj.availability.start_time
    start_time.short_description = 'Start Time'
    start_time.admin_order_field = 'availability__start_time'

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


# Payment Admin (new)
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('booking', 'amount', 'status', 'created_at', 'paid_at')
    list_filter = ('status',)
    search_fields = ('booking__id', 'payment_intent_id')
    raw_id_fields = ('booking',)
    date_hierarchy = 'created_at'

# Existing admin classes (updated with any necessary changes)
@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'group_type', 'year_of_study', 'course', 'hobbies', 'admin')
    search_fields = ('name', 'course', 'hobbies')
    list_filter = ('group_type', 'year_of_study')
    raw_id_fields = ('admin', 'members')

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

@admin.register(ExternalCalendarConnection)
class ExternalCalendarConnectionAdmin(admin.ModelAdmin):
    list_display = ('provider', 'calendly_username', 'is_active')

@admin.register(MeetingProvider)
class MeetingProviderAdmin(admin.ModelAdmin):
    list_display = ('provider', 'is_default')

@admin.register(CalendlyEvent)
class CalendlyEventAdmin(admin.ModelAdmin):
    list_display = ('event_type_name', 'invitee_name', 'start_time', 'status')