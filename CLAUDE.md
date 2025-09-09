# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🚀 Development Commands

### Backend (FastAPI)
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run with specific environment
DATABASE_URL="sqlite:///./malabro_eshop.db" uvicorn app.main:app --reload

# Docker build and run
docker build -t malabro-backend .
docker run -p 8000:8000 malabro-backend
```

### Frontend (Vue 3 + TypeScript)
```bash
cd ../frontend

# Install dependencies
npm install

# Development server
npm run dev

# Type checking
npm run type-check

# Build for production
npm run build

# Lint and format
npm run lint
npm run format
```

### Database Operations
```bash
# Run database migrations (if using migration scripts)
python migrate_sqlite_to_supabase.py

# Initialize database with sample data
python -c "from app.db.initial_data import init_db; init_db()"
```

## 🏗️ Architecture Overview

### Technology Stack
- **Backend**: FastAPI + SQLAlchemy + Pydantic
- **Frontend**: Vue 3 + TypeScript + Pinia + TailwindCSS + Radix Vue
- **Database**: SQLite (development) / PostgreSQL with Supabase (production)
- **Authentication**: JWT with role-based access control
- **File Storage**: Supabase Storage for product images
- **Payment**: Wave QR code integration

### Project Structure
```
MALABRO_eSHOP/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/v1/            # API routes and endpoints
│   │   │   └── endpoints/     # Individual endpoint modules
│   │   ├── core/              # Core config, auth, database
│   │   ├── crud/              # Database CRUD operations
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   └── utils/             # Utility functions
│   ├── uploads/               # Local file uploads (dev only)
│   └── requirements.txt       # Python dependencies
└── frontend/                  # Vue.js frontend
    ├── src/
    │   ├── components/        # Reusable Vue components
    │   ├── views/             # Page-level components
    │   ├── stores/            # Pinia state management
    │   ├── services/          # API service calls
    │   └── router/            # Vue Router configuration
    └── package.json           # Node.js dependencies
```

### Database Design
- **Dual Database Support**: Environment-based switching between SQLite (dev) and PostgreSQL (prod)
- **Models**: User, Product, Order, Category, UnitOfMeasure, InventoryLedger
- **Authentication**: Role-based with admin/user roles
- **Relationships**: Proper foreign key relationships with lazy loading

### API Architecture
- **RESTful Design**: `/api/v1/` versioned endpoints
- **Authentication Flow**: JWT tokens with refresh mechanism
- **Admin Protection**: Role-based middleware for admin endpoints
- **CORS Configuration**: Environment-specific CORS origins

### State Management (Frontend)
- **Pinia Stores**: Modular state management for auth, cart, products
- **Persistent Auth**: Token storage in localStorage with auto-refresh
- **Reactive UI**: Vue 3 Composition API for optimal performance

## 🔧 Configuration

### Environment Variables
Key environment variables (see `.env.example`):
```bash
DATABASE_URL=sqlite:///./malabro_eshop.db
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SECRET_KEY=your-jwt-secret-key
CORS_ORIGINS=http://localhost:5173,http://localhost:5174
```

### Database Configuration
The app automatically switches between SQLite and PostgreSQL based on environment:
- **Development**: SQLite with file-based storage
- **Production**: Supabase PostgreSQL with connection pooling
- **Migration**: Scripts available for SQLite → Supabase migration

## 📊 API Endpoints Structure

### Public Endpoints
- `GET /api/v1/products` - Product listing and filtering
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login-json` - User login

### Protected User Endpoints
- `GET /api/v1/orders` - User's order history
- `POST /api/v1/orders` - Create new order
- `GET /api/v1/auth/me` - Current user profile

### Admin-Only Endpoints
- `GET /api/v1/admin/dashboard` - Dashboard metrics
- `POST /api/v1/admin/products` - Create/update products
- `PUT /api/v1/admin/orders/{id}` - Manage order status
- `DELETE /api/v1/admin/users/{id}` - User management

## 🔐 Security Implementation

### Authentication Flow
1. User login → JWT access token generated
2. Token stored in frontend localStorage
3. Token included in Authorization header for API requests
4. Server validates JWT and extracts user/role information

### Role-Based Access
- **User Role**: Can view products, create orders, manage own profile
- **Admin Role**: Full system access, user management, order processing

### Security Features
- Password hashing with bcrypt
- JWT token authentication with expiration
- Input validation using Pydantic schemas
- SQL injection prevention via SQLAlchemy ORM
- CORS protection with environment-specific origins

## 🗃️ Database Patterns

### CRUD Operations
Each model has corresponding CRUD operations in `app/crud/`:
- Base CRUD class with common operations (get, create, update, delete)
- Specialized CRUD classes for complex queries
- Async-ready database sessions

### Common Query Patterns
```python
# Get with relationship loading
product = db.query(Product).options(joinedload(Product.category)).first()

# Filtering with multiple conditions
products = db.query(Product).filter(Product.is_active == True).filter(Product.stock_quantity > 0)

# Pagination
products = db.query(Product).offset(skip).limit(limit)
```

### Migration Strategy
- Development: SQLAlchemy creates tables automatically
- Production: Use provided migration scripts for Supabase
- Always backup before migrations

## 🎨 Frontend Architecture

### Component Structure
- **Base Components**: Reusable UI components (buttons, cards, modals)
- **Feature Components**: Business logic components (product cards, cart items)
- **Page Components**: Full page views in `src/views/`
- **Admin Components**: Admin-specific components in `src/components/admin/`

### State Management Pattern
```javascript
// Store structure example
const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isLoggedIn = computed(() => !!user.value)
  
  const login = async (credentials) => {
    // API call and state update
  }
})
```

### API Service Pattern
```javascript
// Service layer for API calls
export class ProductService {
  static async getProducts(params = {}) {
    return api.get('/products', { params })
  }
}
```

## 🚨 Important Development Notes

### Database Considerations
- **Environment Detection**: App automatically uses SQLite in development, PostgreSQL in production
- **Initial Data**: `init_db()` creates admin user and sample data on startup
- **File Storage**: Images stored locally in development, Supabase Storage in production

### Development Workflow
1. Backend runs on port 8000 with auto-reload
2. Frontend runs on port 5173 with HMR (Hot Module Replacement)
3. CORS configured to allow frontend-backend communication
4. Database tables created automatically on first run

### Common Development Tasks
- **Add New Model**: Create model → schema → CRUD → endpoints
- **Add API Endpoint**: Define in `app/api/v1/endpoints/` → register in `api.py`
- **Add Frontend Route**: Define in `src/router/index.ts` → create view component
- **Admin Features**: Protect endpoints with admin role check

### Performance Considerations
- Use `joinedload()` or `selectinload()` for relationship queries to avoid N+1 problems
- Implement pagination for large datasets
- Consider caching for frequently accessed data
- Optimize images before upload to reduce storage costs

### Testing Considerations
- No current test framework configured
- Recommended: pytest for backend, Vitest for frontend
- Consider adding API testing with actual database transactions
- E2E testing recommended for critical user flows