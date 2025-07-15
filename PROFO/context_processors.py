# context_processors.py
from django.contrib.auth.decorators import login_required

def unread_notifications_count(request):
    if request.user.is_authenticated:
        return {
            'unread_notifications_count': request.user.notifications.filter(is_read=False).count()
        }
    return {}
