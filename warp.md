# 🚀 MALABRO Backend - Warp Quick Reference

> **Quick commands and workflows for the MALABRO eSHOP FastAPI backend**

## 🎯 Quick Start

### First Time Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env

# Initialize database
python -c "from app.db.init_db import init_db; init_db()"
```

### Start Development Server
```bash
# Activate virtual environment
source venv/bin/activate

# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Access Points:**
- 🌐 API: http://localhost:8000
- 📖 Swagger Docs: http://localhost:8000/docs
- 📚 ReDoc: http://localhost:8000/redoc

---

## 📁 Project Structure

```
malabro-backend/
├── app/
│   ├── api/v1/endpoints/    # API route handlers
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── order.py         # Order management
│   │   ├── products.py      # Product CRUD
│   │   ├── admin.py         # Admin operations
│   │   └── categories.py    # Category management
│   ├── core/                # Core configuration
│   │   ├── config.py        # Settings & environment
│   │   └── security.py      # JWT & password handling
│   ├── crud/                # Database operations
│   ├── db/                  # Database setup
│   │   ├── session.py       # DB connection
│   │   └── init_db.py       # Database initialization
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   └── utils/               # Utility functions
├── .env                     # Environment variables
├── requirements.txt         # Python dependencies
└── malabro_eshop.db        # SQLite database (dev)
```

---

## 🔑 Essential Commands

### Database Operations
```bash
# Initialize fresh database with sample data
python -c "from app.db.init_db import init_db; init_db()"

# Inspect database structure
python inspect_db.py

# Test database configuration
python test_database_config.py
```

### Testing
```bash
# Test server is running
python test_server.py

# Test email configuration
python test_sendgrid_direct.py
python test_real_email.py

# Test Supabase connection (if using)
python test_supabase_connection.py
```

### Development
```bash
# Install new dependency
pip install <package>
pip freeze > requirements.txt

# Format code (if using black)
black app/

# Run linter (if using pylint)
pylint app/
```

---

## 🔐 Authentication Flow

### 1. Register New User
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securepass123",
    "full_name": "Test User"
  }'
```

### 2. Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securepass123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### 3. Use Token in Requests
```bash
# Store token
TOKEN="your_jwt_token_here"

# Make authenticated request
curl -X GET "http://localhost:8000/api/v1/orders/" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🛒 Common API Operations

### Products

**List All Products:**
```bash
curl http://localhost:8000/api/v1/products/
```

**Get Single Product:**
```bash
curl http://localhost:8000/api/v1/products/1
```

**Create Product (Admin):**
```bash
curl -X POST "http://localhost:8000/api/v1/products/" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Fresh Tomatoes",
    "description": "Organic tomatoes",
    "price": 2500,
    "category_id": 1,
    "unit_of_measure_id": 1,
    "stock_quantity": 100,
    "image_url": "/uploads/tomatoes.jpg"
  }'
```

### Orders

**Create Order:**
```bash
curl -X POST "http://localhost:8000/api/v1/orders/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "John Doe",
    "customer_email": "john@example.com",
    "customer_phone": "+225 XX XXX XX XX",
    "shipping_address": "123 Main St",
    "shipping_city": "Abidjan",
    "items": [
      {
        "product_id": 1,
        "quantity": 2
      }
    ]
  }'
```

**Get User Orders:**
```bash
curl -X GET "http://localhost:8000/api/v1/orders/" \
  -H "Authorization: Bearer $TOKEN"
```

**Get Order by ID:**
```bash
curl -X GET "http://localhost:8000/api/v1/orders/1" \
  -H "Authorization: Bearer $TOKEN"
```

### Admin Operations

**List All Orders (Admin):**
```bash
curl -X GET "http://localhost:8000/api/v1/admin/orders/" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**Update Order Status (Admin):**
```bash
curl -X PUT "http://localhost:8000/api/v1/admin/orders/1/status" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "processing"
  }'
```

**Available Order Statuses:**
- `pending` - Order placed, awaiting payment
- `processing` - Payment received, preparing order
- `shipped` - Order shipped
- `delivered` - Order delivered
- `cancelled` - Order cancelled

---

## ⚙️ Environment Configuration

### Required Variables (.env)

```bash
# Database
DATABASE_URL=sqlite:///./malabro_eshop.db

