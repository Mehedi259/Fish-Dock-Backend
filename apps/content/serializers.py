from rest_framework import serializers
from .models import Banner, Testimonial, FAQ

class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ['id', 'title', 'subtitle', 'badge_text', 'image_url', 'button_text', 'link_url', 'display_order', 'is_active', 'created_at']

class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = ['id', 'customer_name', 'customer_area', 'rating', 'comment', 'avatar_url', 'is_active', 'created_at']

class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ['id', 'question', 'answer', 'category', 'display_order', 'is_active', 'created_at']

