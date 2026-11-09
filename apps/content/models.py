from django.db import models
from core.models import TimeStampedModel

class Banner(TimeStampedModel):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True, null=True)
    badge_text = models.CharField(max_length=60, default='Daily Catch')
    image_url = models.URLField(max_length=500)
    button_text = models.CharField(max_length=50, default='Shop Now')
    link_url = models.CharField(max_length=255, default='/products')
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order', '-created_at']

    def __str__(self):
        return self.title

class Testimonial(TimeStampedModel):
    customer_name = models.CharField(max_length=120)
    customer_area = models.CharField(max_length=120, default='Mirpur, Dhaka')
    rating = models.PositiveSmallIntegerField(default=5)
    comment = models.TextField()
    avatar_url = models.URLField(max_length=500, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.customer_name} ({self.rating}★)"

class FAQ(TimeStampedModel):
    question = models.CharField(max_length=300)
    answer = models.TextField()
    category = models.CharField(max_length=80, default='Ordering & Delivery')
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order', 'id']
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'

    def __str__(self):
        return self.question
