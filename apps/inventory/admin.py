from django.contrib import admin
from .models import Inventory, InventoryTransaction

class InventoryTransactionInline(admin.TabularInline):
    model = InventoryTransaction
    extra = 0
    readonly_fields = ['transaction_type', 'quantity', 'balance_after', 'reason', 'created_by', 'created_at']

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ['product', 'available_quantity', 'reserved_quantity', 'low_stock_threshold', 'track_stock', 'is_out_of_stock']
    inlines = [InventoryTransactionInline]
