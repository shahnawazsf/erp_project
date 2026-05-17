from django.urls import path
from . import views

urlpatterns = [
    path('', views.purchasing_dashboard, name='purchasing_dashboard'),
    path('orders/', views.po_list, name='purchasing_orders'),
    path('orders/add/', views.po_create, name='purchasing_order_create'),
    path('orders/<int:pk>/', views.po_detail, name='purchasing_order_detail'),
    path('suppliers/', views.supplier_list, name='purchasing_suppliers'),
    path('suppliers/add/', views.supplier_create, name='purchasing_supplier_create'),
]
