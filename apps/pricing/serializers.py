from rest_framework import serializers
from .models import PriceHistory
from products.models import Product

class PriceHistorySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    changed_by_username = serializers.CharField(source='changed_by.username', read_only=True, default='System')

    class Meta:
        model = PriceHistory
        fields = [
            'id', 'product', 'product_name', 'previous_price', 'new_price',
            'effective_date', 'reason', 'changed_by', 'changed_by_username',
            'notes', 'created_at'
        ]
        read_only_fields = ['id', 'previous_price', 'created_at']

