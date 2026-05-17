from django.contrib import admin
from .models import Customer, SalesOrder, SalesOrderItem


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'email', 'phone', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('code', 'name', 'email')


class SalesOrderItemInline(admin.TabularInline):
    model = SalesOrderItem
    extra = 1


@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer', 'order_date', 'total', 'status')
    list_filter = ('status',)
    search_fields = ('order_number', 'customer__name')
    inlines = [SalesOrderItemInline]
