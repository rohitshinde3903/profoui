from urllib import request
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import CustomUserCreationForm, EditProfileForm, VerifyEmail
# from users import models
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from collections import defaultdict
from .models import Notification, SocialMediaLink, LinkClick
from users import models

from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string


from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def get_unread_notifications(request):
    unread_count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({'unread_notifications_count': unread_count})

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def get_followers_count(request, username):
    user = CustomUser.objects.get(username=username)
    followers_count = user.followers.count()
    return JsonResponse({'followers_count': followers_count})

@login_required
def get_following_count(request, username):
    user = CustomUser.objects.get(username=username)
    following_count = user.following.count()
    return JsonResponse({'following_count': following_count})


def generate_otp():
    return get_random_string(length=6, allowed_chars='0123456789')

def send_otp_email(request, user_email, otp):
    """Send OTP to the user's email."""
    request.session['otp'] = otp  # Store OTP in session for validation
    print(f"OTP saved in session: {request.session['otp']}")  # Debugging
    subject = "Email Verification OTP"
    message = f"Your email verification OTP is {otp}."
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email])



from collections import Counter

def chart_view(request):
    roles = CustomUser.objects.values_list('role', flat=True)
    role_counts = Counter(roles)
    max_count = max(role_counts.values()) if role_counts else 1

    context = {
        'role_counts': role_counts,
        'max_count': max_count
    }
    return render(request, 'admin/chart.html', context)



def send_otp_mobile(user_mobile, otp):
    # Use Twilio or similar service for sending OTP to mobile
    pass

# def register(request):
#     if request.method == 'POST':
#         form = CustomUserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             otp = generate_otp()  # Generate OTP
#             send_otp_email(request, user.email, otp)  # Send OTP to email
#             send_otp_mobile(user.mobile_number, otp)  # Send OTP to mobile
#             user.save()  # Save user instance

#             messages.success(request, 'Account created successfully. Please verify your email and mobile number.')
#             return redirect('verify_otp')  # Redirect to OTP verification page
#     else:
#         form = CustomUserCreationForm()

#     return render(request, 'users/register.html', {'form': form})

from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Store form data temporarily in the session
            request.session['registration_data'] = form.cleaned_data

            # Generate OTP and send it to the user's email
            otp = generate_otp()
            email = form.cleaned_data['email']
            send_otp_email(request, email, otp)

            messages.success(request, 'A verification email has been sent. Please verify your email.')
            return redirect('verify_otp')  # Redirect to the OTP verification page
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})




from django.shortcuts import render, redirect
from django.contrib import messages

# # Assuming you store the OTP in the session when sending it
# def send_otp_email(user_email, otp):
#     # Code to send OTP via email
#     request.session['otp'] = otp  # Save OTP in session for validation

# def otp_is_valid(otp):
#     # Retrieve the stored OTP from session
#     stored_otp = request.session.get('otp')
#     return otp == stored_otp  # Compare entered OTP with the stored one

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model

from django.contrib.auth import get_user_model

User = get_user_model()

def verify_otp(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')  # Get the entered OTP

        if otp_is_valid(request, otp):  # Check if OTP is valid
            # Retrieve registration data from the session
            registration_data = request.session.get('registration_data')
            if not registration_data:
                messages.error(request, 'Session expired. Please register again.')
                return redirect('register')

            # Create the user and save to the database
            try:
                user = User.objects.create_user(
                    username=registration_data['username'],
                    email=registration_data['email'],
                    first_name=registration_data['first_name'],
                    last_name=registration_data['last_name'],
                    mobile_number=registration_data['mobile_number'],
                    password=registration_data['password1']
                )
                user.is_email_verified = True  # Mark email as verified
                user.save()

                # Clear session data
                request.session.pop('registration_data', None)
                request.session.pop('otp', None)

                messages.success(request, 'Email verified successfully! Please log in.')
                return redirect('login')
            except IntegrityError as e:
                if 'username' in str(e):
                    messages.error(request, 'The username is already taken.')
                elif 'email' in str(e):
                    messages.error(request, 'An account with this email already exists.')
                else:
                    messages.error(request, 'An error occurred. Please try again.')
                return redirect('register')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
            return redirect('verify_otp')  # Redirect back to the OTP page

    return render(request, 'users/verify_otp.html')



@login_required
def verify_email(request):
    user = request.user

    if not user.email:  # Ensure the user has an email address
        messages.error(request, "No email address associated with your account.")
        return redirect('profile')

    otp = generate_otp()  # Generate an OTP
    request.session['otp'] = otp  # Store OTP in session for temporary use

    send_otp_email(request, user.email, otp)  # Send OTP to user's email
    messages.success(request, "A verification email has been sent. Please check your inbox.")
    return redirect('verify_otp')  # Redirect to OTP verification page



def otp_is_valid(request, otp):
    """Check if the entered OTP matches the stored OTP."""
    stored_otp = request.session.get('otp')  # Retrieve OTP from session
    print(f"Stored OTP: {stored_otp} (type: {type(stored_otp)})")  # Debugging
    print(f"Entered OTP: {otp} (type: {type(otp)})")  # Debugging
    is_valid = str(otp) == str(stored_otp)
    if is_valid:
        del request.session['otp']  # Clear OTP from session after successful validation
    return is_valid






# Login view
def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Logged in successfully.')
            return redirect('profile')  # Redirect to a profile page or dashboard
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'users/login.html')

