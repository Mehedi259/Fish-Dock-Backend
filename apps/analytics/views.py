from rest_framework.views import APIView
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Count, Q
from decimal import Decimal
from accounts.permissions import IsAdminOrStaff
from products.models import Product
from orders.models import Order, OrderItem, OrderStatus, WhatsAppStatus
from core.utils import api_response

class DashboardOverviewView(APIView):
    permission_classes = [IsAdminOrStaff]

    def get(self, request):
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        seven_days_ago = today_start - timedelta(days=6)

        # Products KPIs
        total_products = Product.objects.count()
        active_products = Product.objects.filter(is_active=True).count()
        out_of_stock_products = Product.objects.filter(inventory__is_out_of_stock=True).count()

        # Orders KPIs
        all_orders = Order.objects.all()
        total_orders = all_orders.count()
        today_orders = all_orders.filter(created_at__gte=today_start).count()
        
        pending_confirmation = all_orders.filter(status=OrderStatus.PENDING_CONFIRMATION).count()
        awaiting_customer = all_orders.filter(status=OrderStatus.AWAITING_CUSTOMER_RESPONSE).count()
        price_confirmed = all_orders.filter(status=OrderStatus.PRICE_CONFIRMED).count()
        confirmed_orders = all_orders.filter(status__in=[OrderStatus.CONFIRMED, OrderStatus.PROCESSING, OrderStatus.READY_FOR_DELIVERY, OrderStatus.OUT_FOR_DELIVERY]).count()
        delivered_orders = all_orders.filter(status=OrderStatus.DELIVERED).count()
        cancelled_orders = all_orders.filter(status=OrderStatus.CANCELLED).count()

        # Revenue
        revenue_delivered = all_orders.filter(status=OrderStatus.DELIVERED).aggregate(
            rev=Sum('final_confirmed_amount')
        )['rev'] or Decimal('0.00')

        revenue_confirmed = all_orders.filter(
            status__in=[OrderStatus.PRICE_CONFIRMED, OrderStatus.CONFIRMED, OrderStatus.PROCESSING, OrderStatus.READY_FOR_DELIVERY, OrderStatus.OUT_FOR_DELIVERY, OrderStatus.DELIVERED]
        ).aggregate(rev=Sum('final_confirmed_amount'))['rev'] or Decimal('0.00')

        total_indicative_demand = all_orders.aggregate(
            ind=Sum('indicative_subtotal')
        )['ind'] or Decimal('0.00')

        # Recent Orders (last 8)
        recent_orders_qs = all_orders.prefetch_related('items')[:8]
        recent_orders = [
            {
                "id": str(o.id),
                "order_reference": o.order_reference,
                "customer_name": o.customer_name,
                "customer_phone": o.customer_phone,
                "delivery_area": o.delivery_area,
                "status": o.status,
                "whatsapp_status": o.whatsapp_status,
                "indicative_subtotal": float(o.indicative_subtotal),
                "final_confirmed_amount": float(o.final_confirmed_amount) if o.final_confirmed_amount else None,
                "items_count": o.items.count(),
                "created_at": o.created_at.isoformat()
            }
            for o in recent_orders_qs
        ]

        # Top selling items
        top_items = OrderItem.objects.values(
            'product_name_snapshot'
        ).annotate(
            total_qty=Sum('quantity'),
            order_count=Count('order')
        ).order_by('-total_qty')[:5]

        # Last 7 days sales trend
        daily_trend = []
        for i in range(7):
            day = seven_days_ago + timedelta(days=i)
            next_day = day + timedelta(days=1)
            day_orders = all_orders.filter(created_at__gte=day, created_at__lt=next_day)
            day_rev = day_orders.filter(
                status__in=[OrderStatus.CONFIRMED, OrderStatus.PRICE_CONFIRMED, OrderStatus.DELIVERED]
            ).aggregate(r=Sum('final_confirmed_amount'))['r'] or Decimal('0.00')
            daily_trend.append({
                "date": day.strftime("%b %d"),
                "orders_count": day_orders.count(),
                "revenue": float(day_rev)
            })

        return api_response(
            success=True,
            data={
                "products": {
                    "total": total_products,
                    "active": active_products,
                    "out_of_stock": out_of_stock_products
                },
                "orders": {
                    "total": total_orders,
                    "today": today_orders,
                    "pending_confirmation": pending_confirmation,
                    "awaiting_customer": awaiting_customer,
                    "price_confirmed": price_confirmed,
                    "confirmed": confirmed_orders,
                    "delivered": delivered_orders,
                    "cancelled": cancelled_orders
                },
                "revenue": {
                    "confirmed_total": float(revenue_confirmed),
                    "delivered_total": float(revenue_delivered),
                    "indicative_demand_total": float(total_indicative_demand)
                },
                "recent_orders": recent_orders,
                "top_selling_products": list(top_items),
                "daily_trend": daily_trend
            }
        )
