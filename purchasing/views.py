from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .models import PurchaseOrder, Supplier


@login_required
def purchasing_dashboard(request):
    context = {
        'total_pos': PurchaseOrder.objects.count(),
        'pending_pos': PurchaseOrder.objects.filter(status__in=['draft', 'sent']).count(),
        'total_suppliers': Supplier.objects.filter(is_active=True).count(),
        'total_spent': PurchaseOrder.objects.filter(status='received').aggregate(t=Sum('total'))['t'] or 0,
        'recent_pos': PurchaseOrder.objects.select_related('supplier').order_by('-created_at')[:10],
    }
    return render(request, 'purchasing/dashboard.html', context)


@login_required
def po_list(request):
    orders = PurchaseOrder.objects.select_related('supplier').order_by('-created_at')
    status_filter = request.GET.get('status')
    search = request.GET.get('search', '')
    if status_filter:
        orders = orders.filter(status=status_filter)
    if search:
        orders = orders.filter(order_number__icontains=search) | orders.filter(supplier__name__icontains=search)
    return render(request, 'purchasing/po_list.html', {
        'orders': orders, 'status_filter': status_filter, 'search': search
    })


@login_required
def po_detail(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    return render(request, 'purchasing/po_detail.html', {'order': order})


@login_required
def po_create(request):
    suppliers = Supplier.objects.filter(is_active=True)
    if request.method == 'POST':
        messages.success(request, 'Purchase order created.')
        return redirect('purchasing_orders')
    return render(request, 'purchasing/po_form.html', {'suppliers': suppliers})


@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all().order_by('name')
    search = request.GET.get('search', '')
    if search:
        suppliers = suppliers.filter(name__icontains=search) | suppliers.filter(code__icontains=search)
    return render(request, 'purchasing/supplier_list.html', {'suppliers': suppliers, 'search': search})


@login_required
def supplier_create(request):
    if request.method == 'POST':
        messages.success(request, 'Supplier added.')
        return redirect('purchasing_suppliers')
    return render(request, 'purchasing/supplier_form.html')
