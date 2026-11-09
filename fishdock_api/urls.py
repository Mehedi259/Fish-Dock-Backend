"""
Fish Dock Backend API URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

# Accounts
from accounts.views import (
    CustomTokenObtainPairView,
    CurrentUserProfileView,
    UserListView,
    UserDetailView
)

# Categories
from categories.views import (
    CategoryListCreateView,
    CategoryDetailView,
    CategoryReorderView
)

# Products
from products.views import (
    ProductListCreateView,
    ProductDetailView,
    ProductToggleStatusView
)

# Pricing
from pricing.views import (
    PriceHistoryListView,
    UpdateProductPriceView
)

# Inventory
from inventory.views import (
    InventoryListView,
    InventoryAdjustView
)

# Orders
from orders.views import (
    CreateOrderView,
    TrackOrderView,
    OrderListAdminView,
    OrderDetailAdminView,
    UpdateOrderStatusView,
    ConfirmOrderPriceView,
    ExportOrdersCSVView
)

# Content
from content.views import (
    BannerListCreateView,
    BannerDetailView,
    TestimonialListCreateView,
    FAQListCreateView
)

# System Settings
from system_settings.views import (
    PublicSettingsView,
    AdminSettingsListUpdateView
)

# Analytics
from analytics.views import DashboardOverviewView

api_v1_patterns = [
    # Auth
    path('auth/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/me/', CurrentUserProfileView.as_view(), name='user_profile'),
    path('auth/users/', UserListView.as_view(), name='admin_user_list'),
    path('auth/users/<int:pk>/', UserDetailView.as_view(), name='admin_user_detail'),

    # Categories
    path('categories/', CategoryListCreateView.as_view(), name='category_list_create'),
    path('categories/<slug:slug>/', CategoryDetailView.as_view(), name='category_detail'),
    path('categories/reorder/', CategoryReorderView.as_view(), name='category_reorder'),

    # Products
    path('products/', ProductListCreateView.as_view(), name='product_list_create'),
    path('products/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('products/<uuid:pk>/toggle-status/', ProductToggleStatusView.as_view(), name='product_toggle_status'),

    # Dynamic Pricing
    path('pricing/history/', PriceHistoryListView.as_view(), name='price_history_list'),
    path('pricing/update/<uuid:pk>/', UpdateProductPriceView.as_view(), name='update_product_price'),

    # Inventory
    path('inventory/', InventoryListView.as_view(), name='inventory_list'),
    path('inventory/adjust/<uuid:pk>/', InventoryAdjustView.as_view(), name='inventory_adjust'),

    # Orders (Customer & Guest)
    path('orders/', CreateOrderView.as_view(), name='create_order'),
    path('orders/track/', TrackOrderView.as_view(), name='track_order'),

    # Orders (Admin)
    path('orders/admin/', OrderListAdminView.as_view(), name='admin_order_list'),
    path('orders/admin/<uuid:id>/', OrderDetailAdminView.as_view(), name='admin_order_detail'),
    path('orders/admin/<uuid:pk>/status/', UpdateOrderStatusView.as_view(), name='admin_order_update_status'),
    path('orders/admin/<uuid:pk>/confirm-price/', ConfirmOrderPriceView.as_view(), name='admin_order_confirm_price'),
    path('orders/admin/export-csv/', ExportOrdersCSVView.as_view(), name='admin_orders_export_csv'),

    # Content
    path('content/banners/', BannerListCreateView.as_view(), name='banner_list'),
    path('content/banners/<uuid:pk>/', BannerDetailView.as_view(), name='banner_detail'),
    path('content/testimonials/', TestimonialListCreateView.as_view(), name='testimonial_list'),
    path('content/faqs/', FAQListCreateView.as_view(), name='faq_list'),

    # System Settings
    path('settings/public/', PublicSettingsView.as_view(), name='public_settings'),
    path('settings/admin/', AdminSettingsListUpdateView.as_view(), name='admin_settings'),

    # Analytics
    path('analytics/dashboard/', DashboardOverviewView.as_view(), name='dashboard_overview'),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(api_v1_patterns)),

    # OpenAPI Schema & Swagger
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
