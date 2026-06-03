from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .models import Invoice, Expense, ChartOfAccounts, Journal, ContainerNotification
from .forms import ContainerNotificationForm


@login_required
def finance_dashboard(request):
    context = {
        'total_receivable': Invoice.objects.filter(invoice_type='sales', status__in=['sent', 'draft']).aggregate(t=Sum('balance_due'))['t'] or 0,
        'total_payable': Invoice.objects.filter(invoice_type='purchase', status__in=['sent', 'draft']).aggregate(t=Sum('balance_due'))['t'] or 0,
        'pending_expenses': Expense.objects.filter(status='pending').count(),
        'recent_invoices': Invoice.objects.order_by('-created_at')[:5],
        'recent_expenses': Expense.objects.order_by('-created_at')[:5],
    }
    return render(request, 'finance/dashboard.html', context)


@login_required
def invoice_list(request):
    invoices = Invoice.objects.all().order_by('-created_at')
    type_filter = request.GET.get('type')
    status_filter = request.GET.get('status')
    if type_filter:
        invoices = invoices.filter(invoice_type=type_filter)
    if status_filter:
        invoices = invoices.filter(status=status_filter)
    return render(request, 'finance/invoice_list.html', {
        'invoices': invoices, 'type_filter': type_filter, 'status_filter': status_filter
    })


@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    return render(request, 'finance/invoice_detail.html', {'invoice': invoice})


@login_required
def invoice_create(request):
    if request.method == 'POST':
        messages.success(request, 'Invoice created successfully.')
        return redirect('finance_invoices')
    return render(request, 'finance/invoice_form.html')


@login_required
def expense_list(request):
    expenses = Expense.objects.all().order_by('-created_at')
    status_filter = request.GET.get('status')
    if status_filter:
        expenses = expenses.filter(status=status_filter)
    return render(request, 'finance/expense_list.html', {'expenses': expenses, 'status_filter': status_filter})


@login_required
def expense_create(request):
    if request.method == 'POST':
        messages.success(request, 'Expense submitted.')
        return redirect('finance_expenses')
    return render(request, 'finance/expense_form.html')


@login_required
def account_list(request):
    accounts = ChartOfAccounts.objects.filter(is_active=True).order_by('code')
    return render(request, 'finance/account_list.html', {'accounts': accounts})


# ── Container Notification ───────────────────────────────────────────

@login_required
def cn_list(request):
    qs = ContainerNotification.objects.exclude(crn_container_no='').order_by('crn_status', 'crn_container_no')
    return render(request, 'finance/cn_list.html', {'rows': qs})


@login_required
def cn_create(request):
    if request.method == 'POST':
        form = ContainerNotificationForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.crn_status = 0
            obj.save()
            messages.success(request, 'Container notification added.')
            return redirect('cn_list')
    else:
        form = ContainerNotificationForm()
    return render(request, 'finance/cn_form.html', {'form': form, 'action': 'Add'})


@login_required
def cn_edit(request, pk):
    obj  = get_object_or_404(ContainerNotification, pk=pk)
    if request.method == 'POST':
        form = ContainerNotificationForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Container notification updated.')
            return redirect('cn_list')
    else:
        form = ContainerNotificationForm(instance=obj)
    return render(request, 'finance/cn_form.html', {'form': form, 'action': 'Edit'})


# ── Reports ──────────────────────────────────────────────────────────

@login_required
def reports_hub(request):
    return render(request, 'finance/reports_hub.html')


