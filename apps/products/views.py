from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from django.db.models import Q
from .models import Product, ProductImage
from .serializers import (
    ProductListSerializer,
    ProductDetailSerializer,
    ProductWriteSerializer
)
from accounts.permissions import IsAdminOrStaff
from core.utils import api_response

class ProductListCreateView(generics.ListCreateAPIView):
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProductWriteSerializer
        return ProductListSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminOrStaff()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        user = self.request.user
        is_admin = bool(user and user.is_authenticated and user.is_admin_or_staff)

        queryset = Product.objects.select_related('category').prefetch_related('images')
        if not is_admin:
            queryset = queryset.filter(is_active=True)

        # Filters
        category_slug = self.request.query_params.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(bangla_name__icontains=search) |
                Q(origin__icontains=search) |
                Q(short_description__icontains=search)
            )

        featured = self.request.query_params.get('featured')
        if featured in ['true', '1', 'True']:
            queryset = queryset.filter(is_featured=True)

        popular = self.request.query_params.get('popular')
        if popular in ['true', '1', 'True']:
            queryset = queryset.filter(is_popular=True)

        seasonal = self.request.query_params.get('seasonal')
        if seasonal in ['true', '1', 'True']:
            queryset = queryset.filter(is_seasonal=True)

        fresh_arrival = self.request.query_params.get('fresh_arrival')
        if fresh_arrival in ['true', '1', 'True']:
            queryset = queryset.filter(is_fresh_arrival=True)

        min_price = self.request.query_params.get('min_price')
        if min_price:
            try:
                queryset = queryset.filter(base_price__gte=float(min_price))
            except ValueError:
                pass

        max_price = self.request.query_params.get('max_price')
        if max_price:
            try:
                queryset = queryset.filter(base_price__lte=float(max_price))
            except ValueError:
                pass

        # Sorting
        sort_by = self.request.query_params.get('sort_by', '-created_at')
        if sort_by == 'price_asc':
            queryset = queryset.order_by('base_price')
        elif sort_by == 'price_desc':
            queryset = queryset.order_by('-base_price')
        elif sort_by == 'popular':
            queryset = queryset.order_by('-is_popular', '-views_count')
        elif sort_by == 'newest':
            queryset = queryset.order_by('-created_at')
        else:
            queryset = queryset.order_by(sort_by)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return api_response(success=True, data=serializer.data)


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ProductWriteSerializer
        return ProductDetailSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAdminOrStaff()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        user = self.request.user
        is_admin = bool(user and user.is_authenticated and user.is_admin_or_staff)
        queryset = Product.objects.select_related('category', 'inventory').prefetch_related('images', 'price_history')
        if not is_admin:
            queryset = queryset.filter(is_active=True)
        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment view count
        Product.objects.filter(id=instance.id).update(views_count=instance.views_count + 1)
        serializer = self.get_serializer(instance)
        return api_response(success=True, data=serializer.data)


class ProductToggleStatusView(APIView):
    permission_classes = [IsAdminOrStaff]

    def post(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
            field = request.data.get('field', 'is_active')
            if hasattr(product, field):
                current_val = getattr(product, field)
                setattr(product, field, not current_val)
                product.save(update_fields=[field])
                return api_response(
                    success=True,
                    message=f"{field} updated to {getattr(product, field)}",
                    data={"id": str(product.id), field: getattr(product, field)}
                )
            return api_response(success=False, message="Invalid field", status=400)
        except Product.DoesNotExist:
            return api_response(success=False, message="Product not found", status=404)
