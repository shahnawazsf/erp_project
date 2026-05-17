from django.urls import path
from . import views

urlpatterns = [
    path('', views.finance_dashboard, name='finance_dashboard'),
    path('invoices/', views.invoice_list, name='finance_invoices'),
    path('invoices/add/', views.invoice_create, name='finance_invoice_create'),
    path('invoices/<int:pk>/', views.invoice_detail, name='finance_invoice_detail'),
    path('expenses/', views.expense_list, name='finance_expenses'),
    path('expenses/add/', views.expense_create, name='finance_expense_create'),
    path('accounts/', views.account_list, name='finance_accounts'),
    path('container-notification/', views.cn_list, name='cn_list'),
    path('container-notification/add/', views.cn_create, name='cn_create'),
    path('container-notification/<str:pk>/edit/', views.cn_edit, name='cn_edit'),
    # Reports
    path('reports/', views.reports_hub, name='finance_reports'),
    path('reports/vat/', views.report_vat, name='report_vat'),
    path('reports/customer-invoice/', views.report_customer_invoice, name='report_customer_invoice'),
]
