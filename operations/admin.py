from django.contrib import admin
from .models import WorkOrder, Maintenance, OperationalMetric


@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'priority', 'assigned_to', 'created_at')
    list_filter = ('status', 'priority', 'created_at')
    search_fields = ('id', 'description', 'assigned_to')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'equipment_name', 'maintenance_type', 'scheduled_date', 'status', 'cost')
    list_filter = ('maintenance_type', 'status', 'scheduled_date')
    search_fields = ('equipment_name', 'description')
    readonly_fields = ('created_at',)


@admin.register(OperationalMetric)
class OperationalMetricAdmin(admin.ModelAdmin):
    list_display = ('id', 'metric_name', 'metric_value', 'unit', 'measurement_date')
    list_filter = ('metric_name', 'measurement_date')
    search_fields = ('metric_name',)
    readonly_fields = ('created_at',)
