from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.db.models import Sum, Q
from .models import WorkOrder, Maintenance, OperationalMetric
from django.db import connection
from django.core.cache import cache


def _safe(default, fn, *args, **kwargs):
    """Run fn(); return default if any DB error occurs (e.g. table missing)."""
    try:
        return fn(*args, **kwargs)
    except Exception:
        return default
def get_container_year_summary():
    """Get Container received by year to date chart"""
    import json

    query ="""
        SELECT TO_NUMBER(TO_CHAR(DATERECEIVED,'YYYY')) YEAR,TO_NUMBER(TO_CHAR(DATERECEIVED,'YYYY')) YEAR1,SUM(QTYRECEIVED) QTY
        FROM RECEIPTDETAIL
        WHERE STORERKEY LIKE 'SDRS%'
        AND SKU LIKE 'CNT%'
        AND STATUS=9
        AND TO_NUMBER(TO_CHAR(DATERECEIVED,'YYYY'))>=TO_NUMBER(TO_CHAR(SYSDATE,'YYYY'))-2
        AND TO_NUMBER(TO_CHAR(DATERECEIVED,'MMDD'))<=TO_NUMBER(TO_CHAR(SYSDATE-1,'MMDD'))
        GROUP BY TO_NUMBER(TO_CHAR(DATERECEIVED,'YYYY'))
        ORDER BY TO_NUMBER(TO_CHAR(DATERECEIVED,'YYYY'))

    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            # print(f"DEBUG: Container data retrieved: {len(data)} records")
            # if data:
            #     print(f"DEBUG: First record: {data[0]}")
            #     print(f"DEBUG: Columns: {columns}")
            return data
    except Exception as e:
        # print(f"DEBUG: Error in get_container_year_summary: {str(e)}")
        # import traceback
        # traceback.print_exc()
        return []


def get_container_year_chart_data():
    """Format yearly container data for bar chart"""
    import json

    cache_key = 'container_year_chart_data'
    cached_data = cache.get(cache_key)
    if cached_data:
        # print(f"DEBUG: Returning cached container year chart data")
        return cached_data

    data = get_container_year_summary()

    if not data:
        # print("DEBUG: No data returned from get_container_year_summary()")
        return json.dumps({
            'labels': [],
            'qty_data': []
        })

    # Extract year and quantity
    labels = []
    qty_data = []

    for item in data:
        try:
            year = int(item['YEAR'])
            qty = int(item['QTY']) if item['QTY'] else 0

            labels.append(str(year))
            qty_data.append(qty)

            # print(f"DEBUG: Added year data - Year: {year}, Qty: {qty}")
        except Exception as e:
            # print(f"DEBUG: Error processing item {item}: {str(e)}")
            continue

    # print(f"DEBUG: Chart data prepared - {len(labels)} years")
    result = json.dumps({
        'labels': labels,
        'qty_data': qty_data
    })
    cache.set(cache_key, result, 300)  # Cache for 5 minutes
    return result


def get_handling_demurrage_data():
    """Get Handling & Demurrage charges by day"""
    from django.db import connection

    query = """
        SELECT TRAN_DAY, HI_CHARGES as Handling, DEM_CHARGES as Dem
        FROM TABLE (GET_HI_DEM_LIST)
        ORDER BY TRAN_DAY ASC
    """

    # print(f"DEBUG: Starting get_handling_demurrage_data()")
    # print(f"DEBUG: Query: {query}")

    try:
        with connection.cursor() as cursor:
            # print(f"DEBUG: Executing query...")
            cursor.execute(query)
            # print(f"DEBUG: Query executed successfully")
            columns = [col[0] for col in cursor.description]
            # print(f"DEBUG: Columns found: {columns}")
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            # print(f"DEBUG: Handling & Demurrage data retrieved: {len(data)} records")
            # if data:
            #     print(f"DEBUG: First record: {data[0]}")
            #     print(f"DEBUG: All data: {data}")
            # else:
            #     print(f"DEBUG: WARNING - No data returned!")
            return data
    except Exception as e:
        # print(f"DEBUG: ERROR in get_handling_demurrage_data: {str(e)}")
        # import traceback
        # traceback.print_exc()
        return []


def get_handling_demurrage_chart_data():
    """Format Handling & Demurrage data for dynamic line chart"""
    import json

    cache_key = 'handling_demurrage_chart_data'
    cached_data = cache.get(cache_key)
    if cached_data:
        # print(f"DEBUG: Returning cached H&D chart data")
        return cached_data

    data = get_handling_demurrage_data()

    if not data:
        # print("DEBUG: No data returned from get_handling_demurrage_data()")
        return json.dumps({
            'labels': [],
            'handling_data': [],
            'demurrage_data': []
        })

    # Extract day and charges
    labels = []
    handling_data = []
    demurrage_data = []

    for item in data:
        try:
            day = int(str(item['TRAN_DAY']).strip())
            handling = float(item['HANDLING']) if item['HANDLING'] else 0
            demurrage = float(item['DEM']) if item['DEM'] else 0

            labels.append(str(day))
            handling_data.append(round(handling, 2))
            demurrage_data.append(round(demurrage, 2))

            # print(f"DEBUG: Added data - Day: {day}, Handling: {handling}, Demurrage: {demurrage}")
        except Exception as e:
            # print(f"DEBUG: Error processing item {item}: {str(e)}")
            continue

    # print(f"DEBUG: Chart data prepared - {len(labels)} days")
    result = json.dumps({
        'labels': labels,
        'handling_data': handling_data,
        'demurrage_data': demurrage_data
    })
    cache.set(cache_key, result, 300)  # Cache for 5 minutes
    return result


def get_container_daily_summary():
    """Get container received and shipped by day for chart"""
    from django.db import connection
    import json

    query = """
        SELECT ACTION_DATE, ACTION_DAY, RECVD_QTY, SHIPPED_QTY
        FROM TABLE (GET_RECVD_SHIPPED_DATE_LIST)
        ORDER BY ACTION_DATE ASC
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            # print(f"DEBUG: Container data retrieved: {len(data)} records")
            # if data:
            #     print(f"DEBUG: First record: {data[0]}")
            #     print(f"DEBUG: Columns: {columns}")
            return data
    except Exception as e:
        # print(f"DEBUG: Error in get_container_daily_summary: {str(e)}")
        # import traceback
        # traceback.print_exc()
        return []


