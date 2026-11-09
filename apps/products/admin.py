from django.contrib import admin
from .models import Product, ProductImage

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'base_price', 'unit', 'price_display_type', 'is_active', 'is_featured', 'is_popular']
    list_filter = ['category', 'unit', 'price_display_type', 'is_active', 'is_featured', 'is_popular']
    search_fields = ['name', 'bangla_name', 'origin']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image_url', 'is_primary', 'display_order']
