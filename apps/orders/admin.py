from django.contrib import admin
from .models import Order, OrderItem, OrderStatusHistory

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ['product_name_snapshot', 'quantity', 'unit_snapshot', 'unit_price_snapshot', 'indicative_total', 'final_unit_price', 'final_total', 'quantity_adjusted', 'cutting_instruction']

class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ['previous_status', 'new_status', 'changed_by', 'notes', 'created_at']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_reference', 'customer_name', 'customer_phone', 'status', 'whatsapp_status', 'indicative_subtotal', 'final_confirmed_amount', 'created_at']
    list_filter = ['status', 'whatsapp_status', 'delivery_area', 'created_at']
    search_fields = ['order_reference', 'customer_name', 'customer_phone']
    inlines = [OrderItemInline, OrderStatusHistoryInline]
