# MALABRO eShop Backend

FastAPI backend for the MALABRO e-commerce platform with AI assistant integration.

## Features

- **FastAPI** REST API with automatic OpenAPI documentation
- **SQLAlchemy** ORM with SQLite database
- **JWT Authentication** for secure user management
- **Email Notifications** via SendGrid SMTP
- **AI Assistant** powered by Groq with MCP tools
- **Payment Integration** supporting Wave and Orange Money
- **File Upload** system for product images
- **Inventory Management** with ledger tracking
- **Admin Dashboard** endpoints

## Quick Start

### Prerequisites

- Python 3.8+
- pip or pipenv

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/eworkforce/malabro_eshop_backend.git
cd malabro_eshop_backend
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

4. **Environment Configuration**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Initialize database**
```bash
python -c "from app.db.init_db import init_db; init_db()"
```

6. **Start the server**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Environment Variables

Create a `.env` file with the following variables:

```env
# Database
DATABASE_URL=sqlite:///./malabro.db

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Admin Configuration
ADMIN_EMAIL=admin@malabro.com
ADMIN_PASSWORD=admin123

# Email Configuration (SendGrid)
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your-sendgrid-api-key
SENDGRID_FROM_EMAIL=noreply@malabro.com

# AI Configuration (Groq)
GROQ_API_KEY=your-groq-api-key

# File Upload
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760
```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Key Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration

### Products
- `GET /api/v1/products/` - List products
- `POST /api/v1/products/` - Create product (admin)
- `GET /api/v1/products/{id}` - Get product details

### Orders
- `POST /api/v1/orders/` - Create order
- `GET /api/v1/orders/` - List user orders

### Admin
- `GET /api/v1/admin/orders` - List all orders
- `PUT /api/v1/admin/orders/{id}/status` - Update order status

### AI Assistant
- `POST /api/v1/ai-tools/chat` - Chat with AI assistant
- `GET /api/v1/ai-tools/inventory/summary` - Get inventory summary

### Notifications
- `POST /api/v1/notifications/payment-started` - Send payment notifications

## Payment Integration

### Wave Payment
- Integrated with Wave payment gateway
- Automatic order creation and email notifications

### Orange Money
- Support for Orange Money mobile payments
- QR code generation for payment processing

## AI Assistant Features

The AI assistant uses Groq LLM with MCP (Model Context Protocol) tools:

- **Inventory Management**: Check stock levels, low stock alerts
- **Order Tracking**: Recent orders, payment status
- **Business Analytics**: Sales summaries, performance metrics
- **Product Search**: Find products by name or category

## File Structure

```
app/
├── api/v1/endpoints/     # API route handlers
├── core/                 # Core configuration
├── crud/                 # Database operations
├── db/                   # Database setup
├── models/               # SQLAlchemy models
├── schemas/              # Pydantic schemas
├── services/             # Business logic services
└── utils/                # Utility functions
```

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black app/
isort app/
```

### Database Migrations
```bash
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## Deployment

### Docker
```bash
docker build -t malabro-backend .
docker run -p 8000:8000 malabro-backend
```

### Production Considerations
- Use PostgreSQL instead of SQLite
- Configure proper CORS settings
- Set up SSL/TLS certificates
- Use environment-specific configuration
- Implement proper logging and monitoring

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is proprietary software owned by eWorkforce.

## Support

For support and questions, contact: sergeziehi@eworkforce.africa
