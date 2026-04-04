from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Domain: users | Purpose: Admin interface configuration for User management

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Customized Admin interface for the Zorvyn User model.
    """
    model = User
    # Display these columns in the list view
    list_display = ("id", "username", "email", "role", "is_active", "is_staff")
    # Quick filters on the sidebar
    list_filter = ("role", "is_active", "is_staff")
    
    # Define fields for the edit form
    fieldsets = UserAdmin.fieldsets + (
        ("RBAC Permissions", {"fields": ("role",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("RBAC Permissions", {"fields": ("role",)}),
    )
    ordering = ("username",)