# Logout view
def logout_user(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('login')


from django.contrib.auth.decorators import login_required
from .forms import CustomUserUpdateForm

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomUserUpdateForm
from .models import SocialMediaLink
from .decorators import custom_login_required

@custom_login_required
def profile(request):
    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('profile')
    else:
        form = CustomUserUpdateForm(instance=request.user)

    # Retrieve user's social media links
    links = SocialMediaLink.objects.filter(user=request.user)

    return render(request, 'users/profile.html', {
        'form': form,
        'links': links,  # Pass links to the template
    })




from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import EditProfileForm
from django.core.mail import send_mail
from django.conf import settings

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)

            # If the email was changed, trigger the verification process
            if user.email != request.user.email:
                # Send email verification (implement this function as per your logic)
                verify_email(user.email)
                # You can set a flag here that email change requires verification
                user.is_active = False  # Set inactive until email is verified
                user.save()
                return redirect('profile')  # Redirect to profile or a verification pending page
            else:
                form.save()
                return redirect('profile')  # Replace with your profile view URL name
    else:
        form = EditProfileForm(instance=request.user)

    return render(request, 'users/edit_profile.html', {'form': form})




from django.shortcuts import get_object_or_404
from .models import CustomUser, LinkClick, SocialMediaLink
from .forms import SocialMediaLinkForm

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError
from .forms import SocialMediaLinkForm
from .models import SocialMediaLink
from django.contrib.auth.decorators import login_required

@login_required
def social_links(request):
    if request.method == 'POST':
        form = SocialMediaLinkForm(request.POST)
        if form.is_valid():
            social_link = form.save(commit=False)
            social_link.user = request.user

            # Validate link format before saving
            try:
                if not validate_url(social_link.url):
                    raise ValidationError("Invalid URL format.")
            except ValidationError as e:
                form.add_error('url', str(e))
                messages.error(request, str(e))
                return render(request, 'users/social_links.html', {'form': form})

            if social_link.platform == 'Other':
                social_link.platform = form.cleaned_data['custom_platform']
            social_link.save()
            messages.success(request, 'Social media link added successfully!')
            return redirect('social_links')
    else:
        form = SocialMediaLinkForm()

    # Fetch all links for the current user
    links = SocialMediaLink.objects.filter(user=request.user)
    return render(request, 'users/social_links.html', {'form': form, 'links': links})


@login_required
def edit_social_link(request, link_id):
    link = get_object_or_404(SocialMediaLink, id=link_id, user=request.user)
    if request.method == 'POST':
        form = SocialMediaLinkForm(request.POST, instance=link)
        if form.is_valid():
            social_link = form.save(commit=False)

            # Validate link format before saving
            try:
                if not validate_url(social_link.url):
                    raise ValidationError("Invalid URL format.")
            except ValidationError as e:
                form.add_error('url', str(e))
                messages.error(request, str(e))
                return render(request, 'users/edit_social_link.html', {'form': form, 'link': link})

            if social_link.platform == 'Other':
                social_link.platform = form.cleaned_data['custom_platform']
            social_link.save()
            messages.success(request, 'Social media link updated successfully!')
            return redirect('social_links')
    else:
        form = SocialMediaLinkForm(instance=link)

    return render(request, 'users/edit_social_link.html', {'form': form, 'link': link})


# Utility function to validate the URL format
def validate_url(url):
    import re
    # Regular expression to validate a basic URL format
    pattern = r'^(https?://)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,6}(/.*)?$'
    return bool(re.match(pattern, url))

@login_required
def delete_social_link(request, link_id):
    link = get_object_or_404(SocialMediaLink, id=link_id, user=request.user)
    link.delete()
    messages.success(request, 'Social media link deleted successfully!')
    return redirect('social_links')

from django.shortcuts import get_object_or_404, render
from .models import CustomUser, SocialMediaLink

from django.shortcuts import render, get_object_or_404
from .models import CustomUser, LinkClick
from django.db.models import Count
from django.db.models.functions import TruncDate
import os
from django.conf import settings



def public_profile(request, username):
    user = get_object_or_404(CustomUser, username=username)
    # Fetch only public social links
    social_links = user.social_links.filter(is_private=False)

    # Fetch click trends for each link grouped by date
    most_clicked_links = []
    for link in social_links:
        daily_clicks = (
            LinkClick.objects.filter(link=link)
            .annotate(date=TruncDate('clicked_at'))
            .values('date')
            .annotate(click_count=Count('id'))
            .order_by('date')
        )
        link.daily_clicks = list(daily_clicks)  # Attach daily trends to each link
        most_clicked_links.append(link)
        
   

    return render(request, 'users/public_profile.html', {
        'user': user,
        'social_links': social_links,
        'most_clicked_links': most_clicked_links,
        
    })





from django.db.models import Q  # Import Q for complex queries
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.shortcuts import render


from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .models import CustomUser

from django.contrib.auth.decorators import login_required

def search_profiles(request):
    query = request.GET.get('q', '')
    results = []

    if query:
        # Search for users by username or bio, excluding the current user
        results = CustomUser.objects.filter(
            Q(username__icontains=query) | Q(bio__icontains=query)
        ).exclude(id=request.user.id if request.user.is_authenticated else None)

    # Paginate the results
    paginator = Paginator(results, 10)  # 10 results per page
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)  # Deliver the first page
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)  # Deliver the last page

    # Handle following list for authenticated users
    following = request.user.following.all() if request.user.is_authenticated else []

    # Pass the query, paginated results, and logged-in user's following list
    return render(request, 'users/search_profiles.html', {
        'query': query,
        'page_obj': page_obj,
        'following': following,
    })



from collections import defaultdict
from django.db.models import Count

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from collections import defaultdict
from .models import SocialMediaLink, LinkClick

@login_required
def dashboard(request):
    links = request.user.social_links.all()
    most_clicked_links = links.order_by('-click_count')[:5]
    total_clicks = sum(link.click_count for link in links)

    # Prepare daily click data for line graph
    daily_clicks = defaultdict(list)
    for link in links:
        clicks = LinkClick.objects.filter(link=link).values('clicked_at').annotate(count=Count('id')).order_by('clicked_at')
        for click in clicks:
            daily_clicks[link.id].append((click['clicked_at'], click['count']))

    return render(request, 'users/dashboard.html', {
        'most_clicked_links': most_clicked_links,
        'total_clicks': total_clicks,
        'daily_clicks': daily_clicks
    })



from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import CustomUser, Follow

from django.shortcuts import render, get_object_or_404
from .models import CustomUser, Follow

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import CustomUser, Follow

@login_required
def view_followers(request, username):
    # Fetch the profile user
    profile_user = get_object_or_404(CustomUser, username=username)

    # Allow only the user to view their followers
    if request.user == profile_user:
        # Use `select_related` to optimize the queryset and avoid fetching issues
        followers = Follow.objects.filter(followed=profile_user).select_related('follower')
    else:
        # Hide the list of followers if it's not their profile
        followers = None

    # Pass the followers and profile_user to the template
    return render(request, 'users/followers.html', {'profile_user': profile_user, 'followers': followers})



@login_required
def view_following(request, username):
    # Fetch the profile user
    profile_user = get_object_or_404(CustomUser, username=username)

    # Allow only the user to view their following list
    if request.user == profile_user:
        # Use `select_related` to optimize the queryset and fetch related data
        following = Follow.objects.filter(follower=profile_user).select_related('followed')
    else:
        # Hide the list of following users if it's not their profile
        following = None

    # Pass the following and profile_user to the template
    return render(request, 'users/following.html', {'profile_user': profile_user, 'following': following})






