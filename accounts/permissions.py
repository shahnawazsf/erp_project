from django.core.cache import cache
from .models import ModulePermission, SubModulePermission


def has_module_permission(user, module_name, action='view'):
    """
    Check if user has permission to access a module.
    action: 'view', 'edit', 'delete'
    """
    if not user.is_authenticated:
        return False

    if user.role == 'admin':
        return True

    cache_key = f'module_perm_{module_name}_{user.role}_{action}'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        perm = ModulePermission.objects.get(module__name=module_name, role=user.role)
        result = False
        if action == 'view':
            result = perm.can_view
        elif action == 'edit':
            result = perm.can_edit
        elif action == 'delete':
            result = perm.can_delete

        cache.set(cache_key, result, 300)
        return result
    except ModulePermission.DoesNotExist:
        cache.set(cache_key, False, 300)
        return False


def has_submodule_permission(user, view_name):
    """
    Check if user has permission to access a specific sub-module/view.
    """
    if not user.is_authenticated:
        return False

    if user.role == 'admin':
        return True

    cache_key = f'submodule_perm_{view_name}_{user.role}'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        perm = SubModulePermission.objects.get(
            sub_module__view_name=view_name,
            role=user.role
        )
        result = perm.can_access
        cache.set(cache_key, result, 300)
        return result
    except SubModulePermission.DoesNotExist:
        cache.set(cache_key, False, 300)
        return False


def get_user_modules(user):
    """Get all modules accessible to user."""
    if not user.is_authenticated:
        return []

    if user.role == 'admin':
        from .models import Module
        return Module.objects.filter(is_active=True)

    return ModulePermission.objects.filter(
        role=user.role,
        can_view=True
    ).select_related('module').values_list('module', flat=True)


def get_module_submodules(user, module_name):
    """Get all sub-modules in a module that user can access."""
    if not user.is_authenticated:
        return []

    if user.role == 'admin':
        from .models import SubModule
        return SubModule.objects.filter(module__name=module_name, is_active=True)

    return SubModulePermission.objects.filter(
        sub_module__module__name=module_name,
        role=user.role,
        can_access=True
    ).select_related('sub_module').values_list('sub_module', flat=True)


def clear_permission_cache(user=None):
    """Clear permission cache for a user or all users."""
    if user:
        pattern = f'*_perm_*_{user.role}_*'
        cache.delete_many([key for key in cache.keys(pattern)])
    else:
        cache.delete_many([key for key in cache.keys('*_perm_*')])
