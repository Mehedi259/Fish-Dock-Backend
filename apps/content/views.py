from rest_framework import generics, permissions
from .models import Banner, Testimonial, FAQ
from .serializers import BannerSerializer, TestimonialSerializer, FAQSerializer
from accounts.permissions import IsAdminOrStaff
from core.utils import api_response

class BannerListCreateView(generics.ListCreateAPIView):
    serializer_class = BannerSerializer

    def get_queryset(self):
        user = self.request.user
        if user and user.is_authenticated and user.is_admin_or_staff:
            return Banner.objects.all().order_by('display_order')
        return Banner.objects.filter(is_active=True).order_by('display_order')

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminOrStaff()]
        return [permissions.AllowAny()]

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return api_response(success=True, data=serializer.data)

class BannerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    permission_classes = [IsAdminOrStaff]

class TestimonialListCreateView(generics.ListCreateAPIView):
    serializer_class = TestimonialSerializer

    def get_queryset(self):
        user = self.request.user
        if user and user.is_authenticated and user.is_admin_or_staff:
            return Testimonial.objects.all()
        return Testimonial.objects.filter(is_active=True)

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminOrStaff()]
        return [permissions.AllowAny()]

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return api_response(success=True, data=serializer.data)

class FAQListCreateView(generics.ListCreateAPIView):
    serializer_class = FAQSerializer

    def get_queryset(self):
        user = self.request.user
        if user and user.is_authenticated and user.is_admin_or_staff:
            return FAQ.objects.all().order_by('display_order')
        return FAQ.objects.filter(is_active=True).order_by('display_order')

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminOrStaff()]
        return [permissions.AllowAny()]

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return api_response(success=True, data=serializer.data)