def get_container_chart_data():
    """Get formatted data for line chart"""
    import json
    from datetime import datetime

    cache_key = 'container_chart_data'
    cached_data = cache.get(cache_key)
    if cached_data:
        # print(f"DEBUG: Returning cached container chart data")
        return cached_data

    data = get_container_daily_summary()

    if not data:
        # print("DEBUG: No data returned from get_container_daily_summary()")
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
            day = int(str(item['ACTION_DAY']).strip())

            labels.append(str(day))
            recvd_data.append(int(item['RECVD_QTY']) if item['RECVD_QTY'] else 0)
            shipped_data.append(int(item['SHIPPED_QTY']) if item['SHIPPED_QTY'] else 0)

            # print(f"DEBUG: Added data - Day: {day}, Recvd: {item['RECVD_QTY']}, Shipped: {item['SHIPPED_QTY']}")
        except Exception as e:
            # print(f"DEBUG: Error processing item {item}: {str(e)}")
            continue

    # print(f"DEBUG: Chart data prepared - {len(labels)} days with labels: {labels}")
    result = json.dumps({
        'labels': labels,
        'recvd_data': recvd_data,
        'shipped_data': shipped_data
    })
    cache.set(cache_key, result, 300)  # Cache for 5 minutes
    return result


def get_last_24hr_container_summary():
    """Get last 24 hours container receive/shipped/balance summary"""
    import json
    from datetime import datetime, timedelta

    cache_key = 'last_24hr_container_summary'
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data

    data = get_container_daily_summary()

    if not data:
        return json.dumps({
            'received_24hr': 0,
            'shipped_24hr': 0,
            'balance': 0,
            'last_day': 'N/A'
        })

    # Get last entry (most recent day)
    if data:
        last_entry = data[-1]  # Last item in the list
        received_24hr = int(last_entry['RECVD_QTY']) if last_entry['RECVD_QTY'] else 0
        shipped_24hr = int(last_entry['SHIPPED_QTY']) if last_entry['SHIPPED_QTY'] else 0
        balance = received_24hr - shipped_24hr
        last_day = str(last_entry['ACTION_DAY']).strip()

        # print(f"DEBUG: Last 24hr - Day: {last_day}, Received: {received_24hr}, Shipped: {shipped_24hr}, Balance: {balance}")

        result = json.dumps({
            'received_24hr': received_24hr,
            'shipped_24hr': shipped_24hr,
            'balance': balance,
            'last_day': f"Day {last_day}"
        })
        cache.set(cache_key, result, 300)
        return result


