# MALABRO eSHOP - Backend API

<div align="center">
  <h1>🥬 MALABRO eSHOP Backend</h1>
  <p><strong>FastAPI-powered backend for fresh produce delivery platform</strong></p>
  
  [![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://python.org)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
  [![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0%2B-red?logo=sqlalchemy&logoColor=white)](https://sqlalchemy.org)
  [![SendGrid](https://img.shields.io/badge/SendGrid-Email-1A82E2?logo=sendgrid&logoColor=white)](https://sendgrid.com)
  [![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
</div>

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Database](#database)
- [Email Notifications](#email-notifications)
- [Authentication](#authentication)
- [Deployment](#deployment)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## 🌟 Overview

MALABRO eSHOP Backend is a robust FastAPI-powered REST API that serves as the core engine for a fresh produce delivery platform. Built for the African market, it supports multi-language content, Wave payment integration, and comprehensive order management.

### Key Highlights
- 🚀 **High Performance**: FastAPI with async support
- 📧 **Email Integration**: SendGrid-powered notifications
- 💰 **Payment Ready**: Wave payment integration
- 🔐 **Secure**: JWT authentication with role-based access
- 📱 **Mobile Ready**: RESTful API designed for mobile apps
- 🌍 **Scalable**: Cloud-ready architecture

## ✨ Features

### Core Features
- 🛒 **Product Management**: Complete CRUD operations for products
- 📦 **Order Processing**: End-to-end order lifecycle management
- 👥 **User Management**: Customer and admin user accounts
- 🏷️ **Category System**: Organized product categorization
- 📊 **Inventory Tracking**: Real-time stock management
- 📧 **Email Notifications**: Automated order and payment alerts

### Business Features
- 💳 **Payment Integration**: Wave payment system support
- 📱 **QR Code Generation**: Payment QR codes for Wave
- 🚚 **Delivery Management**: Address and delivery tracking
- 📈 **Admin Dashboard**: Comprehensive admin panel APIs
- 🔄 **Order Status Tracking**: Real-time order updates
- 📊 **Reporting**: Sales and inventory reports

### Technical Features
- 🔒 **JWT Authentication**: Secure token-based auth
- 🌐 **CORS Support**: Cross-origin resource sharing
- 📝 **Auto Documentation**: OpenAPI/Swagger integration
- 🧪 **Testing Suite**: Comprehensive test coverage
- 🐳 **Docker Ready**: Containerization support
- ☁️ **Cloud Deployment**: Google Cloud Run ready

## 🛠️ Tech Stack

### Core Framework
- **FastAPI**: Modern, fast web framework for building APIs
- **Python 3.8+**: Programming language
- **Pydantic**: Data validation using Python type annotations
- **SQLAlchemy**: SQL toolkit and ORM

### Database
- **SQLite**: Development database (local)
- **PostgreSQL**: Production database (Supabase)
- **Alembic**: Database migration tool

### Email & Communications
- **SendGrid**: Email delivery service
- **SMTP Integration**: Email notifications system

### Authentication & Security
- **JWT**: JSON Web Tokens for authentication
- **BCrypt**: Password hashing
- **CORS**: Cross-Origin Resource Sharing

### Development Tools
- **Uvicorn**: ASGI server
- **Pytest**: Testing framework
- **Black**: Code formatting
- **isort**: Import sorting

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/eworkforce/malabroeshop_backend.git
   cd malabroeshop_backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   python -c "from app.db.init_db import init_db; init_db()"
   ```

6. **Run the application**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Access the API**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root with the following configuration:

```bash
# -----------------------------------------------------------------------------
# DATABASE CONFIGURATION
# -----------------------------------------------------------------------------
DATABASE_URL=sqlite:///./malabro_eshop.db

# For production (PostgreSQL/Supabase)
# DATABASE_URL=postgresql://username:password@host:port/database

# -----------------------------------------------------------------------------
# JWT AUTHENTICATION
# -----------------------------------------------------------------------------
SECRET_KEY=your-very-secret-key-for-jwt-signing
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=3600

# -----------------------------------------------------------------------------
# SENDGRID EMAIL CONFIGURATION
# -----------------------------------------------------------------------------
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your-sendgrid-api-key
SENDGRID_FROM_EMAIL=your-verified-sender-email
ADMIN_EMAIL=admin-email-for-notifications

# -----------------------------------------------------------------------------
# CORS SETTINGS
# -----------------------------------------------------------------------------
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# -----------------------------------------------------------------------------
# GROQ AI CONFIGURATION (Optional)
# -----------------------------------------------------------------------------
GROQ_API_KEY=your-groq-api-key
```

### SendGrid Setup

1. **Create SendGrid Account**
   - Visit [SendGrid](https://sendgrid.com/)
   - Sign up for a free account (100 emails/day)

2. **Generate API Key**
   - Go to Settings → API Keys
   - Create new API key with "Mail Send" permissions
   - Copy the API key to `SMTP_PASSWORD` in `.env`

3. **Verify Sender Email**
   - Go to Settings → Sender Authentication
   - Verify your sender email address
   - Use verified email in `SENDGRID_FROM_EMAIL`

4. **Test Email Configuration**
   ```bash
   python test_sendgrid_direct.py
   ```

## 📚 API Documentation

### API Endpoints Overview

| Category | Endpoint | Method | Description |
|----------|----------|--------|-------------|
| **Authentication** | `/api/v1/auth/login` | POST | User login |
| **Authentication** | `/api/v1/auth/register` | POST | User registration |
| **Products** | `/api/v1/products/` | GET | List products |
| **Products** | `/api/v1/products/` | POST | Create product (Admin) |
| **Products** | `/api/v1/products/{id}` | GET | Get product details |
| **Products** | `/api/v1/products/{id}` | PUT | Update product (Admin) |
| **Products** | `/api/v1/products/{id}` | DELETE | Delete product (Admin) |
| **Orders** | `/api/v1/orders/` | POST | Create order |
| **Orders** | `/api/v1/orders/{id}` | GET | Get order details |
| **Orders** | `/api/v1/orders/` | GET | List user orders |
| **Admin** | `/api/v1/admin/orders/` | GET | List all orders (Admin) |
| **Admin** | `/api/v1/admin/orders/{id}/status` | PUT | Update order status |
| **Notifications** | `/api/v1/notifications/test-email` | POST | Test email system |

### Authentication Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Database
    
    Client->>API: POST /auth/login {email, password}
    API->>Database: Verify credentials
    Database->>API: User data
    API->>Client: JWT token
    
    Client->>API: GET /products (Authorization: Bearer token)
    API->>API: Validate JWT
    API->>Client: Protected resource
```

### Sample API Calls

#### 1. User Registration
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com",
    "password": "securepassword",
    "full_name": "John Doe"
  }'
```

#### 2. Create Order
```bash
curl -X POST "http://localhost:8000/api/v1/orders/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "customer_name": "John Doe",
    "customer_email": "customer@example.com",
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

## 🗄️ Database

### Database Schema

The application uses SQLAlchemy ORM with the following main models:

#### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    full_name VARCHAR,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP
);
```

#### Products Table
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name VARCHAR NOT NULL,
    description TEXT,
    price DECIMAL NOT NULL,
    category_id INTEGER,
    unit_of_measure_id INTEGER,
    stock_quantity INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    image_url VARCHAR,
    created_at TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (unit_of_measure_id) REFERENCES units_of_measure(id)
);
```

#### Orders Table
```sql
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    order_reference VARCHAR UNIQUE,
    customer_name VARCHAR NOT NULL,
    customer_email VARCHAR NOT NULL,
    customer_phone VARCHAR,
    shipping_address TEXT,
    shipping_city VARCHAR,
    total_amount DECIMAL NOT NULL,
    status VARCHAR DEFAULT 'pending',
    created_at TIMESTAMP,
    user_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Downgrade migration
alembic downgrade -1
```

### Sample Data

The application includes sample data for development:

```bash
python -c "
from app.db.init_db import init_db
init_db()
print('Database initialized with sample data!')
"
```

## 📧 Email Notifications

### Email Types

The system sends the following automated emails:

1. **Order Confirmation** (Customer)
   - Sent when order is created
   - Contains order details and payment instructions
   - Wave payment QR code included

2. **Admin Order Alert** (Admin)
   - Sent to admin when new order is placed
   - Contains complete order information
   - Customer contact details included

3. **Payment Notifications**
   - Wave payment process updates
   - Payment confirmation alerts

### Email Templates

All emails use branded HTML templates with MALABRO styling:

```python
# Test email system
curl -X POST "http://localhost:8000/api/v1/notifications/test-email"
```

### Customizing Email Templates

Email templates are located in the notification endpoints. To customize:

1. Edit templates in `app/api/v1/endpoints/notification.py`
2. Update HTML content with your branding
3. Test changes using the test endpoint

## 🔐 Authentication

### JWT Token System

The API uses JSON Web Tokens (JWT) for authentication:

- **Access Token**: 60 minutes expiration (configurable)
- **Secure**: HS256 algorithm with secret key
- **Stateless**: No server-side session storage

### User Roles

1. **Customer**: Can place orders, view own orders
2. **Admin**: Full access to all endpoints, user management

### Protected Endpoints

Most endpoints require authentication. Include the JWT token in the Authorization header:

```bash
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 🚀 Deployment

### Local Development

```bash
# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Deployment

#### Using Docker

1. **Build Docker image**
   ```bash
   docker build -t malabro-backend .
   ```

2. **Run container**
   ```bash
   docker run -d -p 8000:8000 --env-file .env malabro-backend
   ```

#### Google Cloud Run

1. **Build and push to Container Registry**
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/malabro-backend
   ```

2. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy malabro-backend \
     --image gcr.io/PROJECT_ID/malabro-backend \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

#### Environment Setup for Production

- Use PostgreSQL database (Supabase recommended)
- Configure SendGrid for email delivery
- Set strong SECRET_KEY
- Enable HTTPS
- Configure proper CORS origins

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_orders.py

# Run with verbose output
pytest -v
```

### Test Categories

1. **Unit Tests**: Individual function testing
2. **Integration Tests**: API endpoint testing
3. **Database Tests**: CRUD operation testing
4. **Email Tests**: Notification system testing

### Test Database

Tests use a separate SQLite database that's created and destroyed for each test session.

## 🤝 Contributing

### Development Setup

1. **Fork the repository**
2. **Create feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make changes and test**
4. **Submit pull request**

### Code Standards

- **Black**: Code formatting
- **isort**: Import sorting
- **Pytest**: Testing
- **Type hints**: Use Python type annotations
- **Docstrings**: Document functions and classes

### Pre-commit Setup

```bash
# Install pre-commit hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## 📊 API Performance

### Response Times (Local Development)
- **Product List**: ~50ms
- **Order Creation**: ~120ms
- **User Authentication**: ~80ms
- **Email Notifications**: ~200ms (background)

### Rate Limiting

Currently no rate limiting is implemented. For production deployment, consider:
- API Gateway rate limiting
- Application-level rate limiting with Redis
- IP-based request throttling

## 🔍 Monitoring & Logging

### Logging Configuration

The application uses Python's built-in logging:

```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

### Health Check Endpoint

```bash
# Check API health
curl http://localhost:8000/health
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

- **Backend Development**: MALABRO Development Team
- **Email Integration**: SendGrid Integration
- **Payment System**: Wave Payment Integration

## 📞 Support

For support and questions:
- **Email**: support@malabro.com
- **Documentation**: [API Docs](http://localhost:8000/docs)
- **Issues**: [GitHub Issues](https://github.com/eworkforce/malabroeshop_backend/issues)

---

<div align="center">
  <p><strong>Built with ❤️ for fresh produce delivery in Africa</strong></p>
  <p>🥬 MALABRO - Fraîcheur et qualité à votre porte</p>
</div>