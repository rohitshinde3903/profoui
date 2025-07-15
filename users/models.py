from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    role = models.CharField(max_length=10, default='user')
    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)
    is_mobile_verified = models.BooleanField(default=False)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True, default='profile_pics/df.png')
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    following = models.ManyToManyField(
        'self',
        symmetrical=False,
        through='Follow',
        through_fields=('follower', 'followed'),
        related_name='followers',
    )
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    
    # New fields
    skills = models.ManyToManyField(Skill, blank=True, related_name='users')
    intro_video = models.FileField(upload_to='intro_videos/', blank=True, null=True)
    career_growth = models.TextField(blank=True, null=True)
    tagline = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.username

    
    


# Follow Model (Many-to-many relationship between users)
class Follow(models.Model):
    follower = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='following_relationships',  # Unique reverse accessor
    )
    followed = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='follower_relationships',  # Unique reverse accessor
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'followed')  # Prevent duplicates


# Notification Model
from django.db import models
from django.utils.timezone import now
import pytz

from django.db import models
from django.utils.timezone import now
import pytz


from django.db import models
from django.utils.timezone import now, timedelta
import pytz

def get_ist_time():
    """
    Returns the current time adjusted to IST (Asia/Kolkata timezone)
    and adds 5 hours 30 minutes.
    """
    india_tz = pytz.timezone('Asia/Kolkata')
    current_time = now().astimezone(india_tz)
    adjusted_time = current_time + timedelta(hours=5, minutes=30)
    return adjusted_time

class Notification(models.Model):
    user = models.ForeignKey(
        'CustomUser',
        related_name='notifications',
        on_delete=models.CASCADE
    )
    message = models.TextField()
    created_at = models.DateTimeField(default=get_ist_time)  # Adjusted time with +5:30
    is_read = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        """
        Ensure created_at is always set in IST timezone with +5:30 adjustment when saving.
        """
        if not self.created_at:
            india_tz = pytz.timezone('Asia/Kolkata')
            current_time = now().astimezone(india_tz)
            self.created_at = current_time + timedelta(hours=5, minutes=30)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:50]}"

    class Meta:
        ordering = ['-created_at']



# Social Media Link Model
class SocialMediaLink(models.Model):
    PLATFORM_CHOICES = [
        ('Facebook', 'Facebook'),
        ('Twitter', 'Twitter'),
        ('Instagram', 'Instagram'),
        ('LinkedIn', 'LinkedIn'),
        ('YouTube', 'YouTube'),
        ('GitHub', 'GitHub'),
        ('Website', 'Personal Website'),
        ('Leetcode', 'Leetcode'),
        ('Codechef', 'Codechef'),
        ('Naukari', 'Naukari'),
        ('Indeed', 'Indeed'),
        ('Other', 'Other'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='social_links',
        on_delete=models.CASCADE
    )
    platform = models.CharField(
        max_length=100,
        choices=PLATFORM_CHOICES,
        default='Instagram'
    )
    url = models.URLField(help_text="Enter the full URL (e.g., https://example.com)")
    description = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Optional description about the social media link"
    )
    click_count = models.PositiveIntegerField(default=0, editable=False)  # Track the number of clicks
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set the timestamp when created
    updated_at = models.DateTimeField(auto_now=True)  # Automatically update the timestamp when modified
    is_active = models.BooleanField(
        default=True,
        help_text="Uncheck this to disable the social media link."
    )

    is_private = models.BooleanField(
        default=False,
        help_text="Check this to make the link private."
    )

    class Meta:
        verbose_name = "Social Media Link"
        verbose_name_plural = "Social Media Links"
        ordering = ['-created_at']  # Default ordering: newest first

    def increment_click_count(self):
        """Increments the click count by 1."""
        self.click_count += 1
        self.save()

    def __str__(self):
        return f"{self.platform} - {self.user.username}"


# Link Click Model
class LinkClick(models.Model):
    link = models.ForeignKey(SocialMediaLink, related_name="clicks", on_delete=models.CASCADE)
    clicked_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        # Ensure clicks are logged once per day for each link
        if not self.pk:
            self.clicked_at = timezone.localtime(self.clicked_at).date()  # Only store the date part
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.link.platform} clicked on {self.clicked_at}"


# User Activity Log Model
class UserActivityLog(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} performed {self.action} at {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']


# User Subscription Model
class UserSubscription(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    plan = models.CharField(max_length=50, choices=[('Basic', 'Basic'), ('Premium', 'Premium'), ('VIP', 'VIP')])
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=[('Active', 'Active'), ('Expired', 'Expired'), ('Suspended', 'Suspended')])

    def __str__(self):
        return f"{self.user.username} - {self.plan} ({self.status})"

    class Meta:
        ordering = ['-start_date']


# User Preferences Model
class UserPreferences(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    theme = models.CharField(max_length=50, choices=[('Light', 'Light'), ('Dark', 'Dark')], default='Light')
    receive_notifications = models.BooleanField(default=True)
    receive_promotions = models.BooleanField(default=True)

    def __str__(self):
        return f"Preferences for {self.user.username}"


# User Post Model
class UserPost(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Post by {self.user.username} on {self.created_at}"

    class Meta:
        ordering = ['-created_at']


# User Comment Model
class UserComment(models.Model):
    post = models.ForeignKey(UserPost, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.title}"

    class Meta:
        ordering = ['-created_at']


# User Feedback Model
class UserFeedback(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    feedback = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.user.username} on {self.submitted_at}"
