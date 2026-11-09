"""
Seed script for Fish Dock database
Run via: .venv/bin/python seed_data.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fishdock_api.settings')
django.setup()

from decimal import Decimal
from django.utils import timezone
from accounts.models import User, UserRole
from categories.models import Category
from products.models import Product, ProductImage, UnitType, PriceDisplayType
from pricing.models import PriceHistory
from inventory.models import Inventory, InventoryTransaction, TransactionType
from orders.models import Order, OrderItem, OrderStatusHistory, OrderStatus, WhatsAppStatus
from content.models import Banner, Testimonial, FAQ
from system_settings.models import SystemSetting

def seed():
    print("🌱 Starting Fish Dock database seeding...")

    # 1. Admin Users
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@fishdock.com',
            'first_name': 'Principal',
            'last_name': 'Admin',
            'role': UserRole.SUPER_ADMIN,
            'is_staff': True,
            'is_superuser': True,
            'phone': '+8801700000001'
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print("✅ Super Admin created: admin / admin123")
    else:
        print("ℹ️ Super Admin already exists.")

    order_mgr, created = User.objects.get_or_create(
        username='ordermanager',
        defaults={
            'email': 'orders@fishdock.com',
            'first_name': 'Rafiqul',
            'last_name': 'Islam',
            'role': UserRole.ORDER_MANAGER,
            'is_staff': True,
            'phone': '+8801700000002'
        }
    )
    if created:
        order_mgr.set_password('order123')
        order_mgr.save()
        print("✅ Order Manager created: ordermanager / order123")

    # 2. System Settings
    settings_data = [
        ('WHATSAPP_BUSINESS_NUMBER', '+8801712345678', 'Official WhatsApp Business number for order confirmations', True),
        ('STORE_NAME', 'Fish Dock', 'Store branding name', True),
        ('STORE_TAGLINE', 'Fresh River & Sea Fish Direct from Trusted Fishermen to Your Home', 'Tagline', True),
        ('STORE_PHONE', '+8801712345678', 'Customer service hotline', True),
        ('STORE_EMAIL', 'care@fishdock.com', 'Support email', True),
        ('OFFICE_ADDRESS', 'Ghat #4, Sadarghat & Mirpur-1 Seafood Hub, Dhaka', 'Physical office address', True),
        ('CURRENCY_SYMBOL', '৳', 'Display currency symbol', True),
        ('CURRENCY_CODE', 'BDT', 'ISO currency code', True),
        ('DEFAULT_DELIVERY_FEE', '60.00', 'Standard city delivery fee in BDT', True),
        ('FREE_DELIVERY_THRESHOLD', '2000.00', 'Free delivery on orders above this indicative amount', True),
        ('PRICE_DISCLAIMER_TEXT', 'Fish prices fluctuate daily depending on morning river landings, market supply, and catch weight. Final exact price and weight will be confirmed directly with you on WhatsApp before dispatch.', 'Mandatory price disclaimer', True),
        ('STORE_STATUS', 'open', 'Current operation status: open / closed', True)
    ]
    for key, val, desc, is_pub in settings_data:
        SystemSetting.objects.update_or_create(
            key=key,
            defaults={'value': val, 'description': desc, 'is_public': is_pub}
        )
    print("✅ System Settings initialized.")

    # 3. Categories matching mobile screenshot
    categories_data = [
        {
            'name': 'River Fish',
            'bangla_name': 'নদীর তাজা মাছ',
            'slug': 'river-fish',
            'description': 'Sweet freshwater fish sourced daily from Padma, Meghna, and Jamuna rivers.',
            'icon_name': 'waves',
            'image_url': 'https://images.unsplash.com/photo-1544551763-46a013bb70d5?auto=format&fit=crop&w=600&q=80',
            'display_order': 1
        },
        {
            'name': 'Sea Fish',
            'bangla_name': 'সামুদ্রিক মাছ',
            'slug': 'sea-fish',
            'description': 'Deep sea catch from the Bay of Bengal, iced right on the trawler for optimum freshness.',
            'icon_name': 'fish',
            'image_url': 'https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?auto=format&fit=crop&w=600&q=80',
            'display_order': 2
        },
        {
            'name': 'Prawn & Shrimp',
            'bangla_name': 'চিংড়ি মাছ',
            'slug': 'prawn',
            'description': 'Fresh Golda and Bagda prawns selected by size and quality.',
            'icon_name': 'shrimp',
            'image_url': 'https://images.unsplash.com/photo-1565680018434-b513d5e5fd47?auto=format&fit=crop&w=600&q=80',
            'display_order': 3
        },
        {
            'name': 'Crab',
            'bangla_name': 'জীবন্ত কাঁকড়া',
            'slug': 'crab',
            'description': 'Live mud crabs from Sundarbans coastal deltas.',
            'icon_name': 'crab',
            'image_url': 'https://images.unsplash.com/photo-1559847844-5315695dadae?auto=format&fit=crop&w=600&q=80',
            'display_order': 4
        },
        {
            'name': 'Live & Native Fish',
            'bangla_name': 'দেশি ও জ্যান্ত মাছ',
            'slug': 'live-fish',
            'description': 'Live indigenous fish delivered alive in oxygenated water containers.',
            'icon_name': 'sparkles',
            'image_url': 'https://images.unsplash.com/photo-1524704654690-b56c05c78a00?auto=format&fit=crop&w=600&q=80',
            'display_order': 5
        },
        {
            'name': 'Premium Fish',
            'bangla_name': 'স্পেশাল প্রিমিয়াম মাছ',
            'slug': 'premium-fish',
            'description': 'Hand-picked trophy-size catches for festivals, special family dinners, and gourmets.',
            'icon_name': 'crown',
            'image_url': 'https://images.unsplash.com/photo-1534943441045-1089b82b9560?auto=format&fit=crop&w=600&q=80',
            'display_order': 6
        }
    ]

    cat_map = {}
    for cat in categories_data:
        obj, _ = Category.objects.update_or_create(
            slug=cat['slug'],
            defaults=cat
        )
        cat_map[cat['slug']] = obj
    print(f"✅ Created {len(cat_map)} categories.")

    # 4. Products with authentic photography and exact details
    products_data = [
        {
            'name': 'Hilsa (Padma Ilish)',
            'bangla_name': 'চাঁদপুরের পদ্মার রুপালী ইলিশ',
            'slug': 'hilsa-ilish-padma',
            'category': cat_map['river-fish'],
            'short_description': 'Authentic silver Hilsa from Padma River, Chandpur. Incomparable aroma and rich natural omega-3 oils.',
            'full_description': 'The pride of Bengal waters. Sourced at dawn from Chandpur ghat fishermen. Carefully chilled in crushed sea-ice without chemical preservatives. Ideal for Shorshe Ilish, Ilish Bhaja, and Paturi.',
            'origin': 'Padma River, Chandpur',
            'freshness_grade': 'Grade A+ – Dawn Landing',
            'unit': UnitType.KG,
            'standard_weight_range': '≈ 800g – 1kg (per piece)',
            'base_price': Decimal('1350.00'),
            'price_display_type': PriceDisplayType.INDICATIVE,
            'price_notice_label': 'Latest Listed Market Price',
            'min_order_qty': Decimal('1.0'),
            'step_qty': Decimal('1.0'),
            'is_featured': True,
            'is_popular': True,
            'is_fresh_arrival': True,
            'images': [
                'https://images.unsplash.com/photo-1544551763-46a013bb70d5?auto=format&fit=crop&w=800&q=80',
                'https://images.unsplash.com/photo-1534943441045-1089b82b9560?auto=format&fit=crop&w=800&q=80'
            ]
        },
        {
            'name': 'Rohu (Rui)',
            'bangla_name': 'নদীর তাজা রুই মাছ',
            'slug': 'rohu-rui-river',
            'category': cat_map['river-fish'],
            'short_description': 'Fresh river Rui with firm pink gills and glittering scales. Perfect everyday Bengali fish curry.',
            'full_description': 'Caught fresh from river channels. Sweet tasting flesh, thoroughly cleaned and prepared whole or curry cut upon your preference.',
            'origin': 'Meghna River, Munshiganj',
            'freshness_grade': 'Grade A – Morning River Catch',
            'unit': UnitType.KG,
            'standard_weight_range': '≈ 1 – 1.5 kg (per piece)',
            'base_price': Decimal('350.00'),
            'price_display_type': PriceDisplayType.INDICATIVE,
            'price_notice_label': 'Latest Listed Market Price',
            'min_order_qty': Decimal('1.0'),
            'step_qty': Decimal('0.5'),
            'is_featured': True,
            'is_popular': True,
            'is_fresh_arrival': False,
            'images': [
                'https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?auto=format&fit=crop&w=800&q=80',
                'https://images.unsplash.com/photo-1544551763-46a013bb70d5?auto=format&fit=crop&w=800&q=80'
            ]
        },
        {
            'name': 'Katla Fish (River Katol)',
            'bangla_name': 'বড় নদীর কাতলা মাছ',
            'slug': 'katla-fish-river',
            'category': cat_map['river-fish'],
            'short_description': 'Large sweet river Katla with rich head pieces and fatty belly (Peti).',
            'full_description': 'Sourced from the deep currents of the Jamuna. Famous for rich Katla Kalia and head mudi ghonto.',
            'origin': 'Jamuna River, Sirajganj',
            'freshness_grade': 'Grade A – Fresh River Catch',
            'unit': UnitType.KG,
            'standard_weight_range': '≈ 2 – 3 kg (per piece)',
            'base_price': Decimal('420.00'),
            'price_display_type': PriceDisplayType.INDICATIVE,
            'price_notice_label': 'Indicative Rate',
            'min_order_qty': Decimal('1.5'),
            'step_qty': Decimal('0.5'),
            'is_featured': False,
            'is_popular': True,
            'is_fresh_arrival': True,
            'images': [
                'https://images.unsplash.com/photo-1534943441045-1089b82b9560?auto=format&fit=crop&w=800&q=80'
            ]
        },
        {
            'name': 'Pabda Fish (Deshi Pabda)',
            'bangla_name': 'দেশি নদীর পাবদা মাছ',
            'slug': 'pabda-fish-deshi',
            'category': cat_map['river-fish'],
            'short_description': 'Silky soft freshwater Pabda. Tender texture and delicate taste.',
            'full_description': 'Small river catfish with no scales and single central bone. Ideal for delicate mustard or tomato-chili Shorshe Pabda.',
            'origin': 'Chalan Beel & Padma Tributaries',
            'freshness_grade': 'Grade A – Morning Landing',
            'unit': UnitType.KG,
            'standard_weight_range': '≈ 250g – 400g (bundle of 4-6 pcs)',
            'base_price': Decimal('650.00'),
            'price_display_type': PriceDisplayType.INDICATIVE,
            'price_notice_label': 'Indicative Price',
            'min_order_qty': Decimal('0.5'),
            'step_qty': Decimal('0.5'),
            'is_featured': True,
            'is_popular': True,
            'is_fresh_arrival': True,
            'images': [
                'https://images.unsplash.com/photo-1524704654690-b56c05c78a00?auto=format&fit=crop&w=800&q=80'
            ]
        },
        {
            'name': 'Tiger Prawn (Bagda Chingri)',
            'bangla_name': 'সুন্দরবনের বাগদা চিংড়ি',
            'slug': 'tiger-prawn-bagda',
            'category': cat_map['prawn'],
            'short_description': 'Jumbo tiger prawns from the brackish waters of Satkhira and Sundarbans.',
            'full_description': 'Crisp, sweet, firm prawns with signature tiger stripes. Superb for Malaikari, grilled butter prawn, and stir fries.',
            'origin': 'Sundarbans Coast, Satkhira',
            'freshness_grade': 'Chilled Sea Catch',
            'unit': UnitType.KG,
            'standard_weight_range': '≈ 20 – 25 pieces per kg',
            'base_price': Decimal('950.00'),
            'price_display_type': PriceDisplayType.INDICATIVE,
            'price_notice_label': 'Daily Landing Rate',
            'min_order_qty': Decimal('0.5'),
            'step_qty': Decimal('0.5'),
            'is_featured': True,
            'is_popular': True,
            'is_fresh_arrival': False,
            'images': [
                'https://images.unsplash.com/photo-1565680018434-b513d5e5fd47?auto=format&fit=crop&w=800&q=80'
            ]
        },
        {
            'name': 'Giant River Prawn (Golda Chingri)',
            'bangla_name': 'বড় গলদা চিংড়ি',
            'slug': 'giant-river-prawn-golda',
            'category': cat_map['prawn'],
            'short_description': 'Huge freshwater Golda prawns with large heads packed with rich flavorful head roe (Mogoj).',
            'full_description': 'Premium large freshwater river prawns. Prized for their sweet lobster-like tail meat and famous head delicacies.',
            'origin': 'Meghna Estuary, Barisal',
            'freshness_grade': 'Live Morning Landing',
            'unit': UnitType.KG,
            'standard_weight_range': '≈ 8 – 10 pieces per kg',
            'base_price': Decimal('1250.00'),
            'price_display_type': PriceDisplayType.INDICATIVE,
            'price_notice_label': 'Price Subject to Daily Size',
            'min_order_qty': Decimal('1.0'),
            'step_qty': Decimal('0.5'),
            'is_featured': True,
            'is_popular': True,
            'is_fresh_arrival': True,
            'images': [
                'https://images.unsplash.com/photo-1565680018434-b513d5e5fd47?auto=format&fit=crop&w=800&q=80'
            ]
        },
        {
            'name': 'Live Mud Crab (Sundarbans Kankra)',
            'bangla_name': 'সুন্দরবনের জীবন্ত কাদা কাঁকড়া',
            'slug': 'live-mud-crab-sundarbans',
            'category': cat_map['crab'],
            'short_description': 'Tightly tied live mangrove mud crabs with solid meaty claws.',
            'full_description': 'Wild harvested from Sundarbans estuaries. High meat fill guarantee. Superb for spicy Bengali crab curry or garlic butter roast.',
            'origin': 'Sundarbans Delta',
            'freshness_grade': '100% Live Guaranteed',
            'unit': UnitType.KG,
            'standard_weight_range': '≈ 300g – 500g (per piece)',
            'base_price': Decimal('850.00'),
            'price_display_type': PriceDisplayType.INDICATIVE,
            'price_notice_label': 'Live Catch Rate',
            'min_order_qty': Decimal('1.0'),
            'step_qty': Decimal('0.5'),
            'is_featured': False,
            'is_popular': True,
            'is_fresh_arrival': False,
            'images': [
                'https://images.unsplash.com/photo-1559847844-5315695dadae?auto=format&fit=crop&w=800&q=80'
            ]
        },
        {
            'name': 'Coral Fish / Bhetki',
            'bangla_name': 'কোরাল / সামুদ্রিক ভেটকি',
            'slug': 'coral-bhetki-bay-of-bengal',
            'category': cat_map['sea-fish'],
            'short_description': 'Firm white flaked Asian Seabass (Bhetki). King of fish fry and steaks.',
            'full_description': 'Caught in the coastal waters of Cox’s Bazar and Saint Martin. Boneless fillets available upon request.',
            'origin': 'Bay of Bengal, Cox’s Bazar',
            'freshness_grade': 'Grade A+ – Sea Iced',
            'unit': UnitType.KG,
            'standard_weight_range': '≈ 1.5 – 2.5 kg (per piece)',
            'base_price': Decimal('980.00'),
            'price_display_type': PriceDisplayType.INDICATIVE,
            'price_notice_label': 'Subject to Morning Catch',
            'min_order_qty': Decimal('1.0'),
            'step_qty': Decimal('0.5'),
            'is_featured': True,
            'is_popular': False,
            'is_fresh_arrival': True,
            'images': [
                'https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?auto=format&fit=crop&w=800&q=80'
            ]
        },
        {
            'name': 'White Pomfret (Rupchanda)',
            'bangla_name': 'সাদা রূপচাঁদা মাছ',
            'slug': 'white-pomfret-rupchanda',
            'category': cat_map['sea-fish'],
            'short_description': 'Premium silver sea Pomfret. Buttery, succulent, sweet flavor with minimal bones.',
            'full_description': 'Pristine marine catch. Perfect for whole crispy tawa fry, tandoori marination, or steamed with ginger-scallion.',
            'origin': 'Deep Sea, Bay of Bengal',
            'freshness_grade': 'Grade A – Deep Sea Catch',
            'unit': UnitType.KG,
            'standard_weight_range': '≈ 300g – 500g (per piece)',
            'base_price': Decimal('1100.00'),
            'price_display_type': PriceDisplayType.INDICATIVE,
            'price_notice_label': 'Latest Listed Price',
            'min_order_qty': Decimal('1.0'),
            'step_qty': Decimal('0.5'),
            'is_featured': True,
            'is_popular': True,
            'is_fresh_arrival': False,
            'images': [
                'https://images.unsplash.com/photo-1534943441045-1089b82b9560?auto=format&fit=crop&w=800&q=80'
            ]
        },
        {
            'name': 'Boal Fish (River Boal)',
            'bangla_name': 'নদীর বড় বোয়াল মাছ',
            'slug': 'boal-fish-river',
            'category': cat_map['river-fish'],
            'short_description': 'Rich scaleless river predator fish. Highly gelatinous and rich in natural collagen.',
            'full_description': 'Native Meghna catch. Cooked with spicy caramelised onions and green chilies (Boal Bhuna).',
            'origin': 'Meghna River, Bhola',
            'freshness_grade': 'Fresh Morning River Catch',
            'unit': UnitType.KG,
            'standard_weight_range': '≈ 2 – 4 kg (per piece)',
            'base_price': Decimal('750.00'),
            'price_display_type': PriceDisplayType.INDICATIVE,
            'price_notice_label': 'Indicative Rate',
            'min_order_qty': Decimal('1.0'),
            'step_qty': Decimal('0.5'),
            'is_featured': False,
            'is_popular': False,
            'is_fresh_arrival': True,
            'images': [
                'https://images.unsplash.com/photo-1544551763-46a013bb70d5?auto=format&fit=crop&w=800&q=80'
            ]
        },
        {
            'name': 'Live Shing Fish (Deshi Shing)',
            'bangla_name': 'দেশি জ্যান্ত শিং মাছ',
            'slug': 'live-shing-fish-deshi',
            'category': cat_map['live-fish'],
            'short_description': 'Live native stinging catfish. Revered for immense nutritional convalescent benefits.',
            'full_description': 'Delivered 100% alive in water pouches. Superb for gentle broths (Shing Macher Jhol) for recovery and family health.',
            'origin': 'Haor Basin, Netrokona',
            'freshness_grade': '100% Live Swimming',
            'unit': UnitType.KG,
            'standard_weight_range': '≈ 15 – 20 pieces per kg',
            'base_price': Decimal('700.00'),
            'price_display_type': PriceDisplayType.INDICATIVE,
            'price_notice_label': 'Live Market Rate',
            'min_order_qty': Decimal('0.5'),
            'step_qty': Decimal('0.5'),
            'is_featured': True,
            'is_popular': True,
            'is_fresh_arrival': False,
            'images': [
                'https://images.unsplash.com/photo-1524704654690-b56c05c78a00?auto=format&fit=crop&w=800&q=80'
            ]
        },
        {
            'name': 'Chital Fish (Chitol)',
            'bangla_name': 'নদীর চিতল মাছের পেটি ও মুইঠ্যা',
            'slug': 'chital-fish-river',
            'category': cat_map['premium-fish'],
            'short_description': 'Royalty of Bengali river fish. Rich fatty Peti (belly) and delicious Muitha meatballs.',
            'full_description': 'Grand freshwater fish from the deep bends of the Padma. Treasured for Chitol Muitha and deep-fried Peti.',
            'origin': 'Padma River Basin',
            'freshness_grade': 'Trophy Grade A+',
            'unit': UnitType.KG,
            'standard_weight_range': '≈ 3 – 5 kg (per piece)',
            'base_price': Decimal('1150.00'),
            'price_display_type': PriceDisplayType.INDICATIVE,
            'price_notice_label': 'Indicative Price (Subject to Confirmation)',
            'min_order_qty': Decimal('1.0'),
            'step_qty': Decimal('0.5'),
            'is_featured': True,
            'is_popular': False,
            'is_fresh_arrival': True,
            'images': [
                'https://images.unsplash.com/photo-1544551763-46a013bb70d5?auto=format&fit=crop&w=800&q=80'
            ]
        }
    ]

    for pdata in products_data:
        images = pdata.pop('images', [])
        p, _ = Product.objects.update_or_create(
            slug=pdata['slug'],
            defaults=pdata
        )

        # Images
        p.images.all().delete()
        for idx, img_url in enumerate(images):
            ProductImage.objects.create(
                product=p,
                image_url=img_url,
                is_primary=(idx == 0),
                display_order=idx
            )

        # Inventory
        inv, _ = Inventory.objects.get_or_create(
            product=p,
            defaults={
                'available_quantity': Decimal('45.00'),
                'low_stock_threshold': Decimal('5.00'),
                'track_stock': True,
                'is_out_of_stock': False
            }
        )

        # Initial price history
        if not p.price_history.exists():
            PriceHistory.objects.create(
                product=p,
                previous_price=p.base_price - Decimal('50.00'),
                new_price=p.base_price,
                reason="Morning landing wholesale auction baseline",
                changed_by=admin_user
            )

    print(f"✅ Created {len(products_data)} fresh fish products with images and inventories.")

    # 5. Content: Banners matching screenshot
    Banner.objects.all().delete()
    Banner.objects.create(
        title="Fresh River & Sea Fish",
        subtitle="Direct from trusted fishermen to your home. 100% chemical-free morning catch.",
        badge_text="Daily Fresh Catch",
        button_text="Shop Now →",
        link_url="/products",
        image_url="https://images.unsplash.com/photo-1544551763-46a013bb70d5?auto=format&fit=crop&w=1200&q=80",
        display_order=1,
        is_active=True
    )
    Banner.objects.create(
        title="Padma River Hilsa Festival",
        subtitle="Authentic Chandpur silver Ilish delivered to your doorstep with certified weight.",
        badge_text="Season Highlight",
        button_text="Order Ilish Now",
        link_url="/products/hilsa-ilish-padma",
        image_url="https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?auto=format&fit=crop&w=1200&q=80",
        display_order=2,
        is_active=True
    )

    # 6. Content: Testimonials
    Testimonial.objects.all().delete()
    testimonials = [
        ("Tanvir Ahmed", "Mirpur DOHS, Dhaka", 5, "The Padma Ilish was remarkably fresh and had that authentic sweet river taste! The WhatsApp confirmation made weighing and cutting instructions so transparent."),
        ("Dr. Farhana Yasmin", "Gulshan-2, Dhaka", 5, "I never buy fish from unverified markets anymore. Fish Dock confirms exact morning rates, sends photos on WhatsApp before delivery, and cleans the fish impeccably."),
        ("Mahbubur Rahman", "Uttara Sector 7", 5, "Ordered Tiger Prawns and Rui fish. Both were iced properly, delivered within 3 hours, and the prices were completely honest. Highly recommended.")
    ]
    for name, area, rating, comment in testimonials:
        Testimonial.objects.create(customer_name=name, customer_area=area, rating=rating, comment=comment)

    # 7. Content: FAQs
    FAQ.objects.all().delete()
    faqs = [
        ("Why are fish prices listed as indicative rather than fixed checkout?", "Fish market prices change every single morning based on river landing volumes, coastal tides, weather conditions, and seasonal availability. By confirming prices and exact piece weights on WhatsApp before dispatch, we ensure you only pay for genuine market value and real weight — no inflated buffers."),
        ("How does the WhatsApp order workflow work?", "1. Select your preferred fish, quantities, and cutting choices on the website.\n2. Submit your delivery request (guest checkout allowed).\n3. You are redirected to our WhatsApp Business hotline with a pre-filled order summary.\n4. Our team weighs the fresh catch, sends photos/details if requested, confirms final amount, and dispatches your order."),
        ("Can I request specific cutting styles (e.g., Curry Cut, Fry Cut, Cleaned)?", "Yes! You can choose whole fish, curry cut pieces, head cleaned & split, or custom slices during order request, and reinforce any custom preference directly via WhatsApp."),
        ("How do you guarantee freshness and chemical-free fish?", "Our fish are caught overnight and landed at dawn at Chandpur, Barisal, and Cox's Bazar. We transport them directly in insulated food-grade ice boxes with zero formaldehyde or chemical preservation.")
    ]
    for idx, (q, a) in enumerate(faqs):
        FAQ.objects.create(question=q, answer=a, display_order=idx)

    # 8. Sample Real Orders in Different Lifecycle Stages
    Order.objects.all().delete()

    sample_orders = [
        {
            'order_ref': 'FD-2026-1001',
            'name': 'Shakil Hasan',
            'phone': '+8801812345678',
            'address': 'House 14, Road 5, Block B, Mirpur-2',
            'area': 'Mirpur, Dhaka',
            'status': OrderStatus.PENDING_CONFIRMATION,
            'whatsapp_status': WhatsAppStatus.NOT_CONTACTED,
            'notes': 'Please keep the Ilish eggs intact if present.',
            'items': [
                ('hilsa-ilish-padma', Decimal('1.0'), Decimal('1350.00'), 'Curry Cut (Pieces)'),
                ('rohu-rui-river', Decimal('1.5'), Decimal('525.00'), 'Curry Cut (Pieces)')
            ],
            'final_amount': None
        },
        {
            'order_ref': 'FD-2026-1002',
            'name': 'Amina Begum',
            'phone': '+8801912345679',
            'address': 'Flat 4B, Concord Tower, Banani',
            'area': 'Banani, Dhaka',
            'status': OrderStatus.PRICE_CONFIRMED,
            'whatsapp_status': WhatsAppStatus.CONFIRMED_VIA_WHATSAPP,
            'notes': 'Confirmed on WhatsApp. Exact Ilish weight is 1.12kg.',
            'items': [
                ('hilsa-ilish-padma', Decimal('1.12'), Decimal('1512.00'), 'Whole Fish (Gutted)'),
                ('tiger-prawn-bagda', Decimal('1.0'), Decimal('950.00'), 'Whole with Shell')
            ],
            'final_amount': Decimal('2462.00')
        },
        {
            'order_ref': 'FD-2026-1003',
            'name': 'Kamrul Ahsan',
            'phone': '+8801712345680',
            'address': 'Plot 45, Sector 11, Uttara',
            'area': 'Uttara, Dhaka',
            'status': OrderStatus.DELIVERED,
            'whatsapp_status': WhatsAppStatus.CONFIRMED_VIA_WHATSAPP,
            'notes': 'Delivered successfully at 11:30 AM.',
            'items': [
                ('pabda-fish-deshi', Decimal('1.0'), Decimal('650.00'), 'Cleaned Whole'),
                ('live-shing-fish-deshi', Decimal('1.0'), Decimal('700.00'), 'Live in Water')
            ],
            'final_amount': Decimal('1410.00')
        }
    ]

    for s in sample_orders:
        order = Order.objects.create(
            order_reference=s['order_ref'],
            customer_name=s['name'],
            customer_phone=s['phone'],
            delivery_address=s['address'],
            delivery_area=s['area'],
            status=s['status'],
            whatsapp_status=s['whatsapp_status'],
            customer_notes=s['notes'],
            final_confirmed_amount=s['final_amount'],
            delivery_fee=Decimal('60.00')
        )

        subtotal = Decimal('0.00')
        for slug, qty, total, cutting in s['items']:
            prod = Product.objects.get(slug=slug)
            subtotal += total
            OrderItem.objects.create(
                order=order,
                product=prod,
                product_name_snapshot=prod.name,
                unit_snapshot=prod.unit,
                standard_weight_range_snapshot=prod.standard_weight_range or "",
                quantity=qty,
                unit_price_snapshot=prod.base_price,
                indicative_total=total,
                final_unit_price=prod.base_price if s['final_amount'] else None,
                final_total=total if s['final_amount'] else None,
                cutting_instruction=cutting
            )
        order.indicative_subtotal = subtotal
        order.save()

        OrderStatusHistory.objects.create(
            order=order,
            previous_status=None,
            new_status=s['status'],
            notes=f"Order seeded with status {s['status']}"
        )

    print("✅ Created sample lifecycle orders.")
    print("✨ Database seeding complete! Fish Dock Backend is ready.")

if __name__ == '__main__':
    seed()

