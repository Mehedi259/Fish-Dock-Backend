import urllib.parse
from rest_framework.response import Response

def api_response(success=True, message="", data=None, errors=None, status=200):
    return Response({
        "success": success,
        "message": message,
        "data": data,
        "errors": errors
    }, status=status)

def build_whatsapp_order_message(order, store_name="Fish Dock", whatsapp_number="+8801700000000"):
    """
    Constructs a professional, clearly structured, readable pre-filled WhatsApp message
    for order confirmation with deep link URL.
    """
    lines = [
        f"🐟 *{store_name} – Order Confirmation Request*",
        "--------------------------------------",
        f"📋 *Order ID:* {order.order_reference}",
        f"👤 *Customer:* {order.customer_name}",
        f"📞 *Phone:* {order.customer_phone}",
        f"📍 *Delivery Address:* {order.delivery_address}",
    ]

    if hasattr(order, 'delivery_area') and order.delivery_area:
        lines.append(f"🏙️ *Area:* {order.delivery_area}")

    if hasattr(order, 'preferred_delivery_slot') and order.preferred_delivery_slot:
        lines.append(f"⏰ *Preferred Slot:* {order.preferred_delivery_slot}")

    lines.append("\n📦 *Requested Items:*")
    items = order.items.all()
    for idx, item in enumerate(items, 1):
        unit = item.unit_snapshot or "kg"
        qty_str = f"{item.quantity:g} {unit}"
        price_str = f"৳{item.indicative_total:,.2f}" if item.indicative_total else "Price on Call"
        cutting = f" ({item.cutting_instruction})" if item.cutting_instruction else ""
        lines.append(f"{idx}. {item.product_name_snapshot} – {qty_str}{cutting} [≈ {price_str}]")

    lines.append("\n--------------------------------------")
    if order.indicative_subtotal:
        lines.append(f"🏷️ *Indicative Subtotal:* ৳{order.indicative_subtotal:,.2f}")
    if hasattr(order, 'delivery_fee') and order.delivery_fee:
        lines.append(f"🚚 *Estimated Delivery Fee:* ৳{order.delivery_fee:,.2f}")

    if order.customer_notes:
        lines.append(f"\n📝 *Customer Notes:* {order.customer_notes}")

    lines.append("\n⚠️ *Note:* Daily market fish prices fluctuate. Please confirm the latest morning market rate, exact weight, and final total before delivery dispatch.")
    lines.append("\nThank you for choosing Fish Dock! 🐟🌊")

    message_text = "\n".join(lines)
    clean_number = "".join(filter(lambda c: c.isdigit() or c == '+', whatsapp_number)).replace('+', '')
    encoded_text = urllib.parse.quote(message_text)
    
    # WhatsApp deep link URL: https://wa.me/<number>?text=<encoded_text>
    deep_link = f"https://wa.me/{clean_number}?text={encoded_text}"
    
    return {
        "message_text": message_text,
        "whatsapp_number": clean_number,
        "deep_link": deep_link
    }

