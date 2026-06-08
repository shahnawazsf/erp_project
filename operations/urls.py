from django.urls import path
from . import views

app_name = 'operations'

urlpatterns = [
    path('', views.operations_dashboard, name='dashboard'),
    path('work-orders/', views.work_orders_list, name='work_orders_list'),
    path('maintenance/', views.maintenance_list, name='maintenance_list'),
]
