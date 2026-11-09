from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from core.models import TimeStampedModel
from products.models import Product

User = get_user_model()

class PriceHistory(TimeStampedModel):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='price_history'
    )
    previous_price = models.DecimalField(max_digits=10, decimal_places=2)
    new_price = models.DecimalField(max_digits=10, decimal_places=2)
    effective_date = models.DateTimeField(default=timezone.now)
    reason = models.CharField(
        max_length=255,
        default='Daily wholesale market rate update',
        help_text="Reason for price adjustment (e.g. morning landing rate, storm in bay, festival demand)"
    )
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='price_changes'
    )
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-effective_date']

    def __str__(self):
        return f"{self.product.name}: {self.previous_price} -> {self.new_price} ({self.effective_date.strftime('%Y-%m-%d')})"
