from django.contrib import messages
from django.http import HttpResponseForbidden
from functools import wraps

from django.shortcuts import redirect

from PROFO.settings import LOGIN_URL

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'admin':
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("You are not authorized to access this page.")
    return _wrapped_view


def custom_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to view this page.")
            return redirect(f"{LOGIN_URL}?next={request.path}")
        return view_func(request, *args, **kwargs)
    return wrapper
