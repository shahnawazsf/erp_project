# Operations Module - Quick Start Guide

**Date:** June 8, 2026  
**Version:** 1.0  
**Status:** ✅ Ready to Use

---

## 5-Minute Setup

### 1. Access the Operations Dashboard
```
URL: http://localhost:9001/operations/
```

The dashboard displays:
- Total Work Orders count
- Active Work Orders (in-progress)
- Completed Work Orders
- Pending Maintenance tasks
- Total Maintenance Cost
- Recent activities list

### 2. View Work Orders
```
URL: http://localhost:9001/operations/work-orders/
```

See all work orders in a table with:
- Status (draft, scheduled, in_progress, completed, cancelled)
- Priority (low, medium, high)
- Assigned person
- Creation date

### 3. View Maintenance Records
```
URL: http://localhost:9001/operations/maintenance/
```

See all maintenance activities with:
- Equipment name
- Maintenance type (preventive, corrective, predictive)
- Scheduled date
- Status and cost

---

## Create Your First Records

### In Django Admin

**Access:** `http://localhost:9001/admin/`

#### Create a Work Order
1. Navigate to **Operations → Work Orders**
2. Click **Add Work Order**
3. Fill in:
   - **ID:** `WO-2026-001`
   - **Description:** `Replace hydraulic fluid in machinery`
   - **Status:** `scheduled`
   - **Assigned To:** `John Doe`
   - **Priority:** `high`
   - **Start Date:** `2026-06-10 08:00`
   - **End Date:** `2026-06-10 12:00`
4. Click **Save**

#### Create a Maintenance Record
1. Navigate to **Operations → Maintenance**
2. Click **Add Maintenance**
3. Fill in:
   - **ID:** `MAINT-2026-001`
   - **Equipment Name:** `CNC Lathe A`
   - **Maintenance Type:** `preventive`
   - **Scheduled Date:** `2026-06-15`
   - **Description:** `Regular oil change and alignment`
   - **Cost:** `1200.50`
   - **Status:** `pending`
4. Click **Save**

#### Create an Operational Metric
1. Navigate to **Operations → Operational Metrics**
2. Click **Add Operational Metric**
3. Fill in:
   - **ID:** `METRIC-2026-001`
   - **Metric Name:** `Daily Production Units`
   - **Metric Value:** `5000`
   - **Unit:** `units`
   - **Measurement Date:** `2026-06-08`
4. Click **Save**

---

## Python/Django Usage

### In Django Shell
```bash
python manage.py shell
```

#### Create a Work Order
```python
from operations.models import WorkOrder
from datetime import datetime

wo = WorkOrder.objects.create(
    id='WO-2026-002',
    description='Equipment inspection',
    status='scheduled',
    assigned_to='Alice Johnson',
    priority='medium',
    start_date=datetime(2026, 6, 12, 10, 0),
    end_date=datetime(2026, 6, 12, 14, 0)
)
print(f"Created: {wo}")
```

#### Query Work Orders
```python
# Get all work orders
all_orders = WorkOrder.objects.all()

# Get active work orders
active = WorkOrder.objects.filter(status__in=['scheduled', 'in_progress'])

# Get high priority orders
high_priority = WorkOrder.objects.filter(priority='high')

# Count completed orders
completed_count = WorkOrder.objects.filter(status='completed').count()
```

#### Create a Maintenance Record
```python
from operations.models import Maintenance
from datetime import date

maint = Maintenance.objects.create(
    id='MAINT-2026-002',
    equipment_name='Pump System B',
    maintenance_type='corrective',
    scheduled_date=date(2026, 6, 20),
    description='Fix leaking valve',
    cost=800.00,
    status='pending'
)
print(f"Created: {maint}")
```

#### Query Maintenance
```python
# Get pending maintenance
pending = Maintenance.objects.filter(completed_date__isnull=True)

# Get completed maintenance
completed = Maintenance.objects.filter(completed_date__isnull=False)

# Get maintenance cost by equipment
from django.db.models import Sum
costs = Maintenance.objects.values('equipment_name').annotate(
    total=Sum('cost')
)
for item in costs:
    print(f"{item['equipment_name']}: ${item['total']}")
```

#### Record Operational Metric
```python
from operations.models import OperationalMetric
from datetime import date

metric = OperationalMetric.objects.create(
    id='METRIC-2026-002',
    metric_name='Equipment Utilization',
    metric_value=87.5,
    unit='percent',
    measurement_date=date(2026, 6, 8)
)
print(f"Created: {metric}")
```

#### Query Metrics
```python
# Get latest production metrics
latest = OperationalMetric.objects.filter(
    metric_name='Daily Production Units'
).order_by('-measurement_date')[:5]

# Get metrics by date range
from datetime import date
metrics = OperationalMetric.objects.filter(
    measurement_date__gte=date(2026, 6, 1),
    measurement_date__lte=date(2026, 6, 30)
)
```

---

## Common Tasks

### Update a Work Order Status
```python
from operations.models import WorkOrder

wo = WorkOrder.objects.get(id='WO-2026-001')
wo.status = 'in_progress'
wo.save()
```

### Mark Maintenance as Completed
```python
from operations.models import Maintenance
from datetime import date

maint = Maintenance.objects.get(id='MAINT-2026-001')
maint.completed_date = date.today()
maint.status = 'completed'
maint.save()
```

### Calculate Maintenance ROI
```python
from operations.models import Maintenance
from django.db.models import Sum, Count
from datetime import date, timedelta

# Get last 30 days maintenance
thirty_days_ago = date.today() - timedelta(days=30)
recent = Maintenance.objects.filter(
    scheduled_date__gte=thirty_days_ago
)

total_cost = recent.aggregate(Sum('cost'))['cost__sum'] or 0
total_count = recent.count()
avg_cost = total_cost / total_count if total_count > 0 else 0

print(f"30-day Maintenance Report:")
print(f"  Total Cost: ${total_cost}")
print(f"  Number of Activities: {total_count}")
print(f"  Average Cost: ${avg_cost:.2f}")
```

### Get Dashboard Metrics
```python
from operations.models import WorkOrder, Maintenance

metrics = {
    'total_work_orders': WorkOrder.objects.count(),
    'active_work_orders': WorkOrder.objects.filter(
        status__in=['scheduled', 'in_progress']
    ).count(),
    'completed_work_orders': WorkOrder.objects.filter(
        status='completed'
    ).count(),
    'pending_maintenance': Maintenance.objects.filter(
        completed_date__isnull=True
    ).count(),
}

for key, value in metrics.items():
    print(f"{key}: {value}")
```

---

## URL Reference

| Path | View | Description |
|------|------|-------------|
| `/operations/` | `operations_dashboard` | Main dashboard with metrics |
| `/operations/work-orders/` | `work_orders_list` | All work orders |
| `/operations/maintenance/` | `maintenance_list` | All maintenance records |
| `/admin/operations/workorder/` | Admin | Create/edit work orders |
| `/admin/operations/maintenance/` | Admin | Create/edit maintenance |
| `/admin/operations/operationalmetric/` | Admin | Create/edit metrics |

---

## Database Schema Reference

### WORK_ORDERS Table
```sql
-- Column        Type              Description
-- ID            VARCHAR2(50)      Primary key (e.g., WO-2026-001)
-- DESCRIPTION   CLOB              Work order description
-- STATUS        VARCHAR2(20)      draft, scheduled, in_progress, completed, cancelled
-- ASSIGNED_TO   VARCHAR2(100)     Person assigned to work
-- START_DATE    TIMESTAMP         When work should start
-- END_DATE      TIMESTAMP         When work should end
-- PRIORITY      VARCHAR2(20)      low, medium, high
-- CREATED_AT    TIMESTAMP         Record creation time
-- UPDATED_AT    TIMESTAMP         Last update time
```

### MAINTENANCE Table
```sql
-- Column            Type              Description
-- ID                VARCHAR2(50)      Primary key (e.g., MAINT-2026-001)
-- EQUIPMENT_NAME    VARCHAR2(200)     Name of equipment
-- MAINTENANCE_TYPE  VARCHAR2(20)      preventive, corrective, predictive
-- SCHEDULED_DATE    DATE              When maintenance is scheduled
-- COMPLETED_DATE    DATE              When maintenance was completed
-- DESCRIPTION       CLOB              What was done
-- COST              NUMBER(12,2)      Cost of maintenance
-- STATUS            VARCHAR2(20)      pending, in_progress, completed
-- CREATED_AT        TIMESTAMP         Record creation time
```

### OPERATIONAL_METRICS Table
```sql
-- Column            Type              Description
-- ID                VARCHAR2(50)      Primary key
-- METRIC_NAME       VARCHAR2(200)     Name of metric (e.g., Production Units)
-- METRIC_VALUE      NUMBER(12,2)      Value of measurement
-- MEASUREMENT_DATE  DATE              When measurement was taken
-- UNIT              VARCHAR2(50)      Unit of measurement (units, %, hours, etc.)
-- CREATED_AT        TIMESTAMP         Record creation time
```

---

## Troubleshooting

### Issue: 404 Error on `/operations/`
**Solution:** Ensure 'operations' is in INSTALLED_APPS and URLs are configured

### Issue: No data appears on dashboard
**Solution:** Create records via Django admin first (visit `/admin/operations/`)

### Issue: Database tables don't exist
**Solution:** If using Django ORM, run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

For Oracle, create tables manually using the schema reference above.

### Issue: Can't access admin
**Solution:** Create admin user:
```bash
# Option 1: Admin user insertion into Oracle
INSERT INTO ERPP_USERS (USERNAME, PASSWORD, ROLE) VALUES ('admin', 'hashedpwd', 'A');

# Option 2: Django shell
python manage.py shell
from accounts.models import User
User.objects.create_superuser('admin', 'admin@example.com', 'password')
```

---

## Next Steps

1. **Create your first work order** in Django admin
2. **Access the dashboard** at `/operations/`
3. **Create maintenance records** for your equipment
4. **Monitor metrics** by recording operational data
5. **Review reports** in the list views

For more details, see:
- [OPERATIONS_MODULE_GUIDE.md](OPERATIONS_MODULE_GUIDE.md) — Complete documentation
- [COMPLETE_DEVELOPMENT_GUIDE.md](COMPLETE_DEVELOPMENT_GUIDE.md) — General ERP info
- [MODULES_OVERVIEW.md](MODULES_OVERVIEW.md) — All modules guide

---

## Support

If you need help:
1. Check the [OPERATIONS_MODULE_GUIDE.md](OPERATIONS_MODULE_GUIDE.md) for detailed information
2. Review example code in this guide
3. Check Django admin interface for data management
4. See error messages in Django development server console

**Created:** June 8, 2026  
**Module:** Operations (v1.0)
