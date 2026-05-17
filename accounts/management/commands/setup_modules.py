from django.core.management.base import BaseCommand
from accounts.models import Module, SubModule, ModulePermission, SubModulePermission, User


class Command(BaseCommand):
    help = 'Setup initial modules, sub-modules, and permissions'

    def handle(self, *args, **options):
        self.stdout.write('Setting up modules and permissions...')

        modules_data = {
            'hr': {
                'label': 'Human Resources',
                'description': 'Employee management, leaves, payroll',
                'icon': 'bi-people',
                'order': 1,
                'sub_modules': [
                    {'name': 'employees', 'label': 'Employees', 'view_name': 'hr_employees'},
                    {'name': 'departments', 'label': 'Departments', 'view_name': 'hr_departments'},
                    {'name': 'leaves', 'label': 'Leave Requests', 'view_name': 'hr_leaves'},
                    {'name': 'payroll', 'label': 'Payroll', 'view_name': 'hr_payroll'},
                ]
            },
            'inventory': {
                'label': 'Inventory',
                'description': 'Products, stock, warehouse management',
                'icon': 'bi-box',
                'order': 2,
                'sub_modules': [
                    {'name': 'products', 'label': 'Products', 'view_name': 'inventory_products'},
                    {'name': 'stock', 'label': 'Stock', 'view_name': 'inventory_stock'},
                    {'name': 'movements', 'label': 'Stock Movements', 'view_name': 'inventory_movements'},
                    {'name': 'warehouses', 'label': 'Warehouses', 'view_name': 'inventory_warehouses'},
                ]
            },
            'finance': {
                'label': 'Finance',
                'description': 'Invoices, expenses, accounting',
                'icon': 'bi-cash-coin',
                'order': 3,
                'sub_modules': [
                    {'name': 'invoices', 'label': 'Invoices', 'view_name': 'finance_invoices'},
                    {'name': 'expenses', 'label': 'Expenses', 'view_name': 'finance_expenses'},
                    {'name': 'accounts', 'label': 'Chart of Accounts', 'view_name': 'finance_accounts'},
                    {'name': 'reports', 'label': 'Reports', 'view_name': 'finance_reports'},
                ]
            },
            'sales': {
                'label': 'Sales',
                'description': 'Orders, customers, sales tracking',
                'icon': 'bi-graph-up',
                'order': 4,
                'sub_modules': [
                    {'name': 'orders', 'label': 'Sales Orders', 'view_name': 'sales_orders'},
                    {'name': 'customers', 'label': 'Customers', 'view_name': 'sales_customers'},
                ]
            },
            'purchasing': {
                'label': 'Purchasing',
                'description': 'Purchase orders, suppliers',
                'icon': 'bi-basket',
                'order': 5,
                'sub_modules': [
                    {'name': 'orders', 'label': 'Purchase Orders', 'view_name': 'purchasing_orders'},
                    {'name': 'suppliers', 'label': 'Suppliers', 'view_name': 'purchasing_suppliers'},
                ]
            },
        }

        # Create modules and sub-modules
        for module_name, module_info in modules_data.items():
            module, created = Module.objects.get_or_create(
                name=module_name,
                defaults={
                    'label': module_info['label'],
                    'description': module_info['description'],
                    'icon': module_info['icon'],
                    'order': module_info['order'],
                    'is_active': True,
                }
            )
            status = 'Created' if created else 'Found'
            self.stdout.write(f'{status} module: {module.label}')

            # Create sub-modules
            for sub_info in module_info['sub_modules']:
                sub_module, sub_created = SubModule.objects.get_or_create(
                    module=module,
                    name=sub_info['name'],
                    defaults={
                        'label': sub_info['label'],
                        'view_name': sub_info['view_name'],
                        'is_active': True,
                    }
                )
                sub_status = 'Created' if sub_created else 'Found'
                self.stdout.write(f'  {sub_status} sub-module: {sub_module.label}')

        # Setup default permissions for roles
        roles = ['admin', 'manager', 'hr', 'accountant', 'sales', 'purchasing', 'warehouse', 'employee']

        # Default role -> module access mapping
        role_permissions = {
            'admin': {
                'hr': {'can_view': True, 'can_edit': True, 'can_delete': True},
                'inventory': {'can_view': True, 'can_edit': True, 'can_delete': True},
                'finance': {'can_view': True, 'can_edit': True, 'can_delete': True},
                'sales': {'can_view': True, 'can_edit': True, 'can_delete': True},
                'purchasing': {'can_view': True, 'can_edit': True, 'can_delete': True},
            },
            'hr': {
                'hr': {'can_view': True, 'can_edit': True, 'can_delete': False},
            },
            'accountant': {
                'finance': {'can_view': True, 'can_edit': True, 'can_delete': False},
            },
            'sales': {
                'sales': {'can_view': True, 'can_edit': True, 'can_delete': False},
            },
            'purchasing': {
                'purchasing': {'can_view': True, 'can_edit': True, 'can_delete': False},
            },
            'warehouse': {
                'inventory': {'can_view': True, 'can_edit': True, 'can_delete': False},
            },
        }

        for role, module_perms in role_permissions.items():
            for module_name, perms in module_perms.items():
                try:
                    module = Module.objects.get(name=module_name)
                    perm, created = ModulePermission.objects.get_or_create(
                        module=module,
                        role=role,
                        defaults=perms
                    )
                    status = 'Created' if created else 'Updated'
                    self.stdout.write(f'{status} permission: {module.label} -> {role}')
                except Module.DoesNotExist:
                    self.stdout.write(f'Module {module_name} not found', self.style.ERROR)

        self.stdout.write(self.style.SUCCESS('✓ Module setup complete!'))
        self.stdout.write('Go to /admin/accounts/module/ to manage modules and permissions.')
