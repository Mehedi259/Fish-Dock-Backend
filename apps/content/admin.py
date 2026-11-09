from django.contrib import admin
from .models import Banner, Testimonial, FAQ

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'badge_text', 'display_order', 'is_active']

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'customer_area', 'rating', 'is_active']

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'display_order', 'is_active']
