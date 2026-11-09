from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from .models import SystemSetting
from .serializers import SystemSettingSerializer
from accounts.permissions import IsAdminOrStaff
from core.utils import api_response

class PublicSettingsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        settings = SystemSetting.objects.filter(is_public=True)
        data = {s.key: s.value for s in settings}
        # Provide defaults if not found
        defaults = {
            'WHATSAPP_BUSINESS_NUMBER': '+8801700000000',
            'STORE_NAME': 'Fish Dock',
            'STORE_TAGLINE': 'Fresh River & Sea Fish Direct from Trusted Fishermen',
            'CURRENCY_SYMBOL': '৳',
            'CURRENCY_CODE': 'BDT',
            'DEFAULT_DELIVERY_FEE': '60',
            'FREE_DELIVERY_THRESHOLD': '2000',
            'PRICE_DISCLAIMER_TEXT': 'Daily fish prices fluctuate with morning catch and market conditions. Final price and weight will be confirmed via WhatsApp before delivery.',
            'STORE_STATUS': 'open',
            'CONTACT_PHONE': '+8801700000000',
            'CONTACT_EMAIL': 'care@fishdock.com',
            'OFFICE_ADDRESS': 'Fish Market Hub, Mirpur-1, Dhaka-1216',
        }
        for k, v in defaults.items():
            if k not in data:
                data[k] = v
        return api_response(success=True, data=data)


class AdminSettingsListUpdateView(APIView):
    permission_classes = [IsAdminOrStaff]

    def get(self, request):
        settings = SystemSetting.objects.all().order_by('key')
        serializer = SystemSettingSerializer(settings, many=True)
        return api_response(success=True, data=serializer.data)

    def post(self, request):
        """
        Updates multiple settings at once:
        {"settings": [{"key": "WHATSAPP_BUSINESS_NUMBER", "value": "+8801711111111"}, ...]}
        """
        items = request.data.get('settings', [])
        for item in items:
            key = item.get('key')
            val = item.get('value')
            desc = item.get('description')
            is_pub = item.get('is_public')
            if key and val is not None:
                setting, _ = SystemSetting.objects.get_or_create(key=key)
                setting.value = str(val)
                if desc is not None:
                    setting.description = desc
                if is_pub is not None:
                    setting.is_public = is_pub
                setting.save()

        return api_response(success=True, message="System settings successfully updated")
