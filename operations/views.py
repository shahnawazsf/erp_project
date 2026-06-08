from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from .models import WorkOrder, Maintenance, OperationalMetric


def _safe(default, fn, *args, **kwargs):
    """Run fn(); return default if any DB error occurs (e.g. table missing)."""
    try:
        return fn(*args, **kwargs)
    except Exception:
        return default


@login_required
def operations_dashboard(request):
    context = {
        'total_work_orders': _safe(0, lambda: WorkOrder.objects.count()),
        'active_work_orders': _safe(0, lambda: WorkOrder.objects.filter(status__in=['scheduled', 'in_progress']).count()),
        'completed_work_orders': _safe(0, lambda: WorkOrder.objects.filter(status='completed').count()),
        'pending_maintenance': _safe(0, lambda: Maintenance.objects.filter(completed_date__isnull=True).count()),
        'total_maintenance_cost': _safe(0, lambda: Maintenance.objects.filter(completed_date__isnull=False).aggregate(total=Sum('cost'))['total'] or 0),
        'recent_work_orders': _safe([], lambda: list(WorkOrder.objects.order_by('-created_at')[:5])),
        'recent_maintenance': _safe([], lambda: list(Maintenance.objects.order_by('-created_date')[:5])),
    }
    return render(request, 'operations/dashboard.html', context)


@login_required
def work_orders_list(request):
    work_orders = _safe([], lambda: list(WorkOrder.objects.all().order_by('-created_at')))
    context = {'work_orders': work_orders}
    return render(request, 'operations/work_orders_list.html', context)


@login_required
def maintenance_list(request):
    maintenance = _safe([], lambda: list(Maintenance.objects.all().order_by('-scheduled_date')))
    context = {'maintenance': maintenance}
    return render(request, 'operations/maintenance_list.html', context)
