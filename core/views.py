from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.urls import reverse


def _safe(default, fn, *args, **kwargs):
    """Run fn(); return default if any DB error occurs (e.g. table missing)."""
    try:
        return fn(*args, **kwargs)
    except Exception:
        return default


@login_required
def dashboard(request):
    return redirect('operations:dashboard')


@login_required
def core_dashboard(request):
    from hr.models import Employee, LeaveRequest
    from inventory.models import Product
    from sales.models import SalesOrder, Customer
    from purchasing.models import PurchaseOrder, Supplier
    from finance.models import Invoice, Expense

    context = {
        'total_employees':   _safe(0, lambda: Employee.objects.filter(status='active').count()),
        'total_products':    _safe(0, lambda: Product.objects.filter(is_active=True).count()),
        'total_customers':   _safe(0, lambda: Customer.objects.filter(is_active=True).count()),
        'total_suppliers':   _safe(0, lambda: Supplier.objects.filter(is_active=True).count()),
        'pending_leaves':    _safe(0, lambda: LeaveRequest.objects.filter(status='pending').count()),
        'low_stock_products': _safe([], lambda: [p for p in Product.objects.filter(is_active=True) if p.is_low_stock]),
        'recent_sales':      _safe([], lambda: list(SalesOrder.objects.select_related('customer').order_by('-created_at')[:5])),
        'recent_purchases':  _safe([], lambda: list(PurchaseOrder.objects.select_related('supplier').order_by('-created_at')[:5])),
        'pending_invoices':  _safe(0, lambda: Invoice.objects.filter(status__in=['draft', 'sent']).count()),
        'pending_expenses':  _safe(0, lambda: Expense.objects.filter(status='pending').count()),
        'sales_total':       _safe(0, lambda: SalesOrder.objects.filter(status='delivered').aggregate(t=Sum('total'))['t'] or 0),
        'purchase_total':    _safe(0, lambda: PurchaseOrder.objects.filter(status='received').aggregate(t=Sum('total'))['t'] or 0),
    }
    return render(request, 'core/dashboard.html', context)