def get_last_24hr_hidem_summary():
    """Get last 24 hours handling & demurrage summary"""
    import json

    cache_key = 'last_24hr_hidem_summary'
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data

    data = get_handling_demurrage_data()

    if not data:
        return json.dumps({
            'handling_24hr': 0,
            'demurrage_24hr': 0,
            'total_charges_24hr': 0,
            'last_day': 'N/A'
        })

    # Get last entry (most recent day)
    if data:
        last_entry = data[-1]
        handling_24hr = float(last_entry['HANDLING']) if last_entry['HANDLING'] else 0
        demurrage_24hr = float(last_entry['DEM']) if last_entry['DEM'] else 0
        total_charges = handling_24hr + demurrage_24hr
        last_day = str(last_entry['TRAN_DAY']).strip()

        # print(f"DEBUG: Last 24hr H&D - Day: {last_day}, Handling: {handling_24hr}, Demurrage: {demurrage_24hr}, Total: {total_charges}")

        result = json.dumps({
            'handling_24hr': round(handling_24hr, 2),
            'demurrage_24hr': round(demurrage_24hr, 2),
            'total_charges_24hr': round(total_charges, 2),
            'last_day': f"Day {last_day}"
        })
        cache.set(cache_key, result, 300)
        return result


def get_month_to_date_summary():
    """Get month-to-date container and charge totals"""
    import json

    cache_key = 'month_to_date_summary'
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data

    # Container data
    container_data = get_container_daily_summary()
    total_received = 0
    total_shipped = 0

    if container_data:
        for item in container_data:
            total_received += int(item['RECVD_QTY']) if item['RECVD_QTY'] else 0
            total_shipped += int(item['SHIPPED_QTY']) if item['SHIPPED_QTY'] else 0

    # H&D data
    hidem_data = get_handling_demurrage_data()
    total_handling = 0
    total_demurrage = 0

    if hidem_data:
        for item in hidem_data:
            total_handling += float(item['HANDLING']) if item['HANDLING'] else 0
            total_demurrage += float(item['DEM']) if item['DEM'] else 0

    balance = total_received - total_shipped
    total_charges = total_handling + total_demurrage

    # print(f"DEBUG: MTD Summary - Received: {total_received}, Shipped: {total_shipped}, Balance: {balance}")
    # print(f"DEBUG: MTD H&D - Handling: {total_handling}, Demurrage: {total_demurrage}, Total: {total_charges}")

    result = json.dumps({
        'mtd_received': total_received,
        'mtd_shipped': total_shipped,
        'mtd_balance': balance,
        'mtd_handling': round(total_handling, 2),
        'mtd_demurrage': round(total_demurrage, 2),
        'mtd_total_charges': round(total_charges, 2)
    })
    cache.set(cache_key, result, 300)
    return result


@login_required
def operations_dashboard(request):
    import json

    context = {
        # Card 1: Container Received & Shipped Line Chart
        'container_chart_data': _safe('{}', lambda: get_container_chart_data()),
        # Card 2: Container Received by Year Bar Chart
        'container_year_chart_data': _safe('{}', lambda: get_container_year_chart_data()),
        # Card 3: Handling & Demurrage Charges Line Chart
        'handling_demurrage_chart_data': _safe('{}', lambda: get_handling_demurrage_chart_data()),
        # Summary Cards
        'last_24hr_container': _safe('{}', lambda: get_last_24hr_container_summary()),
        'last_24hr_hidem': _safe('{}', lambda: get_last_24hr_hidem_summary()),
        'month_to_date': _safe('{}', lambda: get_month_to_date_summary()),
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
