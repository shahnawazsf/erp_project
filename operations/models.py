from django.db import models


class WorkOrder(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.CharField(max_length=50, primary_key=True)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    assigned_to = models.CharField(max_length=100, null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    priority = models.CharField(max_length=20, choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], default='medium')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'WORK_ORDERS'

    def __str__(self):
        return f"WO-{self.id} ({self.status})"


class Maintenance(models.Model):
    MAINTENANCE_TYPE_CHOICES = [
        ('preventive', 'Preventive'),
        ('corrective', 'Corrective'),
        ('predictive', 'Predictive'),
    ]

    id = models.CharField(max_length=50, primary_key=True)
    equipment_name = models.CharField(max_length=200)
    maintenance_type = models.CharField(max_length=20, choices=MAINTENANCE_TYPE_CHOICES)
    scheduled_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    description = models.TextField()
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'MAINTENANCE'

    def __str__(self):
        return f"{self.equipment_name} - {self.maintenance_type}"


class OperationalMetric(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    metric_name = models.CharField(max_length=200)
    metric_value = models.DecimalField(max_digits=12, decimal_places=2)
    measurement_date = models.DateField()
    unit = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'OPERATIONAL_METRICS'

    def __str__(self):
        return f"{self.metric_name}: {self.metric_value} {self.unit}"
