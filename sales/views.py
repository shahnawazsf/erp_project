from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from .models import SalesOrder, Customer, SalesOrderItem


@login_required
def sales_dashboard(request):
    context = {
        'total_orders': SalesOrder.objects.count(),
        'confirmed_orders': SalesOrder.objects.filter(status='confirmed').count(),
        'total_customers': Customer.objects.filter(is_active=True).count(),
        'revenue': SalesOrder.objects.filter(status='delivered').aggregate(t=Sum('total'))['t'] or 0,
        'recent_orders': SalesOrder.objects.select_related('customer').order_by('-created_at')[:10],
    }
    return render(request, 'sales/dashboard.html', context)


@login_required
def order_list(request):
    orders = SalesOrder.objects.select_related('customer').order_by('-created_at')
    status_filter = request.GET.get('status')
    search = request.GET.get('search', '')
    if status_filter:
        orders = orders.filter(status=status_filter)
    if search:
        orders = orders.filter(order_number__icontains=search) | orders.filter(customer__name__icontains=search)
    return render(request, 'sales/order_list.html', {
        'orders': orders, 'status_filter': status_filter, 'search': search
    })


@login_required
def order_detail(request, pk):
    order = get_object_or_404(SalesOrder, pk=pk)
    return render(request, 'sales/order_detail.html', {'order': order})


@login_required
def order_create(request):
    customers = Customer.objects.filter(is_active=True)
    if request.method == 'POST':
        messages.success(request, 'Sales order created.')
        return redirect('sales_orders')
    return render(request, 'sales/order_form.html', {'customers': customers})


@login_required
def customer_list(request):
    customers = Customer.objects.all().order_by('name')
    search = request.GET.get('search', '')
    if search:
        customers = customers.filter(name__icontains=search) | customers.filter(code__icontains=search)
    return render(request, 'sales/customer_list.html', {'customers': customers, 'search': search})


@login_required
def customer_create(request):
    if request.method == 'POST':
        messages.success(request, 'Customer added.')
        return redirect('sales_customers')
    return render(request, 'sales/customer_form.html')
