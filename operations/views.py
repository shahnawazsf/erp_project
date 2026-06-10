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
        SELECT ACTION_DATE, ACTION_DAY, RECVD_QTY, SHIPPED_QTY
        FROM TABLE (GET_RECVD_SHIPPED_DATE_LIST)
        ORDER BY ACTION_DATE DESC
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            print(f"DEBUG: Container data retrieved: {len(data)} records")
            if data:
                print(f"DEBUG: First record: {data[0]}")
                print(f"DEBUG: Columns: {columns}")
            return data
    except Exception as e:
        print(f"DEBUG: Error in get_container_daily_summary: {str(e)}")
        import traceback
        traceback.print_exc()
        return []


def get_container_chart_data():
    """Get formatted data for line chart"""
    import json
    from datetime import datetime

    data = get_container_daily_summary()

    if not data:
        print("DEBUG: No data returned from get_container_daily_summary()")
        return json.dumps({
            'labels': [],
            'recvd_data': [],
            'shipped_data': []
        })

    # Extract day from ACTION_DATE and ACTION_DAY
    labels = []
    recvd_data = []
    shipped_data = []

    for item in data:
        try:
            # ACTION_DAY is CHAR(2), so it's already the day of month
            day = str(item['ACTION_DAY']).strip()

            labels.append(f"Day {day}")
            recvd_data.append(int(item['RECVD_QTY']) if item['RECVD_QTY'] else 0)
            shipped_data.append(int(item['SHIPPED_QTY']) if item['SHIPPED_QTY'] else 0)

            print(f"DEBUG: Added data - Day: {day}, Recvd: {item['RECVD_QTY']}, Shipped: {item['SHIPPED_QTY']}")
        except Exception as e:
            print(f"DEBUG: Error processing item {item}: {str(e)}")
            continue

    print(f"DEBUG: Chart data prepared - {len(labels)} days")
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
