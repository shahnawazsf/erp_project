# Operations Module Guide

**Author:** Claude Code Assistant  
**Date:** June 2026  
**Version:** 1.0  
**Status:** ✅ Implemented

---

## Table of Contents

1. [Overview](#overview)
2. [Module Structure](#module-structure)
3. [Models](#models)
4. [Views & URLs](#views--urls)
5. [Templates](#templates)
6. [Admin Interface](#admin-interface)
7. [Database Tables](#database-tables)
8. [Usage Examples](#usage-examples)
9. [Integration Points](#integration-points)
10. [Future Enhancements](#future-enhancements)

---

## Overview

### Purpose
The Operations module manages operational workflows, equipment maintenance, work orders, and operational metrics within the ERP system. It provides tools to track and monitor day-to-day operational activities.

### Key Features
- **Work Order Management** — Create, assign, and track work orders
- **Equipment Maintenance** — Schedule and log maintenance activities (preventive, corrective, predictive)
- **Operational Metrics** — Record and track operational KPIs and measurements
- **Dashboard** — Real-time view of operational status and metrics

### Module Location
```
operations/
├── models.py           # Data models
├── views.py            # Views and logic
├── urls.py             # URL routing
├── admin.py            # Django admin interface
├── apps.py             # App configuration
├── migrations/         # Database migrations
└── templates/
    └── operations/
        ├── dashboard.html
        ├── work_orders_list.html
        └── maintenance_list.html
```

---

## Module Structure

### Installation Steps

1. **Created Django App**
   ```bash
   python manage.py startapp operations
   ```

2. **Added to INSTALLED_APPS** in `erp_project/settings.py`
   ```python
   INSTALLED_APPS = [
       ...
       'operations',
   ]
   ```

3. **Configured URLs** in `erp_project/urls.py`
   ```python
   urlpatterns = [
       ...
       path('operations/', include('operations.urls')),
   ]
   ```

---

## Models

### 1. WorkOrder

**Purpose:** Manage work orders and task assignments

**Fields:**
```python
id                CharField(max_length=50, primary_key=True)
description       TextField()
status            CharField(choices=['draft', 'scheduled', 'in_progress', 'completed', 'cancelled'])
assigned_to       CharField(max_length=100, null=True, blank=True)
start_date        DateTimeField(null=True, blank=True)
end_date          DateTimeField(null=True, blank=True)
priority          CharField(choices=['low', 'medium', 'high'], default='medium')
created_at        DateTimeField(auto_now_add=True)
updated_at        DateTimeField(auto_now=True)
```

**Database Table:** `WORK_ORDERS`

**Example Usage:**
```python
# Create a work order
wo = WorkOrder.objects.create(
    id='WO-2026-001',
    description='Equipment maintenance for Assembly Line A',
    status='scheduled',
    assigned_to='John Doe',
    priority='high'
)

# Query work orders
active_orders = WorkOrder.objects.filter(status__in=['scheduled', 'in_progress'])
```

---

### 2. Maintenance

**Purpose:** Track equipment maintenance activities

**Fields:**
```python
id                CharField(max_length=50, primary_key=True)
equipment_name    CharField(max_length=200)
maintenance_type  CharField(choices=['preventive', 'corrective', 'predictive'])
scheduled_date    DateField()
completed_date    DateField(null=True, blank=True)
description       TextField()
cost              DecimalField(max_digits=12, decimal_places=2)
status            CharField(max_length=20, default='pending')
created_at        DateTimeField(auto_now_add=True)
```

**Database Table:** `MAINTENANCE`

**Example Usage:**
```python
# Create maintenance record
maint = Maintenance.objects.create(
    id='MAINT-2026-001',
    equipment_name='Pump System A',
    maintenance_type='preventive',
    scheduled_date='2026-06-15',
    cost=2500.00,
    description='Regular maintenance and filter replacement'
)

# Get pending maintenance
pending = Maintenance.objects.filter(completed_date__isnull=True)

# Get maintenance cost by equipment
total_cost = Maintenance.objects.filter(
    equipment_name='Pump System A',
    completed_date__isnull=False
).aggregate(total=Sum('cost'))['total']
```

---

### 3. OperationalMetric

**Purpose:** Record operational measurements and KPIs

**Fields:**
```python
id                CharField(max_length=50, primary_key=True)
metric_name       CharField(max_length=200)
metric_value      DecimalField(max_digits=12, decimal_places=2)
measurement_date  DateField()
unit              CharField(max_length=50, null=True, blank=True)
created_at        DateTimeField(auto_now_add=True)
```

**Database Table:** `OPERATIONAL_METRICS`

**Example Usage:**
```python
# Record a metric
OperationalMetric.objects.create(
    id='METRIC-2026-001',
    metric_name='Production Output',
    metric_value=5000.00,
    unit='units',
    measurement_date='2026-06-08'
)

# Query metrics
daily_output = OperationalMetric.objects.filter(
    metric_name='Production Output',
    measurement_date='2026-06-08'
)
```

---

## Views & URLs

### Available Views

#### 1. Operations Dashboard
**URL:** `/operations/`
**View:** `operations_dashboard(request)`
**Context Variables:**
- `total_work_orders` — Total count of work orders
- `active_work_orders` — Count of scheduled/in-progress orders
- `completed_work_orders` — Count of completed orders
- `pending_maintenance` — Count of pending maintenance tasks
- `total_maintenance_cost` — Sum of completed maintenance costs
- `recent_work_orders` — Last 5 work orders
- `recent_maintenance` — Last 5 maintenance records

#### 2. Work Orders List
**URL:** `/operations/work-orders/`
**View:** `work_orders_list(request)`
**Context Variables:**
- `work_orders` — All work orders ordered by creation date

#### 3. Maintenance List
**URL:** `/operations/maintenance/`
**View:** `maintenance_list(request)`
**Context Variables:**
- `maintenance` — All maintenance records ordered by scheduled date

### URL Configuration
```python
# operations/urls.py
urlpatterns = [
    path('', views.operations_dashboard, name='dashboard'),
    path('work-orders/', views.work_orders_list, name='work_orders_list'),
    path('maintenance/', views.maintenance_list, name='maintenance_list'),
]
```

### Navigation Links
```html
<!-- Dashboard -->
<a href="{% url 'operations:dashboard' %}">Operations Dashboard</a>

<!-- Work Orders -->
<a href="{% url 'operations:work_orders_list' %}">Work Orders</a>

<!-- Maintenance -->
<a href="{% url 'operations:maintenance_list' %}">Maintenance</a>
```

---

## Templates

### 1. dashboard.html
**Path:** `operations/templates/operations/dashboard.html`

**Features:**
- Key metrics displayed in colored cards (4 cards per row)
- Row 1: Total Work Orders, Active Orders, Completed Orders, Pending Maintenance
- Row 2: Total Maintenance Cost
- Row 3: Recent work orders and maintenance records lists

**Colors:**
- Primary (Blue) — Total Work Orders
- Success (Green) — Active Work Orders
- Info (Cyan) — Completed Work Orders
- Warning (Orange) — Pending Maintenance
- Danger (Red) — Total Maintenance Cost

---

### 2. work_orders_list.html
**Path:** `operations/templates/operations/work_orders_list.html`

**Features:**
- Responsive table with all work orders
- Columns: ID, Description, Status, Priority, Assigned To, Created At
- Status displayed as badge
- Searchable and sortable

---

### 3. maintenance_list.html
**Path:** `operations/templates/operations/maintenance_list.html`

**Features:**
- Responsive table with all maintenance records
- Columns: ID, Equipment, Type, Scheduled Date, Status, Cost
- Type displayed as badge
- Shows both pending and completed maintenance

---

## Admin Interface

### Admin Registration
All models are registered in Django admin with appropriate list displays, filters, and search fields.

**Access:** `/admin/operations/`

### Work Order Admin
- **List Display:** ID, Status, Priority, Assigned To, Created At
- **Filters:** Status, Priority, Creation Date
- **Search:** ID, Description, Assigned To
- **Read-only:** Created At, Updated At

### Maintenance Admin
- **List Display:** ID, Equipment, Type, Scheduled Date, Status, Cost
- **Filters:** Maintenance Type, Status, Scheduled Date
- **Search:** Equipment Name, Description
- **Read-only:** Created At

### Operational Metric Admin
- **List Display:** ID, Metric Name, Value, Unit, Measurement Date
- **Filters:** Metric Name, Measurement Date
- **Search:** Metric Name
- **Read-only:** Created At

---

## Database Tables

### WORK_ORDERS
```sql
CREATE TABLE WORK_ORDERS (
    ID VARCHAR2(50) PRIMARY KEY,
    DESCRIPTION CLOB,
    STATUS VARCHAR2(20),
    ASSIGNED_TO VARCHAR2(100),
    START_DATE TIMESTAMP,
    END_DATE TIMESTAMP,
    PRIORITY VARCHAR2(20),
    CREATED_AT TIMESTAMP,
    UPDATED_AT TIMESTAMP
);
```

### MAINTENANCE
```sql
CREATE TABLE MAINTENANCE (
    ID VARCHAR2(50) PRIMARY KEY,
    EQUIPMENT_NAME VARCHAR2(200),
    MAINTENANCE_TYPE VARCHAR2(20),
    SCHEDULED_DATE DATE,
    COMPLETED_DATE DATE,
    DESCRIPTION CLOB,
    COST NUMBER(12,2),
    STATUS VARCHAR2(20),
    CREATED_AT TIMESTAMP
);
```

### OPERATIONAL_METRICS
```sql
CREATE TABLE OPERATIONAL_METRICS (
    ID VARCHAR2(50) PRIMARY KEY,
    METRIC_NAME VARCHAR2(200),
    METRIC_VALUE NUMBER(12,2),
    MEASUREMENT_DATE DATE,
    UNIT VARCHAR2(50),
    CREATED_AT TIMESTAMP
);
```

---

## Usage Examples

### Create a Work Order
```python
from operations.models import WorkOrder

wo = WorkOrder.objects.create(
    id='WO-2026-001',
    description='Replace hydraulic fluid in Press Machine B',
    status='scheduled',
    assigned_to='Alice Johnson',
    priority='high',
    start_date='2026-06-10 08:00:00',
    end_date='2026-06-10 12:00:00'
)
```

### Update Work Order Status
```python
wo = WorkOrder.objects.get(id='WO-2026-001')
wo.status = 'in_progress'
wo.save()
```

### Query Work Orders by Status
```python
pending = WorkOrder.objects.filter(status__in=['draft', 'scheduled'])
completed = WorkOrder.objects.filter(status='completed')
```

### Record Maintenance Activity
```python
from operations.models import Maintenance
from datetime import date

maint = Maintenance.objects.create(
    id='MAINT-2026-001',
    equipment_name='CNC Lathe A',
    maintenance_type='preventive',
    scheduled_date=date(2026, 6, 15),
    completed_date=date(2026, 6, 15),
    description='Oil change and alignment check',
    cost=1200.50,
    status='completed'
)
```

### Get Maintenance Costs
```python
from django.db.models import Sum

# Total cost by equipment
costs = Maintenance.objects.filter(
    completed_date__isnull=False
).values('equipment_name').annotate(
    total_cost=Sum('cost')
)

# Year-to-date maintenance cost
ytd_cost = Maintenance.objects.filter(
    completed_date__year=2026
).aggregate(total=Sum('cost'))['total']
```

### Record Operational Metric
```python
from operations.models import OperationalMetric
from datetime import date

metric = OperationalMetric.objects.create(
    id='METRIC-2026-001',
    metric_name='Daily Production',
    metric_value=4500.00,
    unit='units',
    measurement_date=date(2026, 6, 8)
)
```

---

## Integration Points

### Dashboard Integration
The Operations module metrics are available to be added to the main dashboard.

**Available Context Variables for Main Dashboard:**
```python
# In core/views.py dashboard() function
'total_work_orders': WorkOrder.objects.count(),
'active_work_orders': WorkOrder.objects.filter(status__in=['scheduled', 'in_progress']).count(),
'pending_maintenance': Maintenance.objects.filter(completed_date__isnull=True).count(),
```

### Permission Integration
All views use `@login_required` decorator. To add role-based access:

```python
from accounts.models import ModulePermission

@login_required
def operations_dashboard(request):
    # Check permission
    has_access = ModulePermission.objects.filter(
        user=request.user,
        module__name='operations',
        can_view=True
    ).exists()
    
    if not has_access:
        return HttpResponseForbidden("Access denied")
    ...
```

---

## Future Enhancements

### Planned Features
1. **Work Order Creation Form** — Add UI for creating/editing work orders
2. **Maintenance Scheduling** — Calendar view for maintenance planning
3. **Equipment Tracking** — Link work orders to specific equipment
4. **Approval Workflow** — Add approval status for work orders
5. **Notifications** — Alert when maintenance is overdue
6. **Reports** — Maintenance cost analysis, KPI trends
7. **Mobile App Integration** — Work order status updates on mobile

### Database Enhancements
```python
# Add to WorkOrder model
equipment = ForeignKey('Equipment', on_delete=models.SET_NULL, null=True)
estimated_hours = DecimalField(max_digits=5, decimal_places=2)
actual_hours = DecimalField(max_digits=5, decimal_places=2, null=True)

# New Equipment model
class Equipment(models.Model):
    id = CharField(max_length=50, primary_key=True)
    name = CharField(max_length=200)
    equipment_type = CharField(max_length=100)
    location = CharField(max_length=200)
    last_maintenance = DateField()
    next_maintenance = DateField()
```

---

## Testing

### Manual Testing Checklist
- [ ] Navigate to `/operations/` and verify dashboard loads
- [ ] Create a work order via admin and verify it appears in dashboard
- [ ] Create a maintenance record via admin
- [ ] Check that metrics display correctly
- [ ] Navigate to `/operations/work-orders/` and verify list displays
- [ ] Navigate to `/operations/maintenance/` and verify list displays
- [ ] Test sorting and filtering in admin

---

## Troubleshooting

### Common Issues

**Issue:** "No module named 'operations'"
**Solution:** Ensure 'operations' is added to INSTALLED_APPS in settings.py

**Issue:** Database table not found
**Solution:** Run migrations if using Django ORM, or create Oracle tables manually

**Issue:** Views not accessible
**Solution:** Verify URL configuration in erp_project/urls.py includes operations URLs

---

## Related Documentation
- [COMPLETE_DEVELOPMENT_GUIDE.md](COMPLETE_DEVELOPMENT_GUIDE.md)
- [TECHNICAL_DOCS.md](TECHNICAL_DOCS.md)
- [ROLE_BASED_ACCESS_GUIDE.md](ROLE_BASED_ACCESS_GUIDE.md)
