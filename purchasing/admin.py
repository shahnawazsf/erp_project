from django.contrib import admin
from .models import Supplier, PurchaseOrder, PurchaseOrderItem


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'email', 'phone', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('code', 'name')


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'supplier', 'order_date', 'total', 'status')
    list_filter = ('status',)
    search_fields = ('order_number', 'supplier__name')
    inlines = [PurchaseOrderItemInline]
