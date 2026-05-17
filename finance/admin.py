from django.contrib import admin
from .models import ChartOfAccounts, Journal, JournalEntry, Invoice, Expense


@admin.register(ChartOfAccounts)
class ChartOfAccountsAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'account_type', 'is_active')
    list_filter = ('account_type', 'is_active')
    search_fields = ('code', 'name')


class JournalEntryInline(admin.TabularInline):
    model = JournalEntry
    extra = 2


@admin.register(Journal)
class JournalAdmin(admin.ModelAdmin):
    list_display = ('reference', 'date', 'description', 'status')
    list_filter = ('status',)
    inlines = [JournalEntryInline]


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'invoice_type', 'party_name', 'total_amount', 'paid_amount', 'status')
    list_filter = ('invoice_type', 'status')
    search_fields = ('invoice_number', 'party_name')


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'amount', 'date', 'submitted_by', 'status')
    list_filter = ('status', 'category')
