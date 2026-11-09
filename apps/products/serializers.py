from rest_framework import serializers
from .models import Product, ProductImage, UnitType, PriceDisplayType
from categories.models import Category
from categories.serializers import CategorySerializer

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image_url', 'alt_text', 'is_primary', 'display_order']

class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    primary_image_url = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'bangla_name', 'slug', 'category', 'category_name',
            'category_slug', 'short_description', 'origin', 'freshness_grade',
            'unit', 'standard_weight_range', 'base_price', 'price_display_type',
            'price_notice_label', 'market_price_updated_at', 'min_order_qty',
            'max_order_qty', 'step_qty', 'allows_cutting_instructions',
            'is_active', 'is_featured', 'is_popular', 'is_seasonal',
            'is_fresh_arrival', 'primary_image_url'
        ]

class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    primary_image_url = serializers.ReadOnlyField()
    in_stock = serializers.SerializerMethodField()
    available_stock = serializers.SerializerMethodField()
    related_products = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'bangla_name', 'slug', 'category',
            'short_description', 'full_description', 'origin', 'freshness_grade',
            'unit', 'standard_weight_range', 'base_price', 'price_display_type',
            'price_notice_label', 'market_price_updated_at', 'min_order_qty',
            'max_order_qty', 'step_qty', 'allows_cutting_instructions',
            'is_active', 'is_featured', 'is_popular', 'is_seasonal',
            'is_fresh_arrival', 'views_count', 'images', 'primary_image_url',
            'in_stock', 'available_stock', 'related_products',
            'created_at', 'updated_at'
        ]

    def get_in_stock(self, obj):
        if hasattr(obj, 'inventory'):
            return not obj.inventory.is_out_of_stock
        return True

    def get_available_stock(self, obj):
        if hasattr(obj, 'inventory'):
            return float(obj.inventory.available_quantity)
        return None

    def get_related_products(self, obj):
        related = Product.objects.filter(category=obj.category, is_active=True).exclude(id=obj.id)[:4]
        return ProductListSerializer(related, many=True).data

class ProductWriteSerializer(serializers.ModelSerializer):
    image_urls = serializers.ListField(
        child=serializers.URLField(),
        required=False,
        write_only=True
    )

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'bangla_name', 'slug', 'category',
            'short_description', 'full_description', 'origin', 'freshness_grade',
            'unit', 'standard_weight_range', 'base_price', 'price_display_type',
            'price_notice_label', 'min_order_qty', 'max_order_qty', 'step_qty',
            'allows_cutting_instructions', 'is_active', 'is_featured',
            'is_popular', 'is_seasonal', 'is_fresh_arrival', 'image_urls'
        ]

    def create(self, validated_data):
        image_urls = validated_data.pop('image_urls', [])
        product = Product.objects.create(**validated_data)
        for idx, url in enumerate(image_urls):
            ProductImage.objects.create(
                product=product,
                image_url=url,
                is_primary=(idx == 0),
                display_order=idx
            )
        return product

    def update(self, instance, validated_data):
        image_urls = validated_data.pop('image_urls', None)
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        if image_urls is not None:
            instance.images.all().delete()
            for idx, url in enumerate(image_urls):
                ProductImage.objects.create(
                    product=instance,
                    image_url=url,
                    is_primary=(idx == 0),
                    display_order=idx
                )
        return instance

