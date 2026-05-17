from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('hr', 'HR'),
        ('accountant', 'Accountant'),
        ('sales', 'Sales'),
        ('purchasing', 'Purchasing'),
        ('warehouse', 'Warehouse'),
        ('employee', 'Employee'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"


class Module(models.Model):
    name = models.CharField(max_length=100, unique=True)
    label = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Bootstrap icon class")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'label']

    def __str__(self):
        return self.label


class SubModule(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='sub_modules')
    name = models.CharField(max_length=100)
    label = models.CharField(max_length=100)
    view_name = models.CharField(max_length=100, help_text="Django view name (e.g., 'hr_employees')")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['module', 'order', 'label']
        unique_together = ('module', 'name')

    def __str__(self):
        return f"{self.module.label} > {self.label}"


class ModulePermission(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='permissions')
    role = models.CharField(max_length=20, choices=User.ROLE_CHOICES)
    can_view = models.BooleanField(default=True)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('module', 'role')

    def __str__(self):
        return f"{self.module.label} - {self.get_role_display()}"


class SubModulePermission(models.Model):
    sub_module = models.ForeignKey(SubModule, on_delete=models.CASCADE, related_name='permissions')
    role = models.CharField(max_length=20, choices=User.ROLE_CHOICES)
    can_access = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('sub_module', 'role')

    def __str__(self):
        return f"{self.sub_module} - {self.get_role_display()}"
