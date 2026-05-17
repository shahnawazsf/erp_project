from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Module, SubModule, ModulePermission, SubModulePermission
from .permissions import clear_permission_cache


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active')
    list_filter = ('role', 'is_active', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('ERP Info', {'fields': ('role', 'phone', 'avatar')}),
    )


class SubModuleInline(admin.TabularInline):
    model = SubModule
    extra = 1
    fields = ('name', 'label', 'view_name', 'is_active', 'order')


class ModulePermissionInline(admin.TabularInline):
    model = ModulePermission
    extra = 1
    fields = ('role', 'can_view', 'can_edit', 'can_delete')


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('label', 'name', 'is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('name', 'label')
    inlines = [SubModuleInline, ModulePermissionInline]
    fields = ('name', 'label', 'description', 'icon', 'is_active', 'order')
    readonly_fields = ('name',)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        clear_permission_cache()


@admin.register(SubModule)
class SubModuleAdmin(admin.ModelAdmin):
    list_display = ('label', 'module', 'view_name', 'is_active', 'order')
    list_filter = ('module', 'is_active')
    search_fields = ('name', 'label', 'view_name')
    fields = ('module', 'name', 'label', 'view_name', 'description', 'is_active', 'order')
    ordering = ('module', 'order')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        clear_permission_cache()


class SubModulePermissionInline(admin.TabularInline):
    model = SubModulePermission
    extra = 1
    fields = ('role', 'can_access')


@admin.register(ModulePermission)
class ModulePermissionAdmin(admin.ModelAdmin):
    list_display = ('module', 'role', 'can_view', 'can_edit', 'can_delete')
    list_filter = ('module', 'role', 'can_view', 'can_edit', 'can_delete')
    search_fields = ('module__label', 'role')
    fields = ('module', 'role', 'can_view', 'can_edit', 'can_delete')
    ordering = ('module', 'role')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        clear_permission_cache()

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        clear_permission_cache()


@admin.register(SubModulePermission)
class SubModulePermissionAdmin(admin.ModelAdmin):
    list_display = ('sub_module', 'role', 'can_access', 'created_at')
    list_filter = ('sub_module__module', 'role', 'can_access')
    search_fields = ('sub_module__label', 'sub_module__module__label', 'role')
    fields = ('sub_module', 'role', 'can_access')
    ordering = ('sub_module__module', 'sub_module', 'role')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        clear_permission_cache()

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        clear_permission_cache()
