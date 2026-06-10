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


def get_container_daily_summary():
    """Get container received and shipped by day"""
    from django.db import connection

    query = """
        SELECT
            ACTION_DAY,
            RECVD_QTY as Recvd,
            SHIPPED_QTY as Shipped
        FROM YOUR_TABLE_NAME
        ORDER BY ACTION_DAY DESC
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


@login_required
def operations_dashboard(request):
    context = {
        # Card 1: Daily Container Activity
        'container_daily_summary': _safe([], lambda: get_container_daily_summary()),
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
