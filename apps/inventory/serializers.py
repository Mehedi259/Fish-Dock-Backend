from rest_framework import serializers
from .models import Inventory, InventoryTransaction

class InventoryTransactionSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True, default='System')

    class Meta:
        model = InventoryTransaction
        fields = [
            'id', 'inventory', 'transaction_type', 'quantity', 'balance_after',
            'reason', 'created_by', 'created_by_username', 'notes', 'created_at'
        ]

class InventorySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_slug = serializers.CharField(source='product.slug', read_only=True)
    product_unit = serializers.CharField(source='product.unit', read_only=True)
    category_name = serializers.CharField(source='product.category.name', read_only=True)
    transactions = InventoryTransactionSerializer(many=True, read_only=True)

    class Meta:
        model = Inventory
        fields = [
            'id', 'product', 'product_name', 'product_slug', 'product_unit',
            'category_name', 'track_stock', 'available_quantity',
            'reserved_quantity', 'low_stock_threshold', 'is_out_of_stock',
            'transactions', 'updated_at'
        ]

