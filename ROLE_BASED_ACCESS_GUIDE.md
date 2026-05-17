# Role-Based Access Control Setup Guide

## Overview
This ERP system implements **dynamic, database-driven role-based access control**. Admins can grant/revoke module and page access from the Django admin interface without touching code.

## Architecture

### Models
- **Module** — Main modules (HR, Finance, Sales, etc.)
- **SubModule** — Pages/views within each module
- **ModulePermission** — Module-level access (view, edit, delete)
- **SubModulePermission** — View-level access (can_access)

### Permission Hierarchy
```
Admin Interface
    ↓
ModulePermission & SubModulePermission (Database)
    ↓
Permission checking functions (permissions.py)
    ↓
@module_access_required() decorator
    ↓
Protected views
```

---

## Setup Steps

### **Step 1: Run Migrations**
```bash
python manage.py makemigrations accounts
python manage.py migrate
```

### **Step 2: Seed Initial Modules**
```bash
python manage.py setup_modules
```

This creates all modules, sub-modules, and default permissions:
- ✓ HR, Finance, Sales, Purchasing, Inventory modules
- ✓ Sub-modules for each module
- ✓ Default role → module permissions
- ✓ Can edit directly in admin

### **Step 3: (Optional) Apply Decorators to Views**
Only needed if you want to enforce sub-module (view-level) access:

```python
# hr/views.py
from accounts.decorators import module_access_required

@module_access_required('hr_employees')
def employee_list(request):
    return render(request, 'hr/employee_list.html')
```

If you **only** use ModulePermission, decorators are optional.

---

## Admin Interface Usage

### **Manage Modules**
Go to `/admin/accounts/module/`

- Create/edit modules (HR, Finance, etc.)
- Add sub-modules inline
- Set order and icon
- Grant module-level permissions inline

### **Manage Sub-Modules**
Go to `/admin/accounts/submodule/`

- Assign to modules
- Enter Django view name (e.g., `hr_employees`)
- Toggle active/inactive

### **Grant Module Access**
Go to `/admin/accounts/modulepermission/`

Assign **view, edit, delete** permissions by role:

| Module | Role | Can View | Can Edit | Can Delete |
|--------|------|----------|----------|------------|
| HR | hr | ✓ | ✓ | ✗ |
| HR | accountant | ✗ | ✗ | ✗ |
| Finance | accountant | ✓ | ✓ | ✗ |

### **Grant View-Level Access**
Go to `/admin/accounts/submodulepermission/`

Assign access to specific pages:

| Sub-Module | Role | Can Access |
|-----------|------|------------|
| HR > Employees | hr | ✓ |
| HR > Payroll | accountant | ✗ |
| Finance > Invoices | accountant | ✓ |

---

## Default Permissions After Seeding

### Role Mapping
```
admin          → All modules (view, edit, delete)
hr             → HR (view, edit)
accountant     → Finance (view, edit)
sales          → Sales (view, edit)
purchasing     → Purchasing (view, edit)
warehouse      → Inventory (view, edit)
manager        → No default permissions (assign in admin)
employee       → No default permissions (assign in admin)
```

**Change these anytime in `/admin/accounts/modulepermission/`**

---

## Code Usage

### **Check Module Permission (in views)**
```python
from accounts.permissions import has_module_permission

def some_view(request):
    if not has_module_permission(request.user, 'hr', action='view'):
        return HttpResponseForbidden('No access')
    # ... rest of view
```

### **Check Sub-Module Permission**
```python
from accounts.permissions import has_submodule_permission

if has_submodule_permission(request.user, 'hr_employees'):
    # User can access this view
```

### **Get User's Accessible Modules (for navigation)**
```python
from accounts.permissions import get_user_modules

def sidebar(request):
    modules = get_user_modules(request.user)
    # Render only accessible modules
```

### **Template Usage**
```html
{% if request.user|has_submodule:'hr_employees' %}
    <a href="{% url 'hr_employees' %}">Employees</a>
{% endif %}
```

---

## Common Tasks

### **Grant a User Access to a Module**

1. Go `/admin/accounts/modulepermission/`
2. Click "+ Add Module Permission"
3. Select module (e.g., Finance)
4. Select role (e.g., accountant)
5. Check: Can View ✓ Can Edit ✓ Can Delete ✗
6. Save

**That's it!** All users with role `accountant` now have Finance access.

### **Revoke View-Level Access**

1. Go `/admin/accounts/submodulepermission/`
2. Find the row (e.g., Finance > Invoices, accountant)
3. Uncheck "Can Access"
4. Save

**Instant!** No code changes, no server restart.

### **Add a New Sub-Module**

1. Go `/admin/accounts/submodule/`
2. Click "+ Add Sub Module"
3. Module: Finance
4. Name: reports_hub
5. Label: Reports Hub
6. View Name: **finance_reports** (must match your Django view URL name)
7. Save

Then grant access in `/admin/accounts/submodulepermission/`

---

## Permission Caching

Permissions are **cached for 5 minutes** for performance. If you change permissions and want instant effect:

### **Clear Cache Programmatically**
```python
from accounts.permissions import clear_permission_cache

# Clear all permissions
clear_permission_cache()

# Clear for specific user
clear_permission_cache(request.user)
```

The admin interface **automatically clears cache** on save.

---

## Files Created

```
accounts/
  ├── models.py          (Module, SubModule, ModulePermission, SubModulePermission)
  ├── permissions.py     (has_module_permission, has_submodule_permission, etc.)
  ├── decorators.py      (@module_access_required decorator)
  ├── admin.py           (Admin interface configuration)
  ├── oracle_auth.py     (Updated with role support)
  └── management/
      └── commands/
          └── setup_modules.py  (Seed initial data)
```

---

## Troubleshooting

### **Permissions not taking effect?**
- Clear cache: `python manage.py shell`
  ```python
  from accounts.permissions import clear_permission_cache
  clear_permission_cache()
  ```

### **User can't access view despite permission being set?**
1. Verify SubModulePermission exists for that view
2. Check `view_name` matches Django URL name (e.g., `'hr_employees'`)
3. Check user's role matches the permission entry

### **Module shows in admin but not in app?**
- Make sure `is_active=True` in Module and SubModule

---

## Next Steps

1. Run migrations
2. Run `setup_modules` command
3. Go to `/admin/accounts/modulepermission/` and verify default roles
4. Go to `/admin/accounts/submodulepermission/` and adjust view-level access as needed
5. (Optional) Apply `@module_access_required` decorators to enforce sub-module access
