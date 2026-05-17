from django.urls import path
from . import views

urlpatterns = [
    path('', views.employee_list, name='hr_employees'),
    path('departments/', views.department_list, name='hr_departments'),
    path('employees/add/', views.employee_create, name='hr_employee_create'),
    path('employees/<int:pk>/', views.employee_detail, name='hr_employee_detail'),
    path('leaves/', views.leave_list, name='hr_leaves'),
    path('leaves/apply/', views.leave_apply, name='hr_leave_apply'),
    path('payroll/', views.payroll_list, name='hr_payroll'),
]
