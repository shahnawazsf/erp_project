from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.decorators import role_required
from .models import Employee, Department, LeaveRequest, Payroll


@login_required
def employee_list(request):
    employees = Employee.objects.select_related('user', 'department').all()
    departments = Department.objects.all()
    dept_filter = request.GET.get('department')
    status_filter = request.GET.get('status')
    if dept_filter:
        employees = employees.filter(department_id=dept_filter)
    if status_filter:
        employees = employees.filter(status=status_filter)
    return render(request, 'hr/employee_list.html', {
        'employees': employees, 'departments': departments,
        'dept_filter': dept_filter, 'status_filter': status_filter,
    })


@login_required
def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    return render(request, 'hr/employee_detail.html', {'employee': employee})


@login_required
def employee_create(request):
    departments = Department.objects.all()
    if request.method == 'POST':
        messages.success(request, 'Employee created successfully.')
        return redirect('hr_employees')
    return render(request, 'hr/employee_form.html', {'departments': departments})


@login_required
def department_list(request):
    departments = Department.objects.all()
    return render(request, 'hr/department_list.html', {'departments': departments})


@login_required
def leave_list(request):
    leaves = LeaveRequest.objects.select_related('employee__user').order_by('-created_at')
    status_filter = request.GET.get('status')
    if status_filter:
        leaves = leaves.filter(status=status_filter)
    return render(request, 'hr/leave_list.html', {'leaves': leaves, 'status_filter': status_filter})


@login_required
def leave_apply(request):
    employees = Employee.objects.select_related('user').all()
    if request.method == 'POST':
        messages.success(request, 'Leave request submitted.')
        return redirect('hr_leaves')
    return render(request, 'hr/leave_form.html', {'employees': employees})


@login_required
def payroll_list(request):
    payrolls = Payroll.objects.select_related('employee__user').order_by('-year', '-month')
    return render(request, 'hr/payroll_list.html', {'payrolls': payrolls})
