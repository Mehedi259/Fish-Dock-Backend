from django.contrib import admin
from .models import PriceHistory

@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ['product', 'previous_price', 'new_price', 'effective_date', 'reason', 'changed_by']
    list_filter = ['effective_date', 'changed_by']
    search_fields = ['product__name', 'reason']
