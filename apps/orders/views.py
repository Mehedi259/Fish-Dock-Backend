import csv
from decimal import Decimal
from django.db import transaction
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Q
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from .models import Order, OrderItem, OrderStatusHistory, OrderStatus, WhatsAppStatus
from .serializers import (
    OrderDetailSerializer,
    CreateOrderRequestSerializer
)
from products.models import Product
from accounts.permissions import IsAdminOrStaff
from system_settings.models import SystemSetting
from core.utils import api_response, build_whatsapp_order_message

class CreateOrderView(APIView):
    """
    Public / Guest order submission endpoint.
    Saves the complete order before generating WhatsApp link.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = CreateOrderRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return api_response(
                success=False,
                message="Order validation failed",
                errors=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        data = serializer.validated_data
        items_data = data.pop('items')

        with transaction.atomic():
            # Generate unique order reference
            order_ref = Order.generate_order_reference()

            # Retrieve default delivery fee
            default_delivery_fee_str = SystemSetting.get_val('DEFAULT_DELIVERY_FEE', '60')
            try:
                delivery_fee = Decimal(default_delivery_fee_str)
            except Exception:
                delivery_fee = Decimal('60.00')

            order = Order.objects.create(
                order_reference=order_ref,
                customer_name=data['customer_name'],
                customer_phone=data['customer_phone'],
                customer_email=data.get('customer_email', ''),
                delivery_address=data['delivery_address'],
                delivery_area=data.get('delivery_area', 'Mirpur, Dhaka'),
                delivery_city=data.get('delivery_city', 'Dhaka'),
                preferred_delivery_slot=data.get('preferred_delivery_slot', 'Morning (8 AM - 12 PM)'),
                customer_notes=data.get('customer_notes', ''),
                delivery_fee=delivery_fee,
                status=OrderStatus.PENDING_CONFIRMATION,
                whatsapp_status=WhatsAppStatus.NOT_CONTACTED
            )

            indicative_subtotal = Decimal('0.00')

            for item_input in items_data:
                product_id = item_input['product_id']
                qty = item_input['quantity']
                cutting = item_input.get('cutting_instruction', 'Whole Fish (Gutted & Cleaned)')

                try:
                    product = Product.objects.select_for_update().get(id=product_id)
                except Product.DoesNotExist:
                    transaction.set_rollback(True)
                    return api_response(
                        success=False,
                        message=f"Product with ID {product_id} was not found or is discontinued.",
                        status=status.HTTP_400_BAD_REQUEST
                    )

                unit_price = product.base_price
                item_indicative_total = (unit_price * qty).quantize(Decimal('0.01'))
                indicative_subtotal += item_indicative_total

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name_snapshot=product.name,
                    unit_snapshot=product.unit,
                    standard_weight_range_snapshot=product.standard_weight_range or "",
                    quantity=qty,
                    unit_price_snapshot=unit_price,
                    indicative_total=item_indicative_total,
                    cutting_instruction=cutting
                )

            # Check for free delivery threshold
            free_threshold_str = SystemSetting.get_val('FREE_DELIVERY_THRESHOLD', '2000')
            try:
                if indicative_subtotal >= Decimal(free_threshold_str):
                    order.delivery_fee = Decimal('0.00')
            except Exception:
                pass

            order.indicative_subtotal = indicative_subtotal
            order.save()

            # Record initial history
            OrderStatusHistory.objects.create(
                order=order,
                previous_status=None,
                new_status=OrderStatus.PENDING_CONFIRMATION,
                notes="Order request placed by customer via web platform."
            )

        # Build WhatsApp link
        store_name = SystemSetting.get_val('STORE_NAME', 'Fish Dock')
        wa_number = SystemSetting.get_val('WHATSAPP_BUSINESS_NUMBER', '+8801700000000')
        wa_data = build_whatsapp_order_message(order, store_name=store_name, whatsapp_number=wa_number)

        serialized = OrderDetailSerializer(order).data

        return api_response(
            success=True,
            message="Order request successfully created and recorded. Please proceed to WhatsApp to confirm latest market price.",
            data={
                "order": serialized,
                "whatsapp": wa_data
            },
            status=status.HTTP_201_CREATED
        )


class TrackOrderView(APIView):
    """
    Public tracking view for customers.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        ref = request.query_params.get('reference', '').strip()
        phone = request.query_params.get('phone', '').strip()

        if not ref and not phone:
            return api_response(success=False, message="Please provide either reference or phone number", status=400)

        queryset = Order.objects.prefetch_related('items', 'status_history')
        if ref:
            order = queryset.filter(order_reference__iexact=ref).first()
        else:
            order = queryset.filter(customer_phone__icontains=phone).first()

        if not order:
            return api_response(success=False, message="No order found matching your inquiry", status=404)

        store_name = SystemSetting.get_val('STORE_NAME', 'Fish Dock')
        wa_number = SystemSetting.get_val('WHATSAPP_BUSINESS_NUMBER', '+8801700000000')
        wa_data = build_whatsapp_order_message(order, store_name=store_name, whatsapp_number=wa_number)

        return api_response(
            success=True,
            data={
                "order": OrderDetailSerializer(order).data,
                "whatsapp": wa_data
            }
        )


