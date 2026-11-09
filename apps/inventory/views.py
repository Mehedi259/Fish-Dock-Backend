from rest_framework import generics, status
from rest_framework.views import APIView
from decimal import Decimal
from .models import Inventory, InventoryTransaction, TransactionType
from .serializers import InventorySerializer, InventoryTransactionSerializer
from accounts.permissions import IsAdminOrStaff
from core.utils import api_response

class InventoryListView(generics.ListAPIView):
    permission_classes = [IsAdminOrStaff]
    serializer_class = InventorySerializer

    def get_queryset(self):
        queryset = Inventory.objects.select_related('product', 'product__category').prefetch_related('transactions').all()
        low_stock = self.request.query_params.get('low_stock')
        if low_stock in ['true', '1']:
            queryset = [item for item in queryset if item.available_quantity <= item.low_stock_threshold]
            return queryset
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return api_response(success=True, data=serializer.data)


class InventoryAdjustView(APIView):
    permission_classes = [IsAdminOrStaff]

    def post(self, request, pk):
        try:
            inventory = Inventory.objects.get(pk=pk)
        except Inventory.DoesNotExist:
            return api_response(success=False, message="Inventory record not found", status=404)

        quantity = request.data.get('quantity')
        transaction_type = request.data.get('transaction_type', TransactionType.MANUAL_ADJUSTMENT)
        reason = request.data.get('reason', 'Stock level updated by admin')
        notes = request.data.get('notes', '')

        if quantity is None:
            return api_response(success=False, message="quantity is required", status=400)

        try:
            qty_delta = Decimal(str(quantity))
        except Exception:
            return api_response(success=False, message="Invalid quantity format", status=400)

        # Update available quantity
        if transaction_type in [TransactionType.RESTOCK]:
            inventory.available_quantity += qty_delta
        elif transaction_type in [TransactionType.ORDER_DEDUCTION, TransactionType.SPOILAGE_WASTE]:
            inventory.available_quantity = max(Decimal('0.00'), inventory.available_quantity - abs(qty_delta))
        else: # Manual adjustment replaces or sets
            mode = request.data.get('mode', 'add') # 'add' or 'set'
            if mode == 'set':
                inventory.available_quantity = max(Decimal('0.00'), qty_delta)
            else:
                inventory.available_quantity = max(Decimal('0.00'), inventory.available_quantity + qty_delta)

        inventory.save()

        # Record transaction
        tx = InventoryTransaction.objects.create(
            inventory=inventory,
            transaction_type=transaction_type,
            quantity=qty_delta,
            balance_after=inventory.available_quantity,
            reason=reason,
            created_by=request.user if request.user.is_authenticated else None,
            notes=notes
        )

        return api_response(
            success=True,
            message=f"Stock adjusted for {inventory.product.name}. New balance: {inventory.available_quantity} {inventory.product.unit}",
            data={
                "inventory_id": str(inventory.id),
                "available_quantity": float(inventory.available_quantity),
                "is_out_of_stock": inventory.is_out_of_stock,
                "transaction_id": str(tx.id)
            }
        )
