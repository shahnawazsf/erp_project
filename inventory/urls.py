from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='inventory_products'),
    path('products/add/', views.product_create, name='inventory_product_create'),
    path('products/<int:pk>/', views.product_detail, name='inventory_product_detail'),
    path('stock/', views.stock_list, name='inventory_stock'),
    path('movements/', views.movement_list, name='inventory_movements'),
    path('warehouses/', views.warehouse_list, name='inventory_warehouses'),
]
