from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from .models import WorkOrder, Maintenance, OperationalMetric


@login_required
def operations_dashboard(request):
    context = {
        'total_work_orders': WorkOrder.objects.count(),
        'active_work_orders': WorkOrder.objects.filter(status__in=['scheduled', 'in_progress']).count(),
        'completed_work_orders': WorkOrder.objects.filter(status='completed').count(),
        'pending_maintenance': Maintenance.objects.filter(completed_date__isnull=True).count(),
        'total_maintenance_cost': Maintenance.objects.filter(completed_date__isnull=False).aggregate(total=Sum('cost'))['total'] or 0,
        'recent_work_orders': list(WorkOrder.objects.order_by('-created_at')[:5]),
        'recent_maintenance': list(Maintenance.objects.order_by('-created_date')[:5]),
    }
    return render(request, 'operations/dashboard.html', context)


@login_required
def work_orders_list(request):
    work_orders = WorkOrder.objects.all().order_by('-created_at')
    context = {'work_orders': work_orders}
    return render(request, 'operations/work_orders_list.html', context)


@login_required
def maintenance_list(request):
    maintenance = Maintenance.objects.all().order_by('-scheduled_date')
    context = {'maintenance': maintenance}
    return render(request, 'operations/maintenance_list.html', context)
