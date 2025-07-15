from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Follow, Notification, Skill, SocialMediaLink, LinkClick, UserActivityLog, UserSubscription, UserPreferences, UserPost, UserComment, UserFeedback
from django.core.mail import send_mail


admin.site.register(Skill)

# Custom User Admin
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = (
        'username', 'email', 'role', 'is_email_verified', 'is_mobile_verified', 
        'profile_picture_preview', 'subscription_status', 'preferences', 'post_count', 
        'comment_count', 'last_login', 'date_joined', 'profile_completion'
    )
    list_filter = ('role', 'is_email_verified', 'is_mobile_verified', 'is_active')  # Added role filter
    search_fields = ('username', 'email')  # Search by username or email
    ordering = ('username',)  # Sorting users alphabetically by username
    
    # Add actions
    actions = ['send_bulk_notifications']

    # Make profile picture preview show the image if available
    def profile_picture_preview(self, obj):
        return obj.profile_picture.url if obj.profile_picture else None
    profile_picture_preview.short_description = 'Profile Picture'

    # Add subscription status of user
    def subscription_status(self, obj):
        try:
            subscription = UserSubscription.objects.filter(user=obj).latest('start_date')
            return subscription.plan
        except UserSubscription.DoesNotExist:
            return "No subscription"
    subscription_status.short_description = "Subscription Plan"

    # Add user preferences (e.g., theme)
    def preferences(self, obj):
        return obj.userpreferences.theme
    preferences.short_description = "User Preferences"

    # Add number of posts by user
    def post_count(self, obj):
        return UserPost.objects.filter(user=obj).count()
    post_count.short_description = "Number of Posts"

    # Add number of comments by user
    def comment_count(self, obj):
        return UserComment.objects.filter(user=obj).count()
    comment_count.short_description = "Number of Comments"

    # Show the last login time for users
    def last_login(self, obj):
        return obj.last_login
    last_login.short_description = "Last Login"

    # Show the date the user joined
    def date_joined(self, obj):
        return obj.date_joined
    date_joined.short_description = "Date Joined"

    # Check if the user has completed their profile (profile picture, bio, etc.)
    def profile_completion(self, obj):
        if obj.profile_picture and obj.bio:
            return "Completed"
        return "Incomplete"
    profile_completion.short_description = "Profile Completion"

    # Action for bulk sending notifications
    def send_bulk_notifications(self, request, queryset):
        subject = "Important Notification"
        message = "This is a notification sent to all selected users."
        from_email = "admin@yourwebsite.com"
        
        for user in queryset:
            send_mail(subject, message, from_email, [user.email])

        self.message_user(request, "Notifications sent successfully.")

    send_bulk_notifications.short_description = "Send Notification to Selected Users"


# Follow Admin
@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'followed', 'created_at')
    search_fields = ('follower__username', 'followed__username')
    list_filter = ('created_at',)
    ordering = ['-created_at']


# Notification Admin
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'created_at', 'is_read')
    search_fields = ('user__username', 'message')
    list_filter = ('is_read',)
    ordering = ['-created_at']


# Social Media Link Admin
@admin.register(SocialMediaLink)
class SocialMediaLinkAdmin(admin.ModelAdmin):
    list_display = ('user', 'platform', 'url', 'click_count', 'is_active', 'created_at', 'updated_at')
    search_fields = ('user__username', 'platform')
    list_filter = ('platform', 'is_active')
    ordering = ['-created_at']


# Link Click Admin
@admin.register(LinkClick)
class LinkClickAdmin(admin.ModelAdmin):
    list_display = ('link', 'clicked_at')
    search_fields = ('link__platform',)
    list_filter = ('clicked_at',)
    ordering = ['-clicked_at']


# User Activity Log Admin
@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp', 'ip_address')
    search_fields = ('user__username', 'action', 'ip_address')
    list_filter = ('action', 'timestamp')
    ordering = ['-timestamp']


# User Subscription Admin
@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'status', 'start_date', 'end_date')
    search_fields = ('user__username', 'plan')
    list_filter = ('status', 'plan')
    ordering = ['-start_date']


# User Preferences Admin
@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = ('user', 'theme', 'receive_notifications', 'receive_promotions')
    search_fields = ('user__username',)
    list_filter = ('theme', 'receive_notifications')


# User Post Admin
@admin.register(UserPost)
class UserPostAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'created_at', 'updated_at')
    search_fields = ('user__username', 'title')
    list_filter = ('created_at',)
    ordering = ['-created_at']


# User Comment Admin
@admin.register(UserComment)
class UserCommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at', 'comment')
    search_fields = ('user__username', 'post__title', 'comment')
    list_filter = ('created_at',)
    ordering = ['-created_at']


# User Feedback Admin
@admin.register(UserFeedback)
class UserFeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'submitted_at', 'feedback')
    search_fields = ('user__username', 'feedback')
    list_filter = ('submitted_at',)
    ordering = ['-submitted_at']
