from rest_framework import serializers
from decimal import Decimal
from .models import Order, OrderItem, OrderStatusHistory, OrderStatus, WhatsAppStatus
from products.models import Product

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_name_snapshot', 'unit_snapshot',
            'standard_weight_range_snapshot', 'quantity', 'unit_price_snapshot',
            'indicative_total', 'final_unit_price', 'final_total',
            'quantity_adjusted', 'adjustment_reason', 'cutting_instruction'
        ]

class OrderStatusHistorySerializer(serializers.ModelSerializer):
    changed_by_name = serializers.CharField(source='changed_by.username', read_only=True, default='System / Customer')

    class Meta:
        model = OrderStatusHistory
        fields = ['id', 'previous_status', 'new_status', 'changed_by_name', 'notes', 'created_at']

class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)
    confirmed_by_name = serializers.CharField(source='confirmed_by.username', read_only=True, default=None)

    class Meta:
        model = Order
        fields = [
            'id', 'order_reference', 'customer_name', 'customer_phone',
            'customer_email', 'delivery_address', 'delivery_area',
            'delivery_city', 'preferred_delivery_slot', 'customer_notes',
            'status', 'whatsapp_status', 'indicative_subtotal', 'delivery_fee',
            'final_confirmed_amount', 'admin_notes', 'confirmed_by_name',
            'confirmed_at', 'items', 'status_history', 'created_at', 'updated_at'
        ]

class OrderItemInputSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    quantity = serializers.DecimalField(max_digits=8, decimal_places=2, min_value=Decimal('0.1'))
    cutting_instruction = serializers.CharField(required=False, default='Whole Fish (Gutted & Cleaned)')

class CreateOrderRequestSerializer(serializers.Serializer):
    customer_name = serializers.CharField(max_length=150)
    customer_phone = serializers.CharField(max_length=25)
    customer_email = serializers.EmailField(required=False, allow_blank=True, default='')
    delivery_address = serializers.CharField()
    delivery_area = serializers.CharField(max_length=100, default='Mirpur, Dhaka')
    delivery_city = serializers.CharField(max_length=60, default='Dhaka')
    preferred_delivery_slot = serializers.CharField(max_length=100, default='Morning (8 AM - 12 PM)')
    customer_notes = serializers.CharField(required=False, allow_blank=True, default='')
    items = OrderItemInputSerializer(many=True, min_length=1)

