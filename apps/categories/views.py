from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from .models import Category
from .serializers import CategorySerializer
from accounts.permissions import IsAdminOrStaff
from core.utils import api_response

class CategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        # Admin sees all, public sees active only
        if self.request.user and self.request.user.is_authenticated and self.request.user.is_admin_or_staff:
            return Category.objects.all().order_by('display_order', 'name')
        return Category.objects.filter(is_active=True).order_by('display_order', 'name')

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminOrStaff()]
        return [permissions.AllowAny()]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return api_response(success=True, data=serializer.data)

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAdminOrStaff()]
        return [permissions.AllowAny()]

class CategoryReorderView(APIView):
    permission_classes = [IsAdminOrStaff]

    def post(self, request):
        """
        Expects a list of objects: [{'id': '...', 'display_order': 0}, ...]
        """
        items = request.data.get('items', [])
        for item in items:
            cat_id = item.get('id')
            order = item.get('display_order')
            if cat_id is not None and order is not None:
                Category.objects.filter(id=cat_id).update(display_order=order)
        return api_response(success=True, message="Categories reordered successfully")
