from django.contrib.auth.models import AbstractUser
from django.db import models

class UserRole(models.TextChoices):
    SUPER_ADMIN = 'super_admin', 'Super Admin'
    ADMIN = 'admin', 'Administrator'
    ORDER_MANAGER = 'order_manager', 'Order Manager'
    PRODUCT_MANAGER = 'product_manager', 'Product Manager'
    INVENTORY_MANAGER = 'inventory_manager', 'Inventory Manager'
    SUPPORT_AGENT = 'support_agent', 'Support Agent'
    CUSTOMER = 'customer', 'Customer'

class User(AbstractUser):
    role = models.CharField(
        max_length=30,
        choices=UserRole.choices,
        default=UserRole.CUSTOMER,
        db_index=True
    )
    phone = models.CharField(max_length=20, blank=True, null=True, unique=True)
    address = models.TextField(blank=True, null=True)
    avatar_url = models.URLField(max_length=500, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    @property
    def is_admin_or_staff(self):
        return self.is_superuser or self.is_staff or self.role in [
            UserRole.SUPER_ADMIN,
            UserRole.ADMIN,
            UserRole.ORDER_MANAGER,
            UserRole.PRODUCT_MANAGER,
            UserRole.INVENTORY_MANAGER,
            UserRole.SUPPORT_AGENT
        ]

    def save(self, *args, **kwargs):
        # Automatically grant staff status for non-customer admin roles
        if self.role != UserRole.CUSTOMER:
            self.is_staff = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
