from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import random
from core.models import TimeStampedModel
from products.models import Product

User = get_user_model()

class OrderStatus(models.TextChoices):
    PENDING_CONFIRMATION = 'pending_confirmation', 'Pending Confirmation'
    AWAITING_CUSTOMER_RESPONSE = 'awaiting_customer_response', 'Awaiting Customer Response'
    PRICE_CONFIRMED = 'price_confirmed', 'Price Confirmed'
    CONFIRMED = 'confirmed', 'Confirmed'
    PROCESSING = 'processing', 'Processing & Cutting'
    READY_FOR_DELIVERY = 'ready_for_delivery', 'Ready for Delivery'
    OUT_FOR_DELIVERY = 'out_for_delivery', 'Out for Delivery'
    DELIVERED = 'delivered', 'Delivered'
    CANCELLED = 'cancelled', 'Cancelled'
    REJECTED = 'rejected', 'Rejected'

class WhatsAppStatus(models.TextChoices):
    NOT_CONTACTED = 'not_contacted', 'Not Contacted'
    CHAT_INITIATED = 'chat_initiated', 'Chat Initiated'
    PRICE_QUOTED = 'price_quoted', 'Price Quoted'
    CONFIRMED_VIA_WHATSAPP = 'confirmed_via_whatsapp', 'Confirmed via WhatsApp'
    UNRESPONSIVE = 'unresponsive', 'Unresponsive'

class Order(TimeStampedModel):
    order_reference = models.CharField(
        max_length=32,
        unique=True,
        db_index=True,
        help_text="Unique customer-facing order ID (e.g. FD-2026-1001)"
    )
    customer_name = models.CharField(max_length=150)
    customer_phone = models.CharField(max_length=25, db_index=True)
    customer_email = models.EmailField(blank=True, null=True)
    delivery_address = models.TextField()
    delivery_area = models.CharField(
        max_length=100,
        default='Mirpur, Dhaka',
        help_text="Neighborhood or area for logistics dispatch"
    )
    delivery_city = models.CharField(max_length=60, default='Dhaka')
    preferred_delivery_slot = models.CharField(
        max_length=100,
        default='Morning (8 AM - 12 PM)',
        help_text="Morning, Afternoon, Evening, or Express"
    )
    customer_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Customer instructions, special cleaning/cutting requests"
    )

    status = models.CharField(
        max_length=40,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING_CONFIRMATION,
        db_index=True
    )
    whatsapp_status = models.CharField(
        max_length=40,
        choices=WhatsAppStatus.choices,
        default=WhatsAppStatus.NOT_CONTACTED,
        db_index=True
    )

    indicative_subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text="Sum of indicative item prices at time of request"
    )
    delivery_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=60.00
    )
    final_confirmed_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Actual finalized price agreed with customer via WhatsApp"
    )

    admin_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Internal staff notes, e.g. 'Customer requested 2 big pieces'"
    )
    confirmed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='confirmed_orders'
    )
    confirmed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    @classmethod
    def generate_order_reference(cls):
        year = timezone.now().year
        rand = random.randint(1000, 9999)
        ref = f"FD-{year}-{rand}"
        while cls.objects.filter(order_reference=ref).exists():
            rand = random.randint(1000, 9999)
            ref = f"FD-{year}-{rand}"
        return ref

    def __str__(self):
        return f"{self.order_reference} - {self.customer_name} ({self.get_status_display()})"


class OrderItem(TimeStampedModel):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_items'
    )
    product_name_snapshot = models.CharField(max_length=200)
    unit_snapshot = models.CharField(max_length=20, default='kg')
    standard_weight_range_snapshot = models.CharField(max_length=100, blank=True, null=True)
    
    quantity = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Quantity or weight in specified unit"
    )
    unit_price_snapshot = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Indicative unit price when order was submitted"
    )
    indicative_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00
    )

    # Final negotiated values by Admin via WhatsApp
    final_unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Final price agreed per unit"
    )
    final_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Final amount for this item"
    )
    quantity_adjusted = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Adjusted weight after weighing exact fresh fish"
    )
    adjustment_reason = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="e.g. 'Padma Ilish was exactly 1.15 kg'"
    )
    cutting_instruction = models.CharField(
        max_length=100,
        default='Whole Fish (Gutted & Cleaned)',
        help_text="e.g. 'Whole', 'Curry Cut', 'Steak Cut', 'Cleaned'"
    )

    def __str__(self):
        return f"{self.product_name_snapshot} ({self.quantity} {self.unit_snapshot}) in {self.order.order_reference}"


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='status_history'
    )
    previous_status = models.CharField(max_length=40, blank=True, null=True)
    new_status = models.CharField(max_length=40)
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order.order_reference}: {self.previous_status} -> {self.new_status} at {self.created_at}"
