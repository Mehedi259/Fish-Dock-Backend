# Fish Dock – Backend API Service

Official Django REST Framework backend for the **Fish Dock** fresh seafood e-commerce platform.

## Architecture & Technology Stack
- **Framework**: Python 3.12+ / 3.14, Django 6+, Django REST Framework
- **Authentication**: JWT (`djangorestframework-simplejwt`) with role-based permissions
- **Database**: PostgreSQL (Production/Docker), SQLite (Local zero-config development)
- **Caching & Tasks**: Redis 7, Celery background tasks
- **API Documentation**: OpenAPI 3.0 schema via `drf-spectacular` & Swagger UI
- **Containerization**: Multi-stage Dockerfile and Docker Compose orchestration

## Key Modules
- `apps.core`: Base models, standard API response wrappers, custom exception handling, WhatsApp message generator.
- `apps.accounts`: Custom `User` model with roles (`SUPER_ADMIN`, `ADMIN`, `ORDER_MANAGER`, `INVENTORY_MANAGER`, `CUSTOMER`).
- `apps.categories`: Seafood category management (River, Sea, Prawn, Crab, Live, Premium).
- `apps.products`: Seafood catalog, images, freshness grades, piece specs, dynamic price labels.
- `apps.pricing`: Dynamic price management and immutable `PriceHistory` audit trail.
- `apps.inventory`: Fish stock tracking, digital scale reservation, and waste auditing.
- `apps.orders`: Order requests, guest checkout, indicative snapshots, scale weighing confirmation, WhatsApp deep links.
- `apps.content`: Banners, testimonials, FAQs.
- `apps.system_settings`: Centralized WhatsApp business hotline, tariffs, and disclaimer text.
- `apps.analytics`: Dashboard metrics, sales volume, top catches, and daily trend analysis.

## Running Locally

```bash
# 1. Activate Virtual Environment
source .venv/bin/activate

# 2. Run Database Migrations
python manage.py migrate

# 3. Seed Fresh Catch Data & Demo Users
python seed_data.py

# 4. Start Development Server on Port 8001
python manage.py runserver 127.0.0.1:8001
```

## Running with Docker Compose

```bash
# Orchestrates Postgres, Redis, Django API, Celery, Website, and Dashboard
docker-compose up --build -d
```

## Default Admin Credentials
- **Super Admin**: `admin` / `admin123`
- **Order Manager**: `ordermanager` / `order123`

## API Endpoints
- Swagger UI Documentation: `http://127.0.0.1:8001/api/docs/`
- OpenAPI Schema: `http://127.0.0.1:8001/api/schema/`
- Products API: `GET /api/v1/products/`
- Guest Order Placement: `POST /api/v1/orders/`
- Order Live Tracking: `GET /api/v1/orders/track/?reference=FD-2026-XXXX`
- Admin Order Management: `GET /api/v1/orders/admin/`
- Final Price Confirmation: `POST /api/v1/orders/admin/<id>/confirm-price/`
- Dynamic Price Update: `POST /api/v1/pricing/update/<product_id>/`
- Inventory Adjustment: `POST /api/v1/inventory/adjust/<id>/`
- Public Settings: `GET /api/v1/settings/public/`
- Dashboard Analytics: `GET /api/v1/analytics/dashboard/`

## Running Automated Tests

```bash
python manage.py test tests
python test_e2e.py
```