# JWT Authentication
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=3600

# SendGrid Email
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=SG.your-sendgrid-api-key
SENDGRID_FROM_EMAIL=noreply@yourdomain.com
ADMIN_EMAIL=admin@yourdomain.com

# CORS (Frontend URLs)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Optional: AI Features
GROQ_API_KEY=your-groq-api-key
```

### Generate Strong Secret Key
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 📧 Email System

### SendGrid Setup Steps

1. **Create Account:** https://sendgrid.com
2. **Get API Key:** Settings → API Keys → Create API Key
3. **Verify Sender:** Settings → Sender Authentication
4. **Update .env:** Add API key to `SMTP_PASSWORD`

### Test Email System
```bash
# Test SendGrid configuration
python test_sendgrid_direct.py

# Test full email system
curl -X POST "http://localhost:8000/api/v1/notifications/test-email" \
  -H "Content-Type: application/json"
```

---

## 🐳 Docker Deployment

### Build Image
```bash
docker build -t malabro-backend .
```

### Run Container
```bash
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  --name malabro-api \
  malabro-backend
```

### View Logs
```bash
docker logs -f malabro-api
```

### Stop Container
```bash
docker stop malabro-api
docker rm malabro-api
```

---

## ☁️ Production Deployment

### Google Cloud Run

```bash
# Build and submit to Cloud Build
gcloud builds submit --tag gcr.io/PROJECT_ID/malabro-backend

# Deploy to Cloud Run
gcloud run deploy malabro-backend \
  --image gcr.io/PROJECT_ID/malabro-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL="postgresql://..." \
  --set-env-vars SECRET_KEY="..." \
  --set-env-vars SMTP_PASSWORD="..."
```

### Production Checklist

- [ ] Use PostgreSQL instead of SQLite
- [ ] Set strong `SECRET_KEY`
- [ ] Configure proper CORS origins
- [ ] Set up SendGrid production account
- [ ] Enable HTTPS
- [ ] Set up monitoring/logging
- [ ] Configure backup strategy
- [ ] Set up rate limiting
- [ ] Review security settings

---

## 🔍 Troubleshooting

### Server Won't Start

**Problem:** `ModuleNotFoundError: No module named 'app'`
```bash
# Solution: Ensure you're in project root
cd /opt/malabro-backend
source venv/bin/activate
python -m uvicorn app.main:app --reload
```

### Database Issues

**Problem:** `no such table: users`
```bash
# Solution: Initialize database
python -c "from app.db.init_db import init_db; init_db()"
```

### Email Not Sending

**Problem:** Emails not being delivered
```bash
# Check SendGrid configuration
python test_sendgrid_direct.py

# Verify .env variables
grep SMTP .env
grep SENDGRID .env
```

### Authentication Errors

**Problem:** `401 Unauthorized`
```bash
# Check token is valid
# Get new token by logging in again
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password"}'
```

### Port Already in Use

**Problem:** `Address already in use`
```bash
# Find process using port 8000
lsof -i :8000

# Kill process (use PID from above)
kill -9 <PID>

# Or use different port
uvicorn app.main:app --reload --port 8001
```

---

## 📊 Database Schema Quick Reference

### Main Tables

**users**
- `id` (Primary Key)
- `email` (Unique)
- `hashed_password`
- `full_name`
- `is_active`
- `is_admin`
- `created_at`

**products**
- `id` (Primary Key)
- `name`
- `description`
- `price`
- `category_id` (Foreign Key)
- `unit_of_measure_id` (Foreign Key)
- `stock_quantity`
- `is_active`
- `image_url`

**orders**
- `id` (Primary Key)
- `order_reference` (Unique)
- `customer_name`
- `customer_email`
- `customer_phone`
- `shipping_address`
- `shipping_city`
- `total_amount`
- `status`
- `user_id` (Foreign Key)
- `created_at`

**order_items**
- `id` (Primary Key)
- `order_id` (Foreign Key)
- `product_id` (Foreign Key)
- `quantity`
- `unit_price`
- `subtotal`

---

## 🎨 Development Tips

### VS Code Extensions
- Python
- Pylance
- REST Client (for API testing)
- Thunder Client (alternative to Postman)

### Python Virtual Environment
```bash
# Activate
source venv/bin/activate

