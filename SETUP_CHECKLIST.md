# Role-Based Access Control - Setup Checklist

## Quick Start (5 minutes)

- [ ] **Step 1: Run migrations**
  ```bash
  python manage.py makemigrations accounts
  python manage.py migrate
  ```

- [ ] **Step 2: Seed modules & permissions**
  ```bash
  python manage.py setup_modules
  ```

- [ ] **Step 3: Start dev server**
  ```bash
  python manage.py runserver 9001
  ```

- [ ] **Step 4: Go to admin**
  - Navigate to `http://localhost:9001/admin/`
  - Login with admin account
  - Verify modules created under "Accounts" section

---

## What Gets Created

### Modules (5 default)
- ✓ Human Resources (hr)
- ✓ Inventory (inventory)
- ✓ Finance (finance)
- ✓ Sales (sales)
- ✓ Purchasing (purchasing)

### Sub-Modules (~18 total)
- HR: Employees, Departments, Leave Requests, Payroll
- Inventory: Products, Stock, Stock Movements, Warehouses
- Finance: Invoices, Expenses, Chart of Accounts, Reports
- Sales: Sales Orders, Customers
- Purchasing: Purchase Orders, Suppliers

### Default Role Permissions
- **admin** → All modules (view, edit, delete)
- **hr** → HR module (view, edit)
- **accountant** → Finance module (view, edit)
- **sales** → Sales module (view, edit)
- **purchasing** → Purchasing module (view, edit)
- **warehouse** → Inventory module (view, edit)
- **manager** → None (customize in admin)
- **employee** → None (customize in admin)

---

## Admin Interface Guide

### Page 1: Modules
**URL:** `/admin/accounts/module/`

Here you can:
- ✓ Add new modules
- ✓ Edit module labels and descriptions
- ✓ Add sub-modules (inline)
- ✓ Grant module-level permissions (inline)

### Page 2: Sub-Modules
**URL:** `/admin/accounts/submodule/`

Here you can:
- ✓ Edit sub-module names and view names
- ✓ Mark as active/inactive
- ✓ Reorder by changing "order" field

### Page 3: Module Permissions
**URL:** `/admin/accounts/modulepermission/`

**Purpose:** Control **module-level** access (view, edit, delete)

**Example:**
| Module | Role | View | Edit | Delete |
|--------|------|------|------|--------|
| Finance | accountant | ✓ | ✓ | ✗ |
| Finance | sales | ✗ | ✗ | ✗ |
| HR | hr | ✓ | ✓ | ✗ |

### Page 4: Sub-Module Permissions
**URL:** `/admin/accounts/submodulepermission/`

**Purpose:** Control **view-level** access

**Example:**
| Sub-Module | Role | Can Access |
|-----------|------|------------|
| Finance > Invoices | accountant | ✓ |
| Finance > Invoices | sales | ✗ |
| HR > Payroll | accountant | ✓ |

---

## Common Admin Tasks

### Task 1: Grant New User Access to Finance Module
1. Go `/admin/accounts/user/`
2. Edit user → Set role = "accountant"
3. Go `/admin/accounts/modulepermission/`
4. Find "Finance" → "accountant" row
5. If not exists: Click "+ Add" and create:
   - Module: Finance
   - Role: accountant
   - Can View: ✓
   - Can Edit: ✓
   - Can Delete: ✗
6. Save

**Done!** Accountant can now access Finance module.

### Task 2: Revoke Access from One View
1. Go `/admin/accounts/submodulepermission/`
2. Find "Finance > Invoices" for role "sales"
3. Uncheck "Can Access"
4. Save

**Instant!** Sales users can't see invoices anymore.

### Task 3: Add a New Module
1. Go `/admin/accounts/module/`
2. Click "+ Add Module"
3. Name: reporting
4. Label: Reporting
5. Description: Report generation and analytics
6. Icon: bi-file-text (optional)
7. Save

Then add sub-modules under it.

### Task 4: Change Default Role for New Employees
1. Go `/admin/accounts/modulepermission/`
2. Add new entries for "employee" role:
   - Module: Sales
   - Can View: ✓
   - Can Edit: ✗
   - Can Delete: ✗
3. Save

Now all new "employee" users can view Sales.

---

## Important Files

### Created
- `accounts/models.py` — Module, SubModule, ModulePermission, SubModulePermission
- `accounts/permissions.py` — Permission checking functions
- `accounts/decorators.py` — @module_access_required decorator
- `accounts/admin.py` — Admin interface configuration
- `accounts/templatetags/permissions.py` — Template filters
- `accounts/management/commands/setup_modules.py` — Seeding script
- `ROLE_BASED_ACCESS_GUIDE.md` — Full documentation

### Modified
- `accounts/oracle_auth.py` — Added role fetching from User model
- `accounts/models.py` — Added role field to OracleUser

---

## Verification Steps

### ✓ After Running `setup_modules`

```bash
python manage.py shell
```

```python
from accounts.models import Module, SubModule, ModulePermission

# Check modules exist
print(Module.objects.count())  # Should be 5
print(Module.objects.all().values_list('name', 'label'))

# Check sub-modules exist
print(SubModule.objects.count())  # Should be ~18
print(SubModule.objects.filter(module__name='hr'))

# Check permissions exist
print(ModulePermission.objects.count())  # Should be ~20
print(ModulePermission.objects.filter(role='hr'))
```

---

## Troubleshooting

### Q: Modules not showing in admin?
**A:** Run migrations first: `python manage.py migrate accounts`

### Q: setup_modules says "Module not found"?
**A:** Migrations didn't run. Run: `python manage.py migrate accounts`

### Q: After changing permissions, still has old access?
**A:** Clear cache:
```python
from accounts.permissions import clear_permission_cache
clear_permission_cache()
```

### Q: Can't find a view name?
**A:** Check your `urls.py`. The `view_name` must match the URL pattern name:
```python
# urls.py
path('employees/', views.employee_list, name='hr_employees'),  # ← use 'hr_employees'
```

---

## Next Steps

1. ✓ Run migrations
2. ✓ Run setup_modules
3. Go to `/admin/` and explore the new permission pages
4. Adjust default permissions as needed
5. (Optional) Apply `@module_access_required('view_name')` decorator to views
6. (Optional) Use permission filters in templates

---

**Questions?** See `ROLE_BASED_ACCESS_GUIDE.md` for detailed documentation.
