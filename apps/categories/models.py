from django.db import models
from core.models import TimeStampedModel

class Category(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    bangla_name = models.CharField(max_length=150, blank=True, null=True)
    slug = models.SlugField(max_length=150, unique=True)
    description = models.TextField(blank=True, null=True)
    icon_name = models.CharField(
        max_length=50,
        default='fish',
        help_text="Icon identifier such as 'fish', 'waves', 'shrimp', 'crab', etc."
    )
    image_url = models.URLField(max_length=500, blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ['display_order', 'name']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name
