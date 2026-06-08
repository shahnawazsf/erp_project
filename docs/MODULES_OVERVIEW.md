# ERP System Modules Overview

**Date:** June 2026  
**Version:** 1.0

---

## Quick Navigation

| Module | URL | Purpose | Status |
|--------|-----|---------|--------|
| [Core](#core) | `/` | Dashboard, shared utilities | ✅ Active |
| [Accounts](#accounts) | `/accounts/` | Authentication, user management | ✅ Active |
| [Finance](#finance) | `/finance/` | Invoices, expenses, reports, VAT | ✅ Active |
| [HR](#hr) | `/hr/` | Employees, leave requests, payroll | ✅ Active |
| [Inventory](#inventory) | `/inventory/` | Products, stock, warehouse | ✅ Active |
| [Sales](#sales) | `/sales/` | Orders, customers, quotes | ✅ Active |
| [Purchasing](#purchasing) | `/purchasing/` | POs, suppliers, procurements | ✅ Active |
| [Operations](#operations) | `/operations/` | Work orders, maintenance, metrics | ✅ New (June 8) |

---

## Module Details

### Core
**Location:** `core/`  
**Purpose:** Main dashboard and shared utilities  
**Key Features:**
- Dashboard with system-wide metrics
- Shared template layouts (base.html)
- Common utilities and helpers

**Main URL:**
- `/` — Dashboard

**Related Docs:** [COMPLETE_DEVELOPMENT_GUIDE.md](COMPLETE_DEVELOPMENT_GUIDE.md)

---

### Accounts
**Location:** `accounts/`  
**Purpose:** User authentication and access control  
**Key Features:**
- Oracle-based authentication
- User management
- Role-based access control
- Two auth paths: Main app login & Django admin

**Main URLs:**
- `/accounts/login/` — Login page
- `/accounts/logout/` — Logout
- `/admin/` — Django admin

**Database Tables:**
- `ERPP_USERS` — Oracle user table
- `accounts_user` — Django auth users (synced with LOGIN_USER role)
- `auth_group` — Permission groups
- `accounts_module` — Modules and permissions

**Related Docs:** [ROLE_BASED_ACCESS_GUIDE.md](ROLE_BASED_ACCESS_GUIDE.md)

---

### Finance
**Location:** `finance/`  
**Purpose:** Financial management and reporting  
**Key Features:**
- Invoice management and tracking
- Expense management
- VAT report generation (monthly)
- Customer invoice reports with BOL lookup
- Chart of accounts
- Container notifications

**Main URLs:**
- `/finance/` — Finance dashboard
- `/finance/invoices/` — Manage invoices
- `/finance/expenses/` — Manage expenses
- `/finance/reports/vat/` — VAT reports
- `/finance/reports/customer-invoice/` — Customer invoices
- `/finance/chart-of-accounts/` — CoA management

**Key Models:**
- `Invoice` — Invoice records
- `Expense` — Expense entries
- `ChartOfAccounts` — CoA entries
- `ContainerNotification` — Container tracking

**Database Tables:**
- `INVOICES` — Invoice data
- `EXPENSES` — Expense records
- `CHART_OF_ACCOUNTS` — CoA mapping
- `INV_WEEKLY_REPORT_VIEW` — Invoice report view
- `INV_WEEKLY_REPORT_BL_VIEW` — BOL lookup view

**Related Docs:** 
- [COMPLETE_DEVELOPMENT_GUIDE.md](COMPLETE_DEVELOPMENT_GUIDE.md) (June 3 update)
- [REPORT_DEVELOPMENT_GUIDE.md](REPORT_DEVELOPMENT_GUIDE.md)

---

### HR
**Location:** `hr/`  
**Purpose:** Human resources management  
**Key Features:**
- Employee records and management
- Leave request tracking
- Attendance management
- Payroll integration

**Main URLs:**
- `/hr/` — HR dashboard
- `/hr/employees/` — Employee list
- `/hr/leave-requests/` — Leave management
- `/hr/attendance/` — Attendance records

**Key Models:**
- `Employee` — Employee records
- `LeaveRequest` — Leave requests
- `Attendance` — Attendance tracking

**Database Tables:**
- `EMPLOYEES` — Employee data
- `LEAVE_REQUESTS` — Leave request records
- `ATTENDANCE` — Attendance logs

---

### Inventory
**Location:** `inventory/`  
**Purpose:** Inventory and warehouse management  
**Key Features:**
- Product catalog management
- Stock level tracking
- Warehouse locations
- Low stock alerts
- Inventory adjustments

**Main URLs:**
- `/inventory/` — Inventory dashboard
- `/inventory/products/` — Product management
- `/inventory/stock/` — Stock levels
- `/inventory/warehouse/` — Warehouse management

**Key Models:**
- `Product` — Product catalog
- `Stock` — Stock levels
- `WarehouseLocation` — Warehouse management

**Database Tables:**
- `PRODUCTS` — Product data
- `STOCK_LEVELS` — Current stock
- `WAREHOUSE_LOCATIONS` — Warehouse info

**Related Docs:** [COMPLETE_DEVELOPMENT_GUIDE.md](COMPLETE_DEVELOPMENT_GUIDE.md)

---

### Sales
**Location:** `sales/`  
**Purpose:** Sales order management and customer relations  
**Key Features:**
- Sales order creation and tracking
- Customer management
- Quote generation
- Order fulfillment
- Sales analytics

**Main URLs:**
- `/sales/` — Sales dashboard
- `/sales/orders/` — Sales orders
- `/sales/customers/` — Customer management
- `/sales/quotes/` — Quote management

**Key Models:**
- `SalesOrder` — Sales orders
- `Customer` — Customer records
- `SalesQuote` — Sales quotes

**Database Tables:**
- `SALES_ORDERS` — Order data
- `CUSTOMERS` — Customer information
- `SALES_QUOTES` — Quote records

---

### Purchasing
**Location:** `purchasing/`  
**Purpose:** Procurement and vendor management  
**Key Features:**
- Purchase order creation and tracking
- Supplier management
- Purchase request handling
- Goods receipt tracking
- Vendor performance

**Main URLs:**
- `/purchasing/` — Purchasing dashboard
- `/purchasing/orders/` — Purchase orders
- `/purchasing/suppliers/` — Supplier management
- `/purchasing/requests/` — Purchase requests

**Key Models:**
- `PurchaseOrder` — Purchase orders
- `Supplier` — Supplier records
- `PurchaseRequest` — Purchase requests

**Database Tables:**
- `PURCHASE_ORDERS` — Order data
- `SUPPLIERS` — Supplier information
- `PURCHASE_REQUESTS` — Request records

---

### Operations (NEW - June 8)
**Location:** `operations/`  
**Purpose:** Operational management, work orders, and maintenance  
**Key Features:**
- Work order tracking and management
- Equipment maintenance scheduling and logging
- Operational metrics and KPI tracking
- Maintenance cost analysis
- Operations dashboard with real-time metrics

**Main URLs:**
- `/operations/` — Operations dashboard
- `/operations/work-orders/` — Work orders list
- `/operations/maintenance/` — Maintenance records

**Key Models:**
- `WorkOrder` — Work order management (status: draft, scheduled, in_progress, completed, cancelled)
- `Maintenance` — Equipment maintenance (types: preventive, corrective, predictive)
- `OperationalMetric` — KPI and measurement tracking

**Database Tables:**
- `WORK_ORDERS` — Work order records
- `MAINTENANCE` — Maintenance activity log
- `OPERATIONAL_METRICS` — KPI measurements

**Dashboard Metrics:**
- Total Work Orders
- Active Work Orders (scheduled + in_progress)
- Completed Work Orders
- Pending Maintenance count
- Total Maintenance Cost
- Recent work orders and maintenance

**Related Docs:** [OPERATIONS_MODULE_GUIDE.md](OPERATIONS_MODULE_GUIDE.md)

---

## Installation Checklist

### For Existing Modules
- [x] Django app created
- [x] Added to INSTALLED_APPS
- [x] Models defined
- [x] URL routing configured
- [x] Views implemented
- [x] Templates created
- [x] Admin interface configured

### For New Modules (Operations - June 8)
- [x] Django app created with `python manage.py startapp operations`
- [x] Added to INSTALLED_APPS in settings.py
- [x] Models created (WorkOrder, Maintenance, OperationalMetric)
- [x] Views implemented (dashboard, lists)
- [x] URL routing added to main urls.py
- [x] Templates created (dashboard, lists)
- [x] Admin interface registered
- [x] Documentation created

---

## Configuration References

### INSTALLED_APPS (settings.py)
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'crispy_forms',
    'crispy_bootstrap5',
    'widget_tweaks',
    'rest_framework',
    # ERP modules
    'core',
    'accounts',
    'hr',
    'inventory',
    'finance',
    'sales',
    'purchasing',
    'operations',  # NEW
]
```

### URL Routing (urls.py)
```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('hr/', include('hr.urls')),
    path('inventory/', include('inventory.urls')),
    path('finance/', include('finance.urls')),
    path('sales/', include('sales.urls')),
    path('purchasing/', include('purchasing.urls')),
    path('operations/', include('operations.urls')),  # NEW
]
```

---

## Quick Commands

### Start Development Server
```bash
python manage.py runserver 9001
```

### Create Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Create Superuser
```bash
python manage.py createsuperuser
# Note: Admin users must be inserted into Oracle ERPP_USERS table
```

### Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### Run in Production (Waitress)
```bash
python manage.py collectstatic --noinput
python -m waitress --port=9001 --host=0.0.0.0 erp_project.wsgi:application
```

---

## Module Dependencies

```
Core ← (used by all modules)
  ├── Finance
  ├── HR
  ├── Inventory ← (used by Sales, Purchasing)
  ├── Sales ← (optional: uses Inventory)
  ├── Purchasing ← (uses Inventory)
  └── Operations (independent)

Accounts ← (authentication for all modules)
```

---

## Access Control

All modules use `@login_required` decorator on views. Role-based access is managed through:
- `accounts.models.ModulePermission` — Module-level permissions
- `accounts.models.SubModulePermission` — Fine-grained access control
- Oracle `LOGIN_USER` table role mapping (A=admin, U=employee)

**Related Docs:** [ROLE_BASED_ACCESS_GUIDE.md](ROLE_BASED_ACCESS_GUIDE.md)

---

## Database Connectivity

All modules use Oracle 12.2 database (`172.16.1.12:1521/SDESDB`) via:
- Python `oracledb` package in thick mode
- Custom backend: `erp_project/oracle_compat/base.py`
- Settings: `DATABASES['default']['ENGINE'] = 'erp_project.oracle_compat.base.DatabaseWrapper'`

**Key Files:**
- `.env` — Database credentials (ORACLE_USER, ORACLE_PASSWORD, ORACLE_CLIENT_DIR)
- `CLAUDE.md` — Oracle connection pattern documentation

---

## Support & Documentation

| Topic | Document |
|-------|----------|
| Getting Started | [COMPLETE_DEVELOPMENT_GUIDE.md](COMPLETE_DEVELOPMENT_GUIDE.md) |
| Technical Details | [TECHNICAL_DOCS.md](TECHNICAL_DOCS.md) |
| Operations Module | [OPERATIONS_MODULE_GUIDE.md](OPERATIONS_MODULE_GUIDE.md) |
| Role-Based Access | [ROLE_BASED_ACCESS_GUIDE.md](ROLE_BASED_ACCESS_GUIDE.md) |
| Reports & Analytics | [REPORT_DEVELOPMENT_GUIDE.md](REPORT_DEVELOPMENT_GUIDE.md) |
| Production Deployment | [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md) |
| Setup Instructions | [SETUP_CHECKLIST.md](SETUP_CHECKLIST.md) |

---

## Version History

| Date | Change | Module |
|------|--------|--------|
| June 8, 2026 | Operations module added | operations |
| June 4, 2026 | Header/footer features added | core, finance |
| June 3, 2026 | Customer invoice report refactored | finance |
| May 2026 | Initial ERP system development | all |
