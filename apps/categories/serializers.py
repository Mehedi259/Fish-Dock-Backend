from rest_framework import serializers
from .models import Category

class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'bangla_name', 'slug', 'description',
            'icon_name', 'image_url', 'display_order', 'is_active',
            'product_count', 'created_at', 'updated_at'
        ]

    def get_product_count(self, obj):
        if hasattr(obj, 'products'):
            return obj.products.filter(is_active=True).count()
        return 0

