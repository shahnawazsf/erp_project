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
    """Get container received and shipped by day for chart"""
    from django.db import connection
    import json

    query = """
        SELECT ACTION_DAY, RECVD_QTY as Recvd, SHIPPED_QTY as Shipped
        FROM TABLE (GET_RECVD_SHIPPED_DATE_LIST)
        ORDER BY ACTION_DAY
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return data
    except Exception as e:
        return []


def get_container_chart_data():
    """Get formatted data for line chart"""
    import json
    from datetime import datetime

    data = get_container_daily_summary()

    if not data:
        return json.dumps({
            'labels': [],
            'recvd_data': [],
            'shipped_data': []
        })

    # Extract day from ACTION_DAY and format as day number
    labels = []
    recvd_data = []
    shipped_data = []

    for item in data:
        try:
            # Format date as "1", "2", "3", etc. (day of month)
            if isinstance(item['ACTION_DAY'], str):
                day = item['ACTION_DAY'].split('-')[2] if '-' in str(item['ACTION_DAY']) else str(item['ACTION_DAY'])
                day = int(day)
            else:
                day = item['ACTION_DAY'].day

            labels.append(str(day))
            recvd_data.append(int(item['Recvd']) if item['Recvd'] else 0)
            shipped_data.append(int(item['Shipped']) if item['Shipped'] else 0)
        except:
            continue

    return json.dumps({
        'labels': labels,
        'recvd_data': recvd_data,
        'shipped_data': shipped_data
    })


@login_required
def operations_dashboard(request):
    import json

    context = {
        # Card 1: Container Received & Shipped Line Chart
        'container_chart_data': _safe('{}', lambda: get_container_chart_data()),
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