@login_required
def report_vat(request):
    import calendar
    import logging
    from datetime import date
    from django.db import connection

    logger = logging.getLogger(__name__)
    current_year = date.today().year
    current_month = date.today().month
    rows = []
    filters = {}
    generated = False
    filter_mode = 'month'

    if request.method == 'POST':
        filter_mode = request.POST.get('filter_mode', 'month')

        if filter_mode == 'range':
            date_from = request.POST.get('date_from', '')
            date_to   = request.POST.get('date_to', '')
            if date_from and date_to:
                filters = {
                    'date_from': date_from,
                    'date_to':   date_to,
                    'month':     '',
                    'month_label': '',
                }
                generated = True
        else:
            selected = request.POST.get('month', '')
            if selected:
                year, month = int(selected.split('-')[0]), int(selected.split('-')[1])
                last_day = calendar.monthrange(year, month)[1]
                filters = {
                    'month':       selected,
                    'month_label': date(year, month, 1).strftime('%B %Y'),
                    'date_from':   f"{year}-{month:02d}-01",
                    'date_to':     f"{year}-{month:02d}-{last_day}",
                }
                generated = True

        if generated:
            try:
                with connection.cursor() as django_cur:
                    cur = django_cur.cursor.cursor
                    cur.execute("""
                        SELECT DOC_NO, DOC_TYPE, INV_NO, DOC_DATE, POSTING_DATE,
                               VENDOR_CUST_NO, VEND_CUST_NAME, VEND_CUST_VAT_NO,
                               TYPES_OF_GOOODS_SERVICES, TAX_CODE,
                               TAX_BASE_AMOUNT, OUTPUT_INPUT_TAX, GRSOS_AMT_INCL_VAT,
                               LOCAL_CURRENCY, FOREIGN_CURRENCY_AMT, FOREIGN_CURRENCY,
                               POSTING_MONTH
                        FROM VIEW_VAT_STATEMENT@SDRS104
                        WHERE TRUNC(POSTING_DATE) BETWEEN TO_DATE(:d1, 'YYYY-MM-DD')
                                                      AND TO_DATE(:d2, 'YYYY-MM-DD')
                    """, {'d1': filters['date_from'], 'd2': filters['date_to']})
                    cols = [d[0].lower() for d in cur.description]
                    rows = [dict(zip(cols, row)) for row in cur.fetchall()]
            except Exception:
                logger.exception('VAT report query failed')
                messages.error(request, 'Query failed — check server logs.')

    month_names = ['Jan','Feb','Mar','Apr','May','Jun',
                   'Jul','Aug','Sep','Oct','Nov','Dec']
    months = [
        {
            'num':        m + 1,
            'short':      month_names[m],
            'value':      f"{current_year}-{m+1:02d}",
            'is_future':  (m + 1) > current_month,
            'is_current': (m + 1) == current_month,
            'is_selected': filters.get('month') == f"{current_year}-{m+1:02d}",
        }
        for m in range(12)
    ]

    return render(request, 'finance/report_vat.html', {
        'rows': rows,
        'filters': filters,
        'generated': generated,
        'filter_mode': filter_mode,
        'current_year': current_year,
        'current_month': current_month,
        'months': months,
    })


@login_required
def report_customer_invoice(request):
    import logging
    from django.db import connection

    logger = logging.getLogger(__name__)
    rows = []
    filters = {}
    generated = False
    agents = []

    # Always load agent list for the dropdown
    try:
        with connection.cursor() as django_cur:
            cur = django_cur.cursor.cursor
            cur.execute("SELECT am_code, am_name FROM AGENT_MASTER ORDER BY am_name")
            agents = [{'code': row[0], 'name': row[1]} for row in cur.fetchall()]
    except Exception:
        logger.exception('Failed to load AGENT_MASTER')

    if request.method == 'POST':
        filters = {
            'date_from':  request.POST.get('date_from', ''),
            'date_to':    request.POST.get('date_to', ''),
            'agent_code': request.POST.get('agent_code', '').strip().upper(),
        }
        # Resolve agent name for display
        filters['agent_name'] = next(
            (a['name'] for a in agents if a['code'] == filters['agent_code']), ''
        )

        if filters['date_from'] and filters['date_to'] and filters['agent_code']:
            generated = True
            try:
                from datetime import datetime
                with connection.cursor() as django_cur:
                    cur = django_cur.cursor.cursor
                    d1_yyyy_mm_dd = filters['date_from']
                    d2_yyyy_mm_dd = filters['date_to']
                    query = f"""
                        SELECT a.INV_NO, a.INV_DATE, a.CUST_CODE, a.AGENT_CODE, a.COMPANY, a.OSO_NO,
                               a.CHARGE_AMOUNT, a.VAT, a.TOTAL, a.BOLNUMBER, b.BOLNUMBER AS BOLNUMBER_1
                        FROM INV_WEEKLY_REPORT_VIEW a
                        LEFT JOIN (
                            SELECT INV_NO, BOLNUMBER,
                                   ROW_NUMBER() OVER (PARTITION BY INV_NO ORDER BY BOLNUMBER) rn
                            FROM INV_WEEKLY_REPORT_BL_VIEW
                        ) b
                        ON a.INV_NO = b.INV_NO AND b.rn = 1
                        WHERE a.AGENT_CODE = '{filters['agent_code']}'
                        AND SUBSTR(a.INV_DATE, 7, 4) || '-' || SUBSTR(a.INV_DATE, 4, 2) || '-' || SUBSTR(a.INV_DATE, 1, 2) >= '{d1_yyyy_mm_dd}'
                        AND SUBSTR(a.INV_DATE, 7, 4) || '-' || SUBSTR(a.INV_DATE, 4, 2) || '-' || SUBSTR(a.INV_DATE, 1, 2) <= '{d2_yyyy_mm_dd}'
                    """
                    cur.execute(query)
                    cols = [d[0].lower() for d in cur.description]
                    rows = [dict(zip(cols, row)) for row in cur.fetchall()]
            except Exception:
                logger.exception('Customer invoice query failed')
                messages.error(request, 'Query failed — check server logs.')
        else:
            messages.warning(request, 'Agent, Date From and Date To are all required.')

    return render(request, 'finance/report_customer_invoice.html', {
        'rows': rows, 'filters': filters, 'generated': generated, 'agents': agents,
    })