class OrderListAdminView(generics.ListAPIView):
    permission_classes = [IsAdminOrStaff]
    serializer_class = OrderDetailSerializer

    def get_queryset(self):
        queryset = Order.objects.prefetch_related('items', 'status_history').all()

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(order_reference__icontains=search) |
                Q(customer_name__icontains=search) |
                Q(customer_phone__icontains=search) |
                Q(delivery_address__icontains=search)
            )

        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)

        wa_status = self.request.query_params.get('whatsapp_status')
        if wa_status:
            queryset = queryset.filter(whatsapp_status=wa_status)

        return queryset.order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return api_response(success=True, data=serializer.data)


class OrderDetailAdminView(generics.RetrieveAPIView):
    permission_classes = [IsAdminOrStaff]
    queryset = Order.objects.prefetch_related('items', 'status_history').all()
    serializer_class = OrderDetailSerializer
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return api_response(success=True, data=serializer.data)


class UpdateOrderStatusView(APIView):
    permission_classes = [IsAdminOrStaff]

    def post(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return api_response(success=False, message="Order not found", status=404)

        new_status = request.data.get('status')
        if not new_status or new_status not in [c[0] for c in OrderStatus.choices]:
            return api_response(success=False, message=f"Invalid status: {new_status}", status=400)

        prev_status = order.status
        order.status = new_status

        whatsapp_status = request.data.get('whatsapp_status')
        if whatsapp_status and whatsapp_status in [c[0] for c in WhatsAppStatus.choices]:
            order.whatsapp_status = whatsapp_status

        admin_notes = request.data.get('admin_notes')
        if admin_notes:
            order.admin_notes = admin_notes

        order.save()

        # Record history
        OrderStatusHistory.objects.create(
            order=order,
            previous_status=prev_status,
            new_status=new_status,
            changed_by=request.user,
            notes=request.data.get('notes', f"Status updated from {prev_status} to {new_status}")
        )

        return api_response(
            success=True,
            message=f"Order status changed to {new_status}",
            data=OrderDetailSerializer(order).data
        )


class ConfirmOrderPriceView(APIView):
    """
    Admin confirms finalized market prices and exact weights agreed with customer on WhatsApp.
    """
    permission_classes = [IsAdminOrStaff]

    def post(self, request, pk):
        try:
            order = Order.objects.prefetch_related('items').get(pk=pk)
        except Order.DoesNotExist:
            return api_response(success=False, message="Order not found", status=404)

        items_updates = request.data.get('items', [])
        # Each item update can include: id, final_unit_price, quantity_adjusted, adjustment_reason

        total_final = Decimal('0.00')

        with transaction.atomic():
            for item_up in items_updates:
                item_id = item_up.get('id')
                item = order.items.filter(id=item_id).first()
                if not item:
                    continue

                if 'final_unit_price' in item_up:
                    item.final_unit_price = Decimal(str(item_up['final_unit_price']))
                if 'quantity_adjusted' in item_up:
                    item.quantity_adjusted = Decimal(str(item_up['quantity_adjusted']))
                if 'adjustment_reason' in item_up:
                    item.adjustment_reason = item_up['adjustment_reason']

                qty = item.quantity_adjusted if item.quantity_adjusted is not None else item.quantity
                unit_price = item.final_unit_price if item.final_unit_price is not None else item.unit_price_snapshot
                item.final_total = (qty * unit_price).quantize(Decimal('0.01'))
                item.save()
                total_final += item.final_total

            custom_final_amount = request.data.get('final_confirmed_amount')
            if custom_final_amount is not None:
                order.final_confirmed_amount = Decimal(str(custom_final_amount))
            else:
                order.final_confirmed_amount = total_final + order.delivery_fee

            order.whatsapp_status = request.data.get('whatsapp_status', WhatsAppStatus.CONFIRMED_VIA_WHATSAPP)
            order.status = request.data.get('status', OrderStatus.PRICE_CONFIRMED)
            order.confirmed_by = request.user
            order.confirmed_at = timezone.now()

            admin_notes = request.data.get('admin_notes')
            if admin_notes:
                order.admin_notes = admin_notes

            order.save()

            OrderStatusHistory.objects.create(
                order=order,
                previous_status=order.status,
                new_status=OrderStatus.PRICE_CONFIRMED,
                changed_by=request.user,
                notes=f"Final order price confirmed at ৳{order.final_confirmed_amount} by {request.user.username} via WhatsApp"
            )

        return api_response(
            success=True,
            message="Final price confirmed and order updated successfully",
            data=OrderDetailSerializer(order).data
        )


class ExportOrdersCSVView(APIView):
    permission_classes = [IsAdminOrStaff]

    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="fishdock_orders_{timezone.now().strftime("%Y%m%d_%H%M")}.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Order Reference', 'Date', 'Customer Name', 'Phone', 'Address',
            'Area', 'Status', 'WhatsApp Status', 'Indicative Subtotal',
            'Delivery Fee', 'Final Confirmed Amount', 'Items Count'
        ])

        orders = Order.objects.prefetch_related('items').all().order_by('-created_at')
        for o in orders:
            writer.writerow([
                o.order_reference,
                o.created_at.strftime('%Y-%m-%d %H:%M'),
                o.customer_name,
                o.customer_phone,
                o.delivery_address,
                o.delivery_area,
                o.status,
                o.whatsapp_status,
                o.indicative_subtotal,
                o.delivery_fee,
                o.final_confirmed_amount or '',
                o.items.count()
            ])

        return response
