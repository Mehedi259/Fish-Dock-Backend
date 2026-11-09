from django.db import models
from django.contrib.auth import get_user_model
from core.models import TimeStampedModel
from products.models import Product

User = get_user_model()

class TransactionType(models.TextChoices):
    RESTOCK = 'restock', 'Morning Catch Restock'
    ORDER_RESERVATION = 'order_reservation', 'Order Reservation'
    ORDER_DEDUCTION = 'order_deduction', 'Order Dispatch Deduction'
    MANUAL_ADJUSTMENT = 'manual_adjustment', 'Manual Inventory Adjustment'
    SPOILAGE_WASTE = 'spoilage_waste', 'Fish Spoilage / Weight Loss'

class Inventory(TimeStampedModel):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name='inventory'
    )
    track_stock = models.BooleanField(
        default=True,
        help_text="Enable or disable stock tracking for this product"
    )
    available_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=50.00
    )
    reserved_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    low_stock_threshold = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=5.00
    )
    is_out_of_stock = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.track_stock:
            self.is_out_of_stock = self.available_quantity <= 0
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Inventory for {self.product.name}: {self.available_quantity} {self.product.unit}"


class InventoryTransaction(TimeStampedModel):
    inventory = models.ForeignKey(
        Inventory,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    transaction_type = models.CharField(
        max_length=30,
        choices=TransactionType.choices,
        default=TransactionType.RESTOCK
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    balance_after = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=255)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.inventory.product.name} {self.transaction_type}: {self.quantity}"
