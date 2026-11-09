from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User, UserRole
from categories.models import Category
from products.models import Product, UnitType, PriceDisplayType
from orders.models import Order, OrderStatus, WhatsAppStatus
from system_settings.models import SystemSetting

class FishDockAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Admin user
        self.admin = User.objects.create_superuser(
            username='testadmin',
            email='admin@test.com',
            password='testpassword123',
            role=UserRole.SUPER_ADMIN
        )

        # Settings
        SystemSetting.objects.create(
            key='WHATSAPP_BUSINESS_NUMBER',
            value='+8801712345678',
            is_public=True
        )
        SystemSetting.objects.create(
            key='DEFAULT_DELIVERY_FEE',
            value='60.00',
            is_public=True
        )

        # Category
        self.category = Category.objects.create(
            name='River Fish',
            slug='river-fish',
            icon_name='waves'
        )

        # Product
        self.product = Product.objects.create(
            category=self.category,
            name='Hilsa (Padma Ilish)',
            bangla_name='চাঁদপুরের পদ্মার রুপালী ইলিশ',
            slug='hilsa-padma-ilish',
            unit=UnitType.KG,
            standard_weight_range='≈ 800g – 1kg',
            base_price=Decimal('1350.00'),
            price_display_type=PriceDisplayType.INDICATIVE,
            is_active=True
        )

    def test_public_products_endpoint(self):
        response = self.client.get('/api/v1/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check standard paginated response structure
        self.assertTrue(response.data['success'])
        self.assertGreaterEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Hilsa (Padma Ilish)')

    def test_public_categories_endpoint(self):
        response = self.client.get('/api/v1/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data'][0]['slug'], 'river-fish')

    def test_guest_order_creation_and_whatsapp_generation(self):
        order_payload = {
            "customer_name": "Rahim Uddin",
            "customer_phone": "+8801711223344",
            "customer_email": "rahim@example.com",
            "delivery_address": "House 12, Road 4, Sector 3, Uttara",
            "delivery_area": "Uttara, Dhaka",
            "delivery_city": "Dhaka",
            "preferred_delivery_slot": "Morning (8 AM - 12 PM)",
            "customer_notes": "Please clean gills and send whole fish.",
            "items": [
                {
                    "product_id": str(self.product.id),
                    "quantity": 1.5,
                    "cutting_instruction": "Whole Fish (Gutted & Cleaned)"
                }
            ]
        }

        response = self.client.post('/api/v1/orders/', order_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        
        order_data = response.data['data']['order']
        whatsapp_data = response.data['data']['whatsapp']

        # Verify order in DB
        self.assertTrue(order_data['order_reference'].startswith('FD-'))
        self.assertEqual(order_data['status'], OrderStatus.PENDING_CONFIRMATION)
        self.assertEqual(Decimal(str(order_data['indicative_subtotal'])), Decimal('2025.00'))

        # Verify WhatsApp deep link and encoded content
        self.assertIn('https://wa.me/8801712345678?text=', whatsapp_data['deep_link'])
        self.assertIn('Rahim Uddin', whatsapp_data['message_text'])
        self.assertIn('Hilsa (Padma Ilish)', whatsapp_data['message_text'])
        self.assertIn('Indicative Subtotal', whatsapp_data['message_text'])

    def test_order_tracking_endpoint(self):
        # Create an order first
        order = Order.objects.create(
            order_reference='FD-2026-9999',
            customer_name='Karim Mia',
            customer_phone='+8801811223344',
            delivery_address='Mirpur-10, Dhaka',
            status=OrderStatus.PENDING_CONFIRMATION
        )

        response = self.client.get('/api/v1/orders/track/?reference=FD-2026-9999')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['order']['order_reference'], 'FD-2026-9999')

    def test_admin_price_update_and_audit_history(self):
        # Authenticate admin
        self.client.force_authenticate(user=self.admin)

        update_payload = {
            "new_price": 1420.00,
            "reason": "Wholesale morning landing price rose at Chandpur",
            "notes": "Limited catch today due to rough weather"
        }
        url = f"/api/v1/pricing/update/{self.product.id}/"
        response = self.client.post(url, update_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Refresh product
        self.product.refresh_from_db()
        self.assertEqual(self.product.base_price, Decimal('1420.00'))

        # Check PriceHistory recorded
        history = self.product.price_history.first()
        self.assertIsNotNone(history)
        self.assertEqual(history.previous_price, Decimal('1350.00'))
        self.assertEqual(history.new_price, Decimal('1420.00'))
        self.assertEqual(history.reason, "Wholesale morning landing price rose at Chandpur")