# Deactivate
deactivate

# Recreate if corrupted
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Hot Reload
The `--reload` flag automatically restarts the server when you save changes:
```bash
uvicorn app.main:app --reload
```

### Debug Mode
```bash
# Enable debug logging
LOG_LEVEL=DEBUG uvicorn app.main:app --reload
```

---

## 📚 Additional Resources

- **FastAPI Docs:** https://fastapi.tiangolo.com
- **SQLAlchemy Docs:** https://docs.sqlalchemy.org
- **SendGrid Docs:** https://docs.sendgrid.com
- **JWT.io:** https://jwt.io (decode/verify tokens)
- **API Testing:** Use `/docs` endpoint for interactive testing

---

## 🚦 Status Checks

### Quick Health Check
```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "api_version": "1.0.0"
}
```

### API Root
```bash
curl http://localhost:8000/
```

---

## 💡 Pro Tips

1. **Use the Interactive Docs**: Visit `/docs` for automatic API documentation and testing
2. **Environment Variables**: Never commit `.env` file - it's in `.gitignore`
3. **Token Expiry**: Default token expires in 60 minutes, re-login if needed
4. **Database Reset**: Run init_db.py to reset and repopulate database
5. **Logs**: Check `app.log` for application logs
6. **CORS Issues**: Add frontend URL to `CORS_ORIGINS` in `.env`

---

**Built with FastAPI ⚡ | SQLAlchemy 🗃️ | SendGrid 📧**

*For detailed documentation, see [README.md](README.md)*

---

## 📦 Delivery Preparation Feature

### New Endpoint: Preparation Summary

**Purpose:** Helps admin prepare deliveries by aggregating all paid orders by product.

#### Get Delivery Preparation Summary

```bash
# Get all paid orders summary
curl -X GET "http://localhost:8000/api/v1/admin/orders/preparation-summary" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

#### With Date Filters

```bash
# Filter by date range
curl -X GET "http://localhost:8000/api/v1/admin/orders/preparation-summary?date_from=2025-10-01&date_to=2025-10-31" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

#### Response Structure

```json
{
  "summary": {
    "total_paid_orders": 11,
    "total_unique_products": 4,
    "total_revenue": 2970.0,
    "last_updated": "2025-10-05T19:52:32"
  },
  "products": [
    {
      "product_id": 2,
      "product_name": "Tomates",
      "total_quantity": 15,
      "unit": "kg",
      "order_count": 6,
      "unique_customers": 2,
      "orders": [
        {
          "order_id": 15,
          "order_reference": "MALABRO-SLISAE",
          "customer_name": "Admin",
          "quantity": 1,
          "created_at": "2025-09-13T09:07:46"
        }
      ]
    }
  ],
  "date_range": {
    "date_from": "2025-10-01",
    "date_to": "2025-10-31"
  }
}
```

#### Use Cases

1. **Daily Preparation List**: View what products to prepare for delivery
2. **Weekly Planning**: Filter by date range for weekly preparation
3. **Stock Management**: Know exact quantities needed by product
4. **Customer Overview**: See which customers ordered each product

#### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `date_from` | string | No | Start date (YYYY-MM-DD) |
| `date_to` | string | No | End date (YYYY-MM-DD) |

#### Status Filter

- Only includes orders with status = `"paid"`
- Excludes pending, cancelled, shipped, and delivered orders
- Manual refresh required (no real-time updates)

#### Example Usage

```bash
# Get today's prep list
TODAY=$(date +%Y-%m-%d)
curl -X GET "http://localhost:8000/api/v1/admin/orders/preparation-summary?date_from=$TODAY&date_to=$TODAY" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Get this week's prep list
WEEK_START=$(date -d "monday" +%Y-%m-%d)
TODAY=$(date +%Y-%m-%d)
curl -X GET "http://localhost:8000/api/v1/admin/orders/preparation-summary?date_from=$WEEK_START&date_to=$TODAY" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

---
