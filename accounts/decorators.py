from functools import wraps
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required


def admin_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.is_staff or request.user.groups.filter(name='Administrators').exists():
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden('You do not have permission to access this page.')
    return wrapper


def customer_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return wrapper