@login_required
def follow_user(request, user_id):
    followed_user = get_object_or_404(CustomUser, id=user_id)
    if followed_user != request.user:
        request.user.following.add(followed_user)  # Assume `following` is a ManyToMany field
        # Create a notification
        Notification.objects.create(
            user=followed_user,
            message=f"{request.user.username} started following you.",
        )
        messages.success(request, f"You are now following {followed_user.username}.")
    else:
        messages.error(request, "You cannot follow yourself.")
    return redirect('public_profile', username=followed_user.username)


@login_required
def unfollow_user(request, user_id):
    followed_user = get_object_or_404(CustomUser, id=user_id)
    if followed_user in request.user.following.all():
        request.user.following.remove(followed_user)  # Assume `following` is a ManyToMany field
        # Create a notification
        Notification.objects.create(
            user=followed_user,
            message=f"{request.user.username} unfollowed you.",
        )
        messages.success(request, f"You have unfollowed {followed_user.username}.")
    else:
        messages.error(request, f"You are not following {followed_user.username}.")
    return redirect('public_profile', username=followed_user.username)


@login_required
def delete_follower(request, user_id):
    follower_user = get_object_or_404(CustomUser, id=user_id)
    try:
        # Check if the user exists in the follower list
        follow_relationship = Follow.objects.get(followed=request.user, follower=follower_user)
        follow_relationship.delete()  # Remove the relationship
        Notification.objects.create(
            user=follower_user,
            message=f"{request.user.username} removed you as a follower.",
        )
        messages.success(request, f"You have removed {follower_user.username} from your followers.")
    except Follow.DoesNotExist:
        messages.error(request, f"{follower_user.username} is not your follower.")
    return redirect('profile', username=request.user.username)



from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db import transaction

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def notifications(request):
    # Fetch all notifications (both read and unread)
    all_notifications = request.user.notifications.order_by('-created_at')

    # Mark unread notifications as read after rendering the response
    unread_notifications = request.user.notifications.filter(is_read=False)
    unread_notifications.update(is_read=True)

    return render(request, 'users/notifications.html', {
        'notifications': all_notifications,
        'unread_count': unread_notifications.count(),
    })









@login_required
def profile_view(request, username):
    user = get_object_or_404(CustomUser, username=username)
    return render(request, 'users/profile.html', {'user': user})




from django.http import HttpResponseRedirect
from django.utils import timezone

def track_click(request, link_id):
    link = get_object_or_404(SocialMediaLink, id=link_id)
    link.click_count += 1
    link.save()

    # Log the click for daily analytics
    LinkClick.objects.create(link=link, clicked_at=timezone.now())

    return HttpResponseRedirect(link.url)

from django.shortcuts import redirect, get_object_or_404
from .models import SocialMediaLink

from django.http import HttpResponseRedirect
from django.utils import timezone
from django.shortcuts import redirect, get_object_or_404
from .models import SocialMediaLink, LinkClick
from django.contrib.auth.decorators import login_required

from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.utils import timezone
from .models import SocialMediaLink, LinkClick


def track_social_link(request, link_id):
    """
    Tracks clicks on social media links, excluding clicks by the owner.
    Logs daily analytics for non-owner clicks.
    """
    link = get_object_or_404(SocialMediaLink, id=link_id)

    # Only increment click count if the user is not the link owner
    if request.user != link.user:
        link.increment_click_count()  # Custom method to increment count

        # Log the click for daily analytics
        LinkClick.objects.create(link=link, clicked_at=timezone.now())

    # Redirect the user to the link URL
    return HttpResponseRedirect(link.url)


    # Redirect to the actual link



# users/views.py
from django.shortcuts import render

def home(request):
    return render(request, 'users/home.html')

def privacy_policy(request):
    return render(request, 'users/privacy_policy.html')

def terms(request):
    return render(request, 'users/terms.html')






from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.urls import reverse_lazy

class CustomPasswordResetView(PasswordResetView):
    template_name = "users/password_reset.html"
    email_template_name = "users/password_reset_email.html"
    subject_template_name = "users/password_reset_subject.txt"
    success_url = reverse_lazy("password_reset_done")


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = "users/password_reset_done.html"


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "users/password_reset_confirm.html"
    success_url = reverse_lazy("password_reset_complete")


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "users/password_reset_complete.html"











