from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from django.utils import timezone
from .models import PriceHistory
from .serializers import PriceHistorySerializer
from products.models import Product
from accounts.permissions import IsAdminOrStaff
from core.utils import api_response

class PriceHistoryListView(generics.ListAPIView):
    permission_classes = [IsAdminOrStaff]
    serializer_class = PriceHistorySerializer

    def get_queryset(self):
        queryset = PriceHistory.objects.select_related('product', 'changed_by').all()
        product_id = self.request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset.order_by('-effective_date')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return api_response(success=True, data=serializer.data)


class UpdateProductPriceView(APIView):
    permission_classes = [IsAdminOrStaff]

    def post(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return api_response(success=False, message="Product not found", status=404)

        new_price = request.data.get('new_price')
        if new_price is None:
            return api_response(success=False, message="new_price is required", status=400)

        try:
            new_price_dec = float(new_price)
        except ValueError:
            return api_response(success=False, message="Invalid price format", status=400)

        old_price = product.base_price
        reason = request.data.get('reason', 'Daily market catch price update')
        notes = request.data.get('notes', '')
        price_display_type = request.data.get('price_display_type')
        price_notice_label = request.data.get('price_notice_label')

        # Update Product
        product.base_price = new_price_dec
        product.market_price_updated_at = timezone.now()
        if price_display_type:
            product.price_display_type = price_display_type
        if price_notice_label:
            product.price_notice_label = price_notice_label
        product.save()

        # Log history
        history = PriceHistory.objects.create(
            product=product,
            previous_price=old_price,
            new_price=new_price_dec,
            effective_date=timezone.now(),
            reason=reason,
            changed_by=request.user if request.user.is_authenticated else None,
            notes=notes
        )

        return api_response(
            success=True,
            message=f"Price for {product.name} updated from ৳{old_price} to ৳{new_price_dec}",
            data={
                "product_id": str(product.id),
                "previous_price": float(old_price),
                "new_price": float(new_price_dec),
                "price_display_type": product.price_display_type,
                "history_id": str(history.id)
            }
        )
