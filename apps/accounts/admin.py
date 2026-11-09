from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Fish Dock Info', {'fields': ('role', 'phone', 'address', 'notes')}),
    )
    list_display = ['username', 'email', 'phone', 'role', 'is_staff', 'is_active']
    list_filter = ['role', 'is_staff', 'is_active']
