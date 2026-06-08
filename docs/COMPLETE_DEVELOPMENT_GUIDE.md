# Complete ERP Development Guide - From Scratch

**Author:** Claude Code Assistant  
**Date:** May 2026  
**Version:** 1.0  
**Audience:** Beginners with Django knowledge

---

## Table of Contents

1. [Project Setup](#1-project-setup)
2. [Running the Application](#2-running-the-application)
3. [Database Configuration](#3-database-configuration)
4. [Authentication System](#4-authentication-system)
5. [Role-Based Access Control](#5-role-based-access-control)
6. [Module Management](#6-module-management)
7. [Container Notification Feature](#7-container-notification-feature)
8. [Recent Updates (June 2026)](#recent-updates-june-2026)
9. [Common Issues & Fixes](#8-common-issues--fixes)

---

## Recent Updates (June 2026)

### June 8: Operations Module - Work Orders & Maintenance Management

#### 1. New Operations Module Created
**Files:** 
- `operations/models.py` — WorkOrder, Maintenance, OperationalMetric models
- `operations/views.py` — Dashboard, list views
- `operations/urls.py` — URL routing
- `operations/templates/` — Dashboard and list templates
- `operations/admin.py` — Django admin interface

**Changes:**
- Added complete Operations module for managing work orders, equipment maintenance, and operational metrics
- Three core models:
  1. **WorkOrder** — Track tasks with status, priority, assignments (statuses: draft, scheduled, in_progress, completed, cancelled)
  2. **Maintenance** — Log equipment maintenance (types: preventive, corrective, predictive)
  3. **OperationalMetric** — Record KPIs and measurements

**Features:**
- Operations Dashboard at `/operations/` with key metrics (total orders, active orders, maintenance status, maintenance costs)
- Work Orders list at `/operations/work-orders/` with detailed table view
- Maintenance list at `/operations/maintenance/` with equipment tracking
- Full Django admin interface for all models with filters and search
- Integration with main ERP settings and URL routing

**Models Database Tables:**
```sql
-- WORK_ORDERS: Track operational work
-- MAINTENANCE: Equipment maintenance tracking
-- OPERATIONAL_METRICS: KPIs and measurements
```

**Dashboard Metrics Displayed:**
- Total Work Orders count
- Active Work Orders (scheduled + in_progress)
- Completed Work Orders
- Pending Maintenance count
- Total Maintenance Cost (completed maintenance only)
- Recent work orders and maintenance records

**Technical Details:**
- Models use string primary keys (UUID format) matching existing ERP pattern
- All views require `@login_required` decorator
- Dashboard uses safe query pattern with exception handling
- Templates follow Bootstrap 5 card layout (same as main dashboard)
- Admin interface includes list filters, search, and read-only fields

**Configuration Changes:**
- Added `'operations'` to `INSTALLED_APPS` in settings.py
- Added `/operations/` path to main `urls.py` routing

**Related Documentation:**
See [OPERATIONS_MODULE_GUIDE.md](OPERATIONS_MODULE_GUIDE.md) for complete module documentation, database schema, usage examples, and integration points.

---

### June 3: Customer Invoice Report & UI Enhancements

#### 1. Customer Invoice Report Query Refactored
**File:** `finance/views.py` (lines 235-254), `templates/finance/report_customer_invoice.html`

**Changes:**
- Migrated from `Custom_report` table to `INV_WEEKLY_REPORT_VIEW` with BOL lookup
- Added LEFT JOIN to `INV_WEEKLY_REPORT_BL_VIEW` to fetch associated BOL numbers
- Fixed date filtering issue: Converted DD/MM/YYYY string comparison to YYYY-MM-DD format
- Report now displays two BOLNUMBER columns: one from invoice, one from BOL view

**Technical Detail - Date Filtering:**
The view returns INV_DATE as VARCHAR 'dd/mm/yyyy', which doesn't sort correctly with string comparison. Solution: Use SUBSTR to convert to YYYY-MM-DD format before comparison.

```python
# Python: Convert form dates (YYYY-MM-DD) to DD/MM/YYYY for Oracle
d1 = datetime.strptime(filters['date_from'], '%Y-%m-%d').strftime('%d/%m/%Y')

# Oracle: Convert view dates back to YYYY-MM-DD for proper string comparison
SUBSTR(a.INV_DATE, 7, 4) || '-' || SUBSTR(a.INV_DATE, 4, 2) || '-' || SUBSTR(a.INV_DATE, 1, 2)
```

#### 2. Global Page Loader - Content Area Only
**File:** `templates/base.html` (CSS and HTML structure)

**Changes:**
- Redesigned page loader from full-viewport (`position: fixed`) to content-area only (`position: absolute`)
- Loader now appears within main-content area, keeping sidebar and topbar visible and interactive
- Positioned 58px from top (below topbar height) and spans full width/height of content
- Automatically shows on all navigation links and form submissions
- Supports smooth transitions with backdrop blur effect

**Why This Matters:**
Users can now navigate and use the sidebar while content is loading, improving UX significantly.

#### 3. Login Page Rebranding to "Reporting Tool"
**File:** `templates/accounts/login.html`

**Changes:**
- Brand title: "ERP System" → "Reporting Tool"
- Subtitle: "Enterprise Resource Planning" → "Analytics & Reporting Platform"
- **Removed:** Module feature list (HR, Inventory, Sales, Finance sections)
- Footer: Updated copyright to "Reporting Tool"

**Result:** Cleaner, more focused branding that reflects the reporting-centric purpose of the system.

---

### June 4: Phase 1 Header/Footer Features & Production Deployment

#### 1. Global Search Bar (Header)
**File:** `templates/base.html` (lines 359-365 HTML, 84-117 CSS, 497-538 JS)

**Features:**
- Search input in topbar left section (320px width)
- Debounced search with 300ms delay to prevent excessive calls
- Dropdown results showing matching reports and navigation items
- Currently shows mock data: Customer Invoice, VAT Report, Dashboard, Reports
- Click result to navigate directly to that page
- Auto-closes when clicking outside

**Current Implementation:**
Mock JavaScript-based search with hardcoded results. Ready to connect to real API endpoint.

**To Enhance:**
```python
# Add to finance/views.py or core/views.py
@login_required
@require_GET
def api_search(request):
    query = request.GET.get('q', '')
    results = {
        'reports': [...],
        'invoices': [...],
    }
    return JsonResponse(results)
```

#### 2. Settings Dropdown (Header)
**File:** `templates/base.html` (lines 368-385 HTML, 119-156 CSS, 540-565 JS)

**Features:**
- Gear icon in topbar right section (before logout)
- Menu with settings options:
  - Date Format (DD/MM/YYYY)
  - Theme (Light Mode)
  - Timezone (UTC)
  - Help & Documentation
- Toggle open/close on click
- Auto-closes when clicking outside

**Current Implementation:**
Menu items are stubs that log to console. Ready to implement actual preferences.

**To Enhance:**
Create UserPreferences model and settings save endpoint:
```python
class UserPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_format = models.CharField(choices=[('DD/MM/YYYY', 'DD/MM/YYYY'), ...])
    theme = models.CharField(choices=[('light', 'Light'), ('dark', 'Dark')])
    timezone = models.CharField(default='UTC')
```

#### 3. Footer with Copyright
**File:** `templates/base.html` (lines 429-434 HTML, 158-194 CSS)

**Features:**
- Simple footer at bottom of all authenticated pages
- Copyright text: "© 2026 SDES Reporting Tool. All rights reserved."
- Uses flexbox layout to automatically push to bottom
- Minimal, clean design

**Layout Strategy:**
```css
.main-content { 
    display: flex; 
    flex-direction: column; 
    min-height: 100vh; 
}
.content-area { flex: 1; }
/* footer naturally appears at bottom */
```

**Note:** Quick Links section intentionally removed per user request.

#### 4. Production Deployment with Waitress
**Changes:**
- Migrated from Django development server to Waitress (production WSGI)
- Collected static files to `staticfiles/` directory
- WhiteNoiseMiddleware already configured for efficient static serving
- Server now binds to 0.0.0.0:9001 (accessible from network)

**Startup Command:**
```bash
python manage.py collectstatic --noinput
python -m waitress --port=9001 --host=0.0.0.0 erp_project.wsgi:application
```

**Network Access:**
- Local: http://localhost:9001
- Network: http://172.16.2.3:9001

**Why Waitress?**
- Pure Python WSGI server (no C extensions needed)
- Windows-compatible
- Production-ready
- Thread-safe and efficient

---

## 1. Project Setup

### 1.1 Initial Project Creation

**What is this?**
Setting up a new Django project for an ERP system that connects to an Oracle database.

**Prerequisites:**
- Python 3.8+ installed
- pip package manager
- Oracle Database access

**Step 1: Create Virtual Environment**

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

**Why?** Virtual environments isolate project dependencies so they don't conflict with system packages.

---

**Step 2: Install Dependencies**

```bash
pip install \
  django==6.0.5 \
  djangorestframework \
  pillow \
  django-crispy-forms \
  crispy-bootstrap5 \
  django-widget-tweaks \
  oracledb \
  whitenoise
```

**What each package does:**
- `django` - Web framework
- `djangorestframework` - REST API support
- `pillow` - Image processing
- `crispy-forms` - Better form rendering
- `oracledb` - Oracle database driver
- `whitenoise` - Static files management

---

**Step 3: Create Django Project**

```bash
django-admin startproject erp_project .
django-admin startapp accounts
django-admin startapp core
django-admin startapp finance
```

**Directory structure created:**
```
erp_project/
├── manage.py
├── erp_project/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── core/
├── finance/
└── venv/
```

---

## 2. Running the Application

### 2.1 Localhost Only

**What is this?**
Running the development server on your local machine. This is the default configuration.

**Step 1: Basic Localhost Server**

```bash
# Activate virtual environment (if not already active)
venv\Scripts\activate

# Start the dev server (port 9001 is used to avoid conflicts with Hyper-V)
python manage.py runserver 9001
```

**Access:**
- http://localhost:9001
- http://127.0.0.1:9001

**How it works:**
- Server binds to `127.0.0.1:9001` (localhost only)
- Not accessible from other machines
- Best for isolated development

---

### 2.2 LAN Access (Network-Wide)

**What is this?**
Making the application accessible from other computers on your network. Useful for team testing or demos.

**Prerequisites:**
- Know your machine's LAN IP address
- Both machines must be on the same network
- Firewall must allow port 9001

**Step 1: Find Your LAN IP Address**

**On Windows (PowerShell):**
```powershell
ipconfig | Select-String -Pattern 'IPv4 Address'
```

Look for output like:
```
   IPv4 Address. . . . . . . . . . . : 172.16.2.3
```

**On Mac/Linux:**
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

---

**Step 2: Update Django Settings**

Edit `erp_project/settings.py` and add your LAN IP to `CSRF_TRUSTED_ORIGINS`:

```python
# Current setting
CSRF_TRUSTED_ORIGINS = ['http://localhost:9001', 'http://127.0.0.1:9001']

# Add your LAN IP (example: 172.16.2.3)
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:9001',
    'http://127.0.0.1:9001',
    'http://172.16.2.3:9001'  # Replace with your actual IP
]
```

**Why?** Django blocks form submissions from untrusted origins for security. Your LAN IP needs to be explicitly trusted.

---

**Step 3: Start Server on All Interfaces**

```bash
# Activate virtual environment
venv\Scripts\activate

# Start on 0.0.0.0:9001 (listens on all network interfaces)
python manage.py runserver 0.0.0.0:9001
```

**Important:** `0.0.0.0:9001` binds to all network interfaces, including LAN.

---

**Step 4: Access from Another Machine**

From any computer on your network:

```
http://172.16.2.3:9001
```

Replace `172.16.2.3` with your actual IP address from Step 1.

---

### 2.3 Quick Reference

**Summary Table:**

| Scenario | Command | Access From |
|----------|---------|-------------|
| **Local only** | `python manage.py runserver 9001` | localhost, 127.0.0.1 |
| **LAN access** | `python manage.py runserver 0.0.0.0:9001` | localhost, 127.0.0.1, LAN IP |

**Settings Update Checklist:**
- [ ] `ALLOWED_HOSTS = ['*']` (already set for LAN)
- [ ] `CSRF_TRUSTED_ORIGINS` includes your LAN IP
- [ ] Firewall allows port 9001
- [ ] Server started with `0.0.0.0:9001`

---

### 2.4 Troubleshooting Access Issues

**Can't connect from another machine?**

1. **Verify server is running:**
   ```bash
   netstat -an | findstr 9001  # Windows
   ```

2. **Check firewall (Windows):**
   - Go to Windows Defender Firewall → Allow an app through
   - Add Python.exe for port 9001
   - Or disable firewall temporarily for testing

3. **Test connectivity:**
   ```bash
   # From the other machine
   ping 172.16.2.3
   ```

4. **Wrong IP in URL?**
   - Always use the IP from `ipconfig | Select-String 'IPv4 Address'`
   - Never use 127.0.0.1 or localhost from another machine

---

## 3. Database Configuration

### 2.1 Oracle Database Connection

**What is this?**
Configuring Django to connect to an Oracle database instead of the default SQLite.

**Step 1: Update settings.py**

```python
# erp_project/settings.py

import os
import oracledb
from pathlib import Path

# Load environment variables from .env file
_env_path = Path(__file__).resolve().parent.parent / '.env'
if _env_path.exists():
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith('#') and '=' in _line:
                _key, _val = _line.split('=', 1)
                os.environ.setdefault(_key.strip(), _val.strip())

# Enable Oracle thick mode (requires Oracle Instant Client)
ORACLE_CLIENT_DIR = os.environ.get('ORACLE_CLIENT_DIR', None)
if ORACLE_CLIENT_DIR:
    oracledb.init_oracle_client(lib_dir=ORACLE_CLIENT_DIR)

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'erp_project.oracle_compat',  # Custom backend for Oracle 12c
        'NAME': os.environ.get('ORACLE_DB_NAME', 'ORCL'),
        'USER': os.environ.get('ORACLE_DB_USER', 'erp_user'),
        'PASSWORD': os.environ.get('ORACLE_DB_PASSWORD', ''),
        'HOST': os.environ.get('ORACLE_DB_HOST', 'localhost'),
        'PORT': os.environ.get('ORACLE_DB_PORT', '1521'),
    }
}
```

**Why customize the backend?**
Oracle 12c is older than Django's minimum version requirement. A custom backend allows us to use it anyway.

---

**Step 2: Create Custom Oracle Backend**

```python
# erp_project/oracle_compat/base.py

from django.db.backends.oracle.base import DatabaseWrapper as OracleWrapper

class DatabaseWrapper(OracleWrapper):
    """
    Custom Oracle backend that supports Oracle 12.2
    Django normally requires Oracle 21c+
    """
    
    @staticmethod
    def _get_varchar2_max_length():
        """Allow VARCHAR2 fields"""
        return 2000
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Lower minimum version to 12.2
        self.minimum_database_version = (12, 2)
```

**Why this matters?**
Without this, Django will reject Oracle 12c as "too old." This override bypasses that check.

---

**Step 3: Create .env File**

```env
# .env - Keep this file secret (add to .gitignore)

ORACLE_DB_NAME=SDESDB
ORACLE_DB_USER=sdeserp
ORACLE_DB_PASSWORD=your_password_here
ORACLE_DB_HOST=172.16.1.12
ORACLE_DB_PORT=1521
ORACLE_CLIENT_DIR=C:\oracle\instantclient_21_9
```

**Why use environment variables?**
- Never hardcode passwords in code
- Easy to change between dev/staging/production
- Safer for version control

---

## 3. Authentication System

### 3.1 Understanding the Dual Authentication Paths

**Why two systems?**
- **Main App**: Uses Oracle procedure (existing system)
- **Admin Panel**: Uses Django User model (our system)

```
┌─────────────────────────────────┐
│  User Tries to Login            │
└────────────┬────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
/accounts/       /admin/
login/           
    │                 │
    ▼                 ▼
Oracle Proc     Django User
(GET_USER_DETAIL) (accounts_user)
    │                 │
    ▼                 ▼
Session          Session
(oracle_user)    (User model)
```

---

### 3.2 Oracle-Based Authentication

**Step 1: Create oracle_auth.py**

```python
# accounts/oracle_auth.py

import logging
import oracledb
from django.db import connection

logger = logging.getLogger(__name__)
SESSION_KEY = 'oracle_user'

def call_get_user_detail(username, password):
    """
    Call Oracle procedure: GET_USER_DETAIL
    
    Parameters:
    - P_USER_ID (IN): Username
    - P_PASSWORD (IN): Password
    - P_USER_NAME (OUT): Full name
    - P_USER_GRP_ID (OUT): Group ID
    - P_USER_EMP_CODE (OUT): Employee code
    - P_USER_DESC (OUT): Description
    - P_STATUS (OUT): 'TRUE' if login succeeds
    
    Returns: Dict with user data or None if failed
    """
    
    with connection.cursor() as django_cur:
        # Get raw oracledb cursor (needed for .var() and .callproc())
        cur = django_cur.cursor.cursor
        
        # Create output variables
        p_user_name = cur.var(oracledb.STRING)
        p_user_grp_id = cur.var(oracledb.STRING)
        p_user_emp_code = cur.var(oracledb.STRING)
        p_user_desc = cur.var(oracledb.STRING)
        p_status = cur.var(oracledb.STRING)
        
        # Call the Oracle procedure
        cur.callproc('SDESERP.GET_USER_DETAIL', [
            username, password,
            p_user_name, p_user_grp_id, p_user_emp_code,
            p_user_desc, p_status,
        ])
        
        # Check if login was successful
        status = p_status.getvalue()
        if status != 'TRUE':
            logger.warning('Login failed for %s', username)
            return None
        
        # Fetch user role from LOGIN_USER table
        user_data = {
            'username': username,
            'user_name': p_user_name.getvalue() or '',
            'user_grp_id': p_user_grp_id.getvalue() or '',
            'user_emp_code': p_user_emp_code.getvalue() or '',
            'user_desc': p_user_desc.getvalue() or '',
            'role': 'employee',  # default
        }
        
        # Query user role from LOGIN_USER table
        try:
            cur.execute(
                "SELECT USER_ROLE FROM LOGIN_USER WHERE USER_ID = :uid",
                {'uid': username}
            )
            result = cur.fetchone()
            if result:
                oracle_role = result[0]
                if oracle_role:
                    # Map Oracle roles to permission system
                    role_mapping = {
                        'A': 'admin',
                        'U': 'employee',
                    }
                    oracle_role = oracle_role.strip().upper()
                    user_data['role'] = role_mapping.get(oracle_role, 'employee')
        except Exception as e:
            logger.warning('Failed to fetch role: %s', e)
        
        return user_data


class OracleUser:
    """
    Lightweight user object (NOT a Django model)
    Represents an authenticated user from Oracle
    """
    is_anonymous = False
    is_authenticated = True
    
    def __init__(self, data):
        self.username = data['username']
        self.user_name = data.get('user_name', '')
        self.user_grp_id = data.get('user_grp_id', '')
        self.user_emp_code = data.get('user_emp_code', '')
        self.user_desc = data.get('user_desc', '')
        self.role = data.get('role', 'employee')
    
    def get_full_name(self):
        return self.user_name
    
    def has_role(self, *roles):
        return self.role in roles
    
    def __str__(self):
        return self.username
```

**Key Concepts:**
1. **Two-level cursor access**: Django wraps the Oracle cursor, so we unwrap it with `.cursor.cursor`
2. **Output variables**: Oracle needs `.var()` to capture procedure outputs
3. **Role mapping**: Oracle roles ('A', 'U') → Permission system roles ('admin', 'employee')
4. **Not a Django model**: `OracleUser` is plain Python, faster and simpler

---

**Step 2: Create Login View**

```python
# accounts/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .oracle_auth import SESSION_KEY, call_get_user_detail

@login_required
def login_view(request):
    """Handle user login via Oracle"""
    
    # If already logged in, go to dashboard
    if request.session.get(SESSION_KEY):
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        try:
            # Authenticate with Oracle
            info = call_get_user_detail(username, password)
        except Exception as e:
            logger.exception('Oracle auth error')
            info = None
        
        if info:
            # Store user data in session
            request.session[SESSION_KEY] = info
            return redirect(request.GET.get('next', 'dashboard'))
        
        messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/login.html')


def logout_view(request):
    """Clear session and logout"""
    request.session.flush()
    return redirect('login')
```

**Flow Explanation:**
1. User submits username/password
2. Call Oracle procedure to validate
3. If valid, store user dict in session
4. Middleware converts session data to `OracleUser` object
5. Now `request.user` has the user data available

---

**Step 3: Create Middleware**

```python
# accounts/middleware.py

from .oracle_auth import OracleUser, SESSION_KEY

class OracleAuthMiddleware:
    """
    Convert session['oracle_user'] dict → OracleUser object
    Makes request.user available in all views
    
    Must be placed AFTER AuthenticationMiddleware
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check if user data in session
        data = request.session.get(SESSION_KEY)
        
        if data:
            # Convert dict to OracleUser object
            request.user = OracleUser(data)
        
        return self.get_response(request)
```

**Why middleware?**
- Runs on every request
- Sets `request.user` early so views/templates can access it
- Works with `@login_required` decorator
- Satisfies `is_authenticated = True` check

---

### 3.3 Django Admin Authentication

**Step 1: Create Django User Model**

```python
# accounts/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """Extended Django User model"""
    
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('hr', 'HR'),
        ('accountant', 'Accountant'),
        ('sales', 'Sales'),
        ('purchasing', 'Purchasing'),
        ('warehouse', 'Warehouse'),
        ('employee', 'Employee'),
    ]
    
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='employee'
    )
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

# Update settings.py
AUTH_USER_MODEL = 'accounts.User'
```

**Why extend AbstractUser?**
- Keep all Django User features
- Add our custom fields (role, phone, avatar)
- Still works with Django admin, permissions, auth decorators

---

**Step 2: Create Django Admin User**

```bash
# One-time setup
python manage.py shell
```

```python
from accounts.models import User

user = User.objects.create_user(
    username='sfaridi',
    email='shahnawazsf@gmail.com',
    password='admin123',
    role='admin',
    is_staff=True,
    is_superuser=True
)
```

**What each flag means:**
- `is_staff=True` - Can access `/admin/`
- `is_superuser=True` - Full admin access

---

## 4. Role-Based Access Control

### 4.1 Permission Models

**What is this?**
Dynamic permission system where admins assign module/view access via Django admin.

**Step 1: Create Permission Models**

```python
# accounts/models.py (add to existing)

class Module(models.Model):
    """Main modules: HR, Finance, Sales, etc."""
    
    name = models.CharField(max_length=100, unique=True)  # 'hr', 'finance'
    label = models.CharField(max_length=100)  # 'Human Resources'
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # 'bi-people'
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'label']
    
    def __str__(self):
        return self.label


class SubModule(models.Model):
    """Pages/views within a module"""
    
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    label = models.CharField(max_length=100)  # 'Employees'
    view_name = models.CharField(max_length=100)  # 'hr_employees' (Django URL name)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['module', 'order']
        unique_together = ('module', 'name')
    
    def __str__(self):
        return f"{self.module.label} > {self.label}"


class ModulePermission(models.Model):
    """Who can access what module (view, edit, delete)"""
    
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=20, 
        choices=User.ROLE_CHOICES
    )
    can_view = models.BooleanField(default=True)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('module', 'role')
    
    def __str__(self):
        return f"{self.module.label} - {self.get_role_display()}"


class SubModulePermission(models.Model):
    """Who can access what specific view"""
    
    sub_module = models.ForeignKey(SubModule, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=20, 
        choices=User.ROLE_CHOICES
    )
    can_access = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('sub_module', 'role')
    
    def __str__(self):
        return f"{self.sub_module} - {self.get_role_display()}"
```

**Database schema created:**
```
Module (1) ──────────────────┬─ (Many) ModulePermission
                             │
         (1) ─────────────────┬─ (Many) SubModule
         SubModule (1) ───────┴─ (Many) SubModulePermission
```

---

### 4.2 Permission Checking System

**Step 1: Create permissions.py**

```python
# accounts/permissions.py

from django.core.cache import cache
from .models import ModulePermission, SubModulePermission

def has_module_permission(user, module_name, action='view'):
    """
    Check if user can access a module
    
    Args:
        user: OracleUser or Django User
        module_name: 'hr', 'finance', etc.
        action: 'view', 'edit', 'delete'
    
    Returns: Boolean
    """
    
    # Admins always have access
    if user.role == 'admin':
        return True
    
    # Check cache first (5 min TTL)
    cache_key = f'module_perm_{module_name}_{user.role}_{action}'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    
    try:
        # Query database
        perm = ModulePermission.objects.get(
            module__name=module_name, 
            role=user.role
        )
        
        # Check specific action
        if action == 'view':
            result = perm.can_view
        elif action == 'edit':
            result = perm.can_edit
        elif action == 'delete':
            result = perm.can_delete
        else:
            result = False
        
        # Cache the result
        cache.set(cache_key, result, 300)
        return result
        
    except ModulePermission.DoesNotExist:
        cache.set(cache_key, False, 300)
        return False


def has_submodule_permission(user, view_name):
    """Check if user can access a specific view"""
    
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


def clear_permission_cache(user=None):
    """Clear permission cache when permissions change"""
    if user:
        # Clear just this user's permissions
        pattern = f'*_perm_*_{user.role}_*'
        cache.delete_many([key for key in cache.keys(pattern)])
    else:
        # Clear all permissions
        cache.delete_many([key for key in cache.keys('*_perm_*')])
```

**Why caching?**
- Permission checks happen on every request
- Database queries are slow
- 5-minute cache is reasonable for ERP system
- Admin panel auto-clears cache on changes

---

### 4.3 Decorators

**Step 1: Create decorators.py**

```python
# accounts/decorators.py

from functools import wraps
from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from .permissions import has_submodule_permission

def module_access_required(view_name):
    """
    Protect a view with permission check
    
    Usage:
        @module_access_required('hr_employees')
        def employee_list(request):
            ...
    
    The view_name must match Django URL name
    """
    
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Must be logged in
            if not request.user.is_authenticated:
                return redirect('login')
            
            # Check permission
            if has_submodule_permission(request.user, view_name):
                return view_func(request, *args, **kwargs)
            
            # Permission denied
            return HttpResponseForbidden(
                'You do not have permission to access this page.'
            )
        
        return wrapper
    return decorator
```

---

### 4.4 Admin Interface Configuration

**Step 1: Register Models in Admin**

```python
# accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Module, SubModule, ModulePermission, SubModulePermission
from .permissions import clear_permission_cache


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('ERP Info', {'fields': ('role', 'phone', 'avatar')}),
    )


class SubModuleInline(admin.TabularInline):
    """Allow adding sub-modules while editing a module"""
    model = SubModule
    extra = 1
    fields = ('name', 'label', 'view_name', 'is_active')


class ModulePermissionInline(admin.TabularInline):
    model = ModulePermission
    extra = 1
    fields = ('role', 'can_view', 'can_edit', 'can_delete')


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('label', 'name', 'is_active', 'order')
    inlines = [SubModuleInline, ModulePermissionInline]
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        clear_permission_cache()  # Clear cache on save


@admin.register(ModulePermission)
class ModulePermissionAdmin(admin.ModelAdmin):
    list_display = ('module', 'role', 'can_view', 'can_edit', 'can_delete')
    list_filter = ('module', 'role')
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        clear_permission_cache()
```

---

### 4.5 Management Command to Seed Data

**Step 1: Create setup_modules.py**

```python
# accounts/management/commands/setup_modules.py

from django.core.management.base import BaseCommand
from accounts.models import Module, SubModule, ModulePermission

class Command(BaseCommand):
    help = 'Setup initial modules and permissions'
    
    def handle(self, *args, **options):
        modules_data = {
            'hr': {
                'label': 'Human Resources',
                'order': 1,
                'sub_modules': [
                    {'name': 'employees', 'label': 'Employees', 'view_name': 'hr_employees'},
                    {'name': 'leaves', 'label': 'Leave Requests', 'view_name': 'hr_leaves'},
                ]
            },
            'finance': {
                'label': 'Finance',
                'order': 2,
                'sub_modules': [
                    {'name': 'invoices', 'label': 'Invoices', 'view_name': 'finance_invoices'},
                ]
            },
        }
        
        for module_name, module_info in modules_data.items():
            # Create module
            module, created = Module.objects.get_or_create(
                name=module_name,
                defaults={'label': module_info['label'], 'order': module_info['order']}
            )
            self.stdout.write(f"Module: {module.label}")
            
            # Create sub-modules
            for sub_info in module_info['sub_modules']:
                SubModule.objects.get_or_create(
                    module=module,
                    name=sub_info['name'],
                    defaults={
                        'label': sub_info['label'],
                        'view_name': sub_info['view_name'],
                    }
                )
        
        # Create default permissions
        role_permissions = {
            'admin': {'can_view': True, 'can_edit': True, 'can_delete': True},
            'hr': {'can_view': True, 'can_edit': True, 'can_delete': False},
        }
        
        for module in Module.objects.all():
            for role, perms in role_permissions.items():
                ModulePermission.objects.get_or_create(
                    module=module,
                    role=role,
                    defaults=perms
                )
        
        self.stdout.write(self.style.SUCCESS('✓ Setup complete!'))
```

**Run it:**
```bash
python manage.py setup_modules
```

---

## 5. Module Management

### 5.1 Creating Module Apps

**Structure:**
```
hr/
├── models.py
├── views.py
├── urls.py
├── forms.py
└── templates/hr/
    └── employee_list.html
```

**Step 1: Define Models**

```python
# hr/models.py

from django.db import models

class Employee(models.Model):
    user = models.OneToOneField('accounts.User', on_delete=models.SET_NULL, null=True)
    emp_code = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    status = models.CharField(
        max_length=20,
        choices=[('active', 'Active'), ('inactive', 'Inactive')],
        default='active'
    )
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
```

---

**Step 2: Create Views with Permission Check**

```python
# hr/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.decorators import module_access_required
from .models import Employee

@module_access_required('hr_employees')
def employee_list(request):
    """List all employees (permission checked by decorator)"""
    employees = Employee.objects.filter(status='active')
    return render(request, 'hr/employee_list.html', {
        'employees': employees
    })
```

---

**Step 3: Configure URLs**

```python
# hr/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('employees/', views.employee_list, name='hr_employees'),
]

# erp_project/urls.py
from django.urls import path, include

urlpatterns = [
    path('hr/', include('hr.urls')),
    path('finance/', include('finance.urls')),
]
```

---

## 6. Container Notification Feature

### 6.1 Model Setup

```python
# finance/models.py

from django.db import models

class ContainerNotification(models.Model):
    crn_container_no = models.CharField(
        max_length=30, 
        primary_key=True,
        db_column='CRN_CONTAINER_NO'
    )
    crn_status = models.IntegerField(
        default=0,
        db_column='CRN_STATUS'
        # 0 = Pending, 9 = Received
    )
    
    class Meta:
        db_table = 'CNT_RECVD_NOTIFICATION'
        managed = False  # Don't migrate this table
    
    def __str__(self):
        return self.crn_container_no
    
    def get_status_display(self):
        """Display status as text"""
        status_map = {0: 'Pending', 9: 'Received'}
        return status_map.get(self.crn_status, 'Unknown')
```

---

### 6.2 Form and Views

```python
# finance/forms.py

from django import forms
from .models import ContainerNotification

class ContainerNotificationForm(forms.ModelForm):
    class Meta:
        model = ContainerNotification
        fields = ['crn_container_no']
        labels = {'crn_container_no': 'Container No'}
        widgets = {
            'crn_container_no': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'e.g., CNT-TCKU1234567',
                'style': 'text-transform:uppercase;',
            })
        }
    
    def clean_crn_container_no(self):
        return self.cleaned_data.get('crn_container_no', '').upper()


# finance/views.py

from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from accounts.decorators import module_access_required
from .models import ContainerNotification
from .forms import ContainerNotificationForm

@module_access_required('cn_list')
def cn_list(request):
    """List container notifications, sorted by pending first"""
    qs = ContainerNotification.objects.exclude(
        crn_container_no=''
    ).order_by('crn_status', 'crn_container_no')
    
    return render(request, 'finance/cn_list.html', {'rows': qs})

@module_access_required('cn_create')
def cn_create(request):
    """Add new container notification"""
    if request.method == 'POST':
        form = ContainerNotificationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Container notification added.')
            return redirect('cn_list')
    else:
        form = ContainerNotificationForm()
    
    return render(request, 'finance/cn_form.html', {
        'form': form,
        'action': 'Add'
    })
```

---

### 6.3 List Template with Status Column

```html
<!-- templates/finance/cn_list.html -->

{% extends 'base.html' %}

{% block extra_css %}
<style>
    .status-pending {
        background: #fff3cd;
        color: #856404;
        padding: 0.35em 0.65em;
        border-radius: 50px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .status-received {
        background: #d4edda;
        color: #155724;
        padding: 0.35em 0.65em;
        border-radius: 50px;
        font-size: 0.75rem;
        font-weight: 600;
    }
</style>
{% endblock %}

{% block content %}

<div class="page-header">
    <h4>Container Notification</h4>
    <a href="{% url 'cn_create' %}" class="btn btn-primary btn-sm">
        <i class="bi bi-plus-lg"></i> Add Record
    </a>
</div>

<table class="table">
    <thead>
        <tr>
            <th>#</th>
            <th>Container No</th>
            <th>Status</th>
            <th>Action</th>
        </tr>
    </thead>
    <tbody>
        {% for row in rows %}
        <tr>
            <td>{{ forloop.counter }}</td>
            <td>{{ row.crn_container_no }}</td>
            <td>
                {% if row.crn_status == 0 %}
                    <span class="status-pending">
                        <i class="bi bi-hourglass-split"></i> Pending
                    </span>
                {% elif row.crn_status == 9 %}
                    <span class="status-received">
                        <i class="bi bi-check-circle"></i> Received
                    </span>
                {% endif %}
            </td>
            <td>
                <a href="{% url 'cn_edit' row.pk %}" class="btn btn-sm btn-outline-primary">
                    Edit
                </a>
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>

{% endblock %}
```

---

## 7. Common Issues & Fixes

### 7.1 CSRF Token Error

**Error:**
```
NoReverseMatch: Reverse for 'report_ai' not found
```

**Solution:**
1. Find all references to the deleted view
```bash
grep -r "report_ai" . --include="*.py" --include="*.html"
```

2. Remove from URLs, views, and templates

3. Add CSRF settings to settings.py:
```python
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_SAMESITE = 'Lax'
```

---

### 7.2 Oracle Connection Issues

**Error:** `django.db.utils.DatabaseError: ORA-12514`

**Solutions:**
1. Check Oracle is running
2. Verify ORACLE_CLIENT_DIR is correct
3. Test connection manually:
```python
import oracledb
conn = oracledb.connect("user/password@host:port/SDESDB")
conn.close()
```

---

### 7.3 Session/Cache Issues

**Permission changes not taking effect:**

```python
from accounts.permissions import clear_permission_cache
clear_permission_cache()
```

---

## Deployment Checklist

- [ ] DEBUG = False in settings.py
- [ ] ALLOWED_HOSTS configured
- [ ] CSRF_COOKIE_SECURE = True (HTTPS only)
- [ ] SESSION_COOKIE_SECURE = True
- [ ] SECRET_KEY randomized
- [ ] Database backups enabled
- [ ] Static files collected
- [ ] Logs configured

---

## Summary

**What We Built:**

1. **Dual Authentication**
   - Oracle procedure for main app
   - Django User model for admin

2. **Role-Based Access Control**
   - Module-level permissions
   - View-level permissions
   - Cached for performance

3. **Module System**
   - Scalable app structure
   - Modular features
   - Admin-controlled access

4. **Real-World Feature**
   - Container Notification with status
   - Ordered by pending first
   - Display-only status column

---

**Key Takeaways:**

✅ Always separate authentication from authorization  
✅ Use caching for permission checks  
✅ Make admin interface user-friendly  
✅ Test with real data  
✅ Document everything  

---

**Next Steps:**

1. Add tests for permission checking
2. Implement audit logging
3. Create user onboarding workflow
4. Add email notifications
5. Set up monitoring/alerts

---

**Questions?**

Refer to the CLAUDE.md file in the project root for specific commands and setup instructions.

Good luck building! 🚀
