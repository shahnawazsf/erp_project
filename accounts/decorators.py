from functools import wraps
from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from .permissions import has_submodule_permission


def module_access_required(view_name):
    """
    Dynamic permission decorator. Checks if user has access to this view.
    Uses database-configured permissions (can be changed via admin).
    Usage: @module_access_required('hr_employees')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            if has_submodule_permission(request.user, view_name):
                return view_func(request, *args, **kwargs)

            return HttpResponseForbidden('You do not have permission to access this page.')
        return wrapper
    return decorator


def role_required(*allowed_roles):
    """
    Static permission decorator (hardcoded roles).
    Use module_access_required() instead for dynamic permissions.
    Usage: @role_required('admin', 'manager')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            if hasattr(request.user, 'role') and request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)

            return HttpResponseForbidden('You do not have permission to access this page.')
        return wrapper
    return decorator
