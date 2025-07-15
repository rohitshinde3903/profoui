from django.urls import path

from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.urls import path
from django.contrib.auth import views as auth_views


from django.urls import path
from .views import (
    CustomPasswordResetView,
    CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetCompleteView,
)


urlpatterns = [
    path('followers-count/<str:username>/', views.get_followers_count, name='followers_count'),
    path('following-count/<str:username>/', views.get_following_count, name='following_count'),
    path('delete-follower/<int:user_id>/', views.delete_follower, name='delete_follower'),
    path('notifications/unread-count/', views.get_unread_notifications, name='unread_notifications_count'),
    path('register/', views.register, name='register'),
    path('privacy_policy/', views.privacy_policy, name='privacy_policy'),
    path('terms/', views.terms, name='terms'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('verify_email/', views.verify_email, name='verify_email'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('profile/<str:username>/followers/', views.view_followers, name='view_followers'),
    path('profile/<str:username>/following/', views.view_following, name='view_following'),
    path('social-links/', views.social_links, name='social_links'),  # Specific pattern
    path('social-link/<int:link_id>/track/', views.track_social_link, name='track_social_link'),
    path('social-links/edit/<int:link_id>/', views.edit_social_link, name='edit_social_link'),
    path('social-links/delete/<int:link_id>/', views.delete_social_link, name='delete_social_link'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('search/', views.search_profiles, name='search_profiles'),
    path('track-link/<int:link_id>/', views.track_social_link, name='track_social_link'),
    path('click/<int:link_id>/', views.track_click, name='track_click'),
    path('unfollow/<int:user_id>/', views.unfollow_user, name='unfollow_user'),
    path('follow/<int:user_id>/', views.follow_user, name='follow_user'),
    path('notifications/', views.notifications, name='notifications'),

    # Other URLs...
     path("password_reset/", CustomPasswordResetView.as_view(), name="password_reset"),
    path("password_reset/done/", CustomPasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", CustomPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/done/", CustomPasswordResetCompleteView.as_view(), name="password_reset_complete"),

    path('<str:username>/', views.public_profile, name='public_profile'),
      # Generic pattern
]








if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)



