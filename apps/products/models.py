from django.db import models
from django.utils import timezone
from core.models import TimeStampedModel
from categories.models import Category

class UnitType(models.TextChoices):
    KG = 'kg', 'Kilogram (kg)'
    GM = 'gm', 'Gram (gm)'
    PIECE = 'piece', 'Piece (pc)'
    BUNDLE = 'bundle', 'Bundle'

class PriceDisplayType(models.TextChoices):
    INDICATIVE = 'indicative', 'Indicative Price'
    FIXED = 'fixed', 'Fixed Listed Price'
    SUBJECT_TO_CONFIRMATION = 'subject_to_confirmation', 'Price Subject to Confirmation'
    CONTACT_FOR_PRICE = 'contact_for_price', 'Contact for Current Price'

class Product(TimeStampedModel):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products'
    )
    name = models.CharField(max_length=200, db_index=True)
    bangla_name = models.CharField(max_length=200, blank=True, null=True)
    slug = models.SlugField(max_length=220, unique=True, db_index=True)
    short_description = models.CharField(max_length=300, blank=True, null=True)
    full_description = models.TextField(blank=True, null=True)
    
    origin = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        help_text="Catch location, e.g. 'Padma River, Chandpur' or 'Bay of Bengal'"
    )
    freshness_grade = models.CharField(
        max_length=100,
        default='Grade A – Morning Catch',
        help_text="e.g. 'Grade A – Morning Catch', 'Live Catch', 'Deep Sea Fresh'"
    )
    
    unit = models.CharField(
        max_length=20,
        choices=UnitType.choices,
        default=UnitType.KG
    )
    standard_weight_range = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="e.g. '≈ 800g – 1kg (per piece)' or '≈ 1.5 – 2 kg (per piece)'"
    )

    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Indicative or listed price in BDT per unit"
    )
    price_display_type = models.CharField(
        max_length=30,
        choices=PriceDisplayType.choices,
        default=PriceDisplayType.INDICATIVE
    )
    price_notice_label = models.CharField(
        max_length=150,
        default='Indicative Price (Subject to Daily Market Rates)',
        help_text="Label shown on customer card and detail page"
    )
    market_price_updated_at = models.DateTimeField(default=timezone.now)

    min_order_qty = models.DecimalField(max_digits=6, decimal_places=2, default=1.00)
    max_order_qty = models.DecimalField(max_digits=6, decimal_places=2, default=20.00)
    step_qty = models.DecimalField(max_digits=6, decimal_places=2, default=0.50)
    allows_cutting_instructions = models.BooleanField(
        default=True,
        help_text="Whether customer can specify cutting preferences (Curry Cut, Whole, Steak Cut, Gutted)"
    )

    is_active = models.BooleanField(default=True, db_index=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    is_popular = models.BooleanField(default=False, db_index=True)
    is_seasonal = models.BooleanField(default=False, db_index=True)
    is_fresh_arrival = models.BooleanField(default=False, db_index=True)

    views_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.base_price} BDT/{self.unit})"

    @property
    def primary_image_url(self):
        primary = self.images.filter(is_primary=True).first()
        if primary:
            return primary.image_url
        first = self.images.first()
        return first.image_url if first else None


class ProductImage(TimeStampedModel):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image_url = models.URLField(max_length=500)
    alt_text = models.CharField(max_length=200, blank=True, null=True)
    is_primary = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'created_at']

    def __str__(self):
        return f"Image for {self.product.name} ({self.id})"
