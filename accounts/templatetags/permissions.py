from django import template
from accounts.permissions import has_submodule_permission, has_module_permission

register = template.Library()


@register.filter
def has_submodule(user, view_name):
    """
    Template filter to check if user can access a view.
    Usage: {% if request.user|has_submodule:'hr_employees' %}
    """
    return has_submodule_permission(user, view_name)


@register.filter
def has_module(user, module_data):
    """
    Template filter to check module permission.
    Usage: {% if request.user|has_module:'hr:view' %}
    Format: 'module_name:action' where action is view/edit/delete
    """
    if ':' not in module_data:
        module_data = f"{module_data}:view"

    module_name, action = module_data.split(':')
    return has_module_permission(user, module_name, action)
