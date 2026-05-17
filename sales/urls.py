from django.urls import path
from . import views

urlpatterns = [
    path('', views.sales_dashboard, name='sales_dashboard'),
    path('orders/', views.order_list, name='sales_orders'),
    path('orders/add/', views.order_create, name='sales_order_create'),
    path('orders/<int:pk>/', views.order_detail, name='sales_order_detail'),
    path('customers/', views.customer_list, name='sales_customers'),
    path('customers/add/', views.customer_create, name='sales_customer_create'),
]
