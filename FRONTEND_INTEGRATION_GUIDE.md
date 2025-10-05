# 📱 Frontend Integration Guide - Delivery Preparation Feature

## 🎯 Overview

The backend team has completed a new API endpoint for delivery preparation. This feature aggregates all paid orders by product to help admins prepare deliveries efficiently.

**Target Page:** `https://malabroeshop.web.app/admin/orders`

---

## 🔌 API Endpoint

### Endpoint Details

**URL:** `GET /api/v1/admin/orders/preparation-summary`

**Authentication:** Bearer Token (Admin only)

**Base URL:** Your backend API base URL

### Query Parameters

| Parameter | Type | Required | Format | Description |
|-----------|------|----------|--------|-------------|
| `date_from` | string | No | YYYY-MM-DD | Filter orders from this date |
| `date_to` | string | No | YYYY-MM-DD | Filter orders until this date |

### Example Requests

```javascript
// Get all paid orders
GET /api/v1/admin/orders/preparation-summary

// Filter by date range
GET /api/v1/admin/orders/preparation-summary?date_from=2025-10-01&date_to=2025-10-31

// Get today's orders only
const today = new Date().toISOString().split('T')[0];
GET /api/v1/admin/orders/preparation-summary?date_from=${today}&date_to=${today}
```

---

## 📦 Response Format

### Success Response (200 OK)

```json
{
  "summary": {
    "total_paid_orders": 11,
    "total_unique_products": 4,
    "total_revenue": 2970.0,
    "last_updated": "2025-10-05T19:52:32.322501"
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
        },
        {
          "order_id": 13,
          "order_reference": "MALABRO-JWJIMB",
          "customer_name": "Serge",
          "quantity": 4,
          "created_at": "2025-09-09T15:48:11"
        }
        // ... more orders
      ]
    },
    {
      "product_id": 3,
      "product_name": "Salades",
      "total_quantity": 15,
      "unit": "kg",
      "order_count": 6,
      "unique_customers": 2,
      "orders": [...]
    }
    // ... more products
  ],
  "date_range": {
    "date_from": "2025-10-01",
    "date_to": "2025-10-31"
  }
}
```

### Empty Response (No Paid Orders)

```json
{
  "summary": {
    "total_paid_orders": 0,
    "total_unique_products": 0,
    "total_revenue": 0,
    "last_updated": "2025-10-05T20:00:00"
  },
  "products": [],
  "date_range": {
    "date_from": null,
    "date_to": null
  }
}
```

### Error Response (401 Unauthorized)

```json
{
  "detail": "Not authenticated"
}
```

### Error Response (403 Forbidden)

```json
{
  "detail": "Not enough permissions"
}
```

---

## 🎨 Recommended UI Implementation

### Layout: Hybrid Approach (Summary Card + Modal)

#### 1. Summary Card (Always Visible)

Place this at the **top of the admin orders page**, above the orders table:

```
┌─────────────────────────────────────────────────────────────────┐
│  📦 PRÉPARATION LIVRAISON                                       │
│  ─────────────────────────────────────────────────────────────  │
│  🔵 11 commandes payées  │  📦 4 produits à préparer           │
│  💰 2,970 FCFA de revenus                                       │
│                                                                  │
│  [📋 Voir Détails Complets]  [🔄 Actualiser]  [📥 Exporter]   │
└─────────────────────────────────────────────────────────────────┘
```

**Card Content:**
- Total paid orders count
- Total unique products count
- Total revenue
- Buttons: "View Details", "Refresh", "Export" (optional)

#### 2. Detailed Modal (On Button Click)

When user clicks "Voir Détails Complets", open a modal:

```
╔═══════════════════════════════════════════════════════════════╗
║  📦 Récapitulatif de Préparation - Commandes Payées          ║
║  ───────────────────────────────────────────────────────────  ║
║  Période: [05/10/2025] - [Aujourd'hui] [Filtrer]             ║
╠═══════════════════════════════════════════════════════════════╣
║                                                                ║
║  🥬 Tomates                              15 kg  │  6 cmd      ║
║  ├─ MALABRO-SLISAE: Admin (1 kg)                             ║
║  ├─ MALABRO-JWJIMB: Serge (4 kg)                             ║
║  ├─ MALABRO-FI46ON: Serge (4 kg)                             ║
║  └─ ... 3 autres commandes           [Voir tout]             ║
║                                                                ║
║  🥗 Salades                              15 kg  │  6 cmd      ║
║  ├─ MALABRO-MAX4F8: Admin (1 kg)                             ║
║  └─ ... 5 autres commandes           [Voir tout]             ║
║                                                                ║
║  🍆 Aubergines                           5 kg   │  2 cmd      ║
║  🧅 Poireaux                             1 kg   │  1 cmd      ║
║                                                                ║
╠═══════════════════════════════════════════════════════════════╣
║  [📥 Télécharger CSV]  [🖨️ Imprimer]  [✖️ Fermer]          ║
╚═══════════════════════════════════════════════════════════════╝
```

**Modal Content:**
- Date range filter (with date pickers)
- Product list with expandable order details
- Export/Print buttons
- Close button

---

## 💻 Sample Code Implementation

### React/TypeScript Example

```typescript
// types.ts
interface OrderItemSummary {
  order_id: number;
  order_reference: string;
  customer_name: string;
  quantity: number;
  created_at: string;
}

interface ProductPreparationSummary {
  product_id: number;
  product_name: string;
  total_quantity: number;
  unit: string | null;
  order_count: number;
  unique_customers: number;
  orders: OrderItemSummary[];
}

interface PreparationSummaryResponse {
  summary: {
    total_paid_orders: number;
    total_unique_products: number;
    total_revenue: number;
    last_updated: string;
  };
  products: ProductPreparationSummary[];
  date_range: {
    date_from: string | null;
    date_to: string | null;
  };
}

// api.ts
export const fetchPreparationSummary = async (
  dateFrom?: string,
  dateTo?: string
): Promise<PreparationSummaryResponse> => {
  const params = new URLSearchParams();
  if (dateFrom) params.append('date_from', dateFrom);
  if (dateTo) params.append('date_to', dateTo);
  
  const queryString = params.toString();
  const url = `/api/v1/admin/orders/preparation-summary${queryString ? `?${queryString}` : ''}`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${getAuthToken()}`,
      'Content-Type': 'application/json',
    },
  });
  
  if (!response.ok) {
    throw new Error('Failed to fetch preparation summary');
  }
  
  return response.json();
};

// DeliveryPrepCard.tsx
import React, { useState, useEffect } from 'react';

export const DeliveryPrepCard: React.FC = () => {
  const [data, setData] = useState<PreparationSummaryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const result = await fetchPreparationSummary();
      setData(result);
    } catch (error) {
      console.error('Error loading preparation summary:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading) return <div>Chargement...</div>;
  if (!data) return null;

  return (
    <>
      <div className="prep-summary-card">
        <h3>📦 PRÉPARATION LIVRAISON</h3>
        <div className="summary-stats">
          <div className="stat">
            <span className="label">Commandes payées:</span>
            <span className="value">{data.summary.total_paid_orders}</span>
          </div>
          <div className="stat">
            <span className="label">Produits à préparer:</span>
            <span className="value">{data.summary.total_unique_products}</span>
          </div>
          <div className="stat">
            <span className="label">Revenus:</span>
            <span className="value">
              {data.summary.total_revenue.toLocaleString()} FCFA
            </span>
          </div>
        </div>
        <div className="actions">
          <button onClick={() => setShowModal(true)}>
            📋 Voir Détails Complets
          </button>
          <button onClick={loadData}>
            🔄 Actualiser
          </button>
        </div>
      </div>

      {showModal && (
        <DeliveryPrepModal
          data={data}
          onClose={() => setShowModal(false)}
          onRefresh={loadData}
        />
      )}
    </>
  );
};

// DeliveryPrepModal.tsx (simplified)
export const DeliveryPrepModal: React.FC<{
  data: PreparationSummaryResponse;
  onClose: () => void;
  onRefresh: () => void;
}> = ({ data, onClose, onRefresh }) => {
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');

  const handleFilter = async () => {
    const result = await fetchPreparationSummary(dateFrom, dateTo);
    // Update parent component with new data
    onRefresh();
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <header>
          <h2>📦 Récapitulatif de Préparation</h2>
          <button onClick={onClose}>✖️</button>
        </header>

        <div className="date-filters">
          <input
            type="date"
            value={dateFrom}
            onChange={(e) => setDateFrom(e.target.value)}
            placeholder="Date début"
          />
          <input
            type="date"
            value={dateTo}
            onChange={(e) => setDateTo(e.target.value)}
            placeholder="Date fin"
          />
          <button onClick={handleFilter}>Filtrer</button>
        </div>

        <div className="products-list">
          {data.products.map((product) => (
            <div key={product.product_id} className="product-item">
              <div className="product-header">
                <span className="product-name">{product.product_name}</span>
                <span className="product-quantity">
                  {product.total_quantity} {product.unit || ''}
                </span>
                <span className="order-count">
                  {product.order_count} commande{product.order_count > 1 ? 's' : ''}
                </span>
              </div>
              
              <div className="orders-list">
                {product.orders.slice(0, 3).map((order) => (
                  <div key={order.order_id} className="order-item">
                    <span>{order.order_reference}</span>
                    <span>{order.customer_name}</span>
                    <span>{order.quantity} {product.unit || ''}</span>
                  </div>
                ))}
                {product.orders.length > 3 && (
                  <button>+ {product.orders.length - 3} autres</button>
                )}
              </div>
            </div>
          ))}
        </div>

        <footer>
          <button onClick={() => exportToCSV(data)}>📥 Télécharger CSV</button>
          <button onClick={() => window.print()}>🖨️ Imprimer</button>
        </footer>
      </div>
    </div>
  );
};
```

### Vue.js Example

```vue
<template>
  <div class="delivery-prep-card">
    <h3>📦 PRÉPARATION LIVRAISON</h3>
    
    <div v-if="loading">Chargement...</div>
    
    <div v-else-if="data" class="summary-content">
      <div class="stats">
        <div class="stat-item">
          <span class="label">Commandes payées:</span>
          <span class="value">{{ data.summary.total_paid_orders }}</span>
        </div>
        <div class="stat-item">
          <span class="label">Produits:</span>
          <span class="value">{{ data.summary.total_unique_products }}</span>
        </div>
        <div class="stat-item">
          <span class="label">Revenus:</span>
          <span class="value">{{ formatCurrency(data.summary.total_revenue) }}</span>
        </div>
      </div>
      
      <div class="actions">
        <button @click="showModal = true">📋 Voir Détails</button>
        <button @click="loadData">🔄 Actualiser</button>
      </div>
    </div>
    
    <!-- Modal Component -->
    <DeliveryPrepModal
      v-if="showModal"
      :data="data"
      @close="showModal = false"
      @refresh="loadData"
    />
  </div>
</template>

<script>
export default {
  name: 'DeliveryPrepCard',
  data() {
    return {
      data: null,
      loading: false,
      showModal: false,
    };
  },
  mounted() {
    this.loadData();
  },
  methods: {
    async loadData() {
      this.loading = true;
      try {
        const response = await fetch(
          '/api/v1/admin/orders/preparation-summary',
          {
            headers: {
              'Authorization': `Bearer ${this.$store.state.authToken}`,
            },
          }
        );
        this.data = await response.json();
      } catch (error) {
        console.error('Error:', error);
      } finally {
        this.loading = false;
      }
    },
    formatCurrency(amount) {
      return `${amount.toLocaleString()} FCFA`;
    },
  },
};
</script>
```

---

## 🎯 Integration Checklist

### Required Steps

- [ ] **Add API endpoint URL to your config**
  - Base URL + `/api/v1/admin/orders/preparation-summary`

- [ ] **Implement authentication**
  - Include Bearer token in Authorization header
  - Ensure only admin users can access

- [ ] **Create Summary Card Component**
  - Display at top of admin orders page
  - Show total paid orders, products, revenue
  - Add "View Details" button

- [ ] **Create Detailed Modal Component**
  - List all products with quantities
  - Show orders per product (expandable)
  - Include date range filter
  - Add export/print functionality (optional)

- [ ] **Handle Loading States**
  - Show loading indicator while fetching
  - Handle empty state (no paid orders)
  - Show error messages if API fails

- [ ] **Implement Date Filtering**
  - Date pickers with YYYY-MM-DD format
  - Filter button to refresh with new dates
  - Clear filter option

- [ ] **Add Refresh Functionality**
  - Manual refresh button
  - Consider auto-refresh every 5-10 minutes (optional)

- [ ] **Responsive Design**
  - Card should work on mobile/tablet
  - Modal should be scrollable
  - Consider mobile-first approach

### Optional Enhancements

- [ ] **Export to CSV**
  - Generate CSV from products data
  - Include product name, quantity, order count

- [ ] **Print View**
  - Printer-friendly format
  - Hide unnecessary UI elements

- [ ] **Caching**
  - Cache response for 5-10 minutes
  - Reduce API calls on page refresh

- [ ] **Notifications**
  - Show toast notification when data refreshes
  - Alert when new paid orders arrive

---

## 🐛 Error Handling

### Common Scenarios

1. **No Paid Orders:**
   - Display: "Aucune commande payée pour le moment"
   - Hide or disable "View Details" button

2. **API Error:**
   - Display: "Erreur lors du chargement des données"
   - Show retry button

3. **Authentication Error:**
   - Redirect to login page
   - Show: "Session expirée, veuillez vous reconnecter"

4. **Network Error:**
   - Display: "Problème de connexion, veuillez réessayer"
   - Keep previous data if available

---

## 📊 Testing Recommendations

### Test Cases

1. **Normal Flow:**
   - Load page → see summary card with data
   - Click "View Details" → modal opens
   - Apply date filter → data updates

2. **Empty State:**
   - Test with no paid orders
   - Verify empty message displays

3. **Date Filtering:**
   - Test with valid date range
   - Test with no results in date range
   - Test with invalid dates

4. **Performance:**
   - Test with many products (10+)
   - Test with many orders per product (20+)
   - Verify loading states

5. **Responsive:**
   - Test on mobile (320px width)
   - Test on tablet (768px width)
   - Test on desktop (1920px width)

---

## 💡 Tips & Best Practices

1. **Caching:** Consider caching the response for 5-10 minutes to reduce API load

2. **Date Format:** Always use YYYY-MM-DD format for date parameters

3. **Error States:** Always show user-friendly error messages

4. **Loading States:** Show skeleton loaders or spinners during API calls

5. **Empty States:** Provide clear messaging when no data is available

6. **Accessibility:** Ensure buttons have proper aria-labels and keyboard navigation works

7. **Mobile First:** Design for mobile screens first, then enhance for desktop

---

## 📞 Support & Questions

**Backend Developer:** [Your Name]
**Backend Repository:** https://github.com/eworkforce/malabroeshop_backend
**Documentation:** See `warp.md` and `DELIVERY_PREP_FEATURE.md` in backend repo

For questions or issues:
- Check API docs: `http://your-backend-url/docs`
- Review complete feature docs: `DELIVERY_PREP_FEATURE.md`
- Contact backend team

---

## 🎉 Summary

**What You Need to Build:**
1. A summary card component at the top of admin orders page
2. A detailed modal that opens when clicking "View Details"
3. Date filtering functionality
4. API integration with proper auth

**What's Already Done:**
✅ Backend API endpoint is live and tested
✅ Authentication and authorization
✅ Data aggregation and sorting
✅ Date filtering logic

**Estimated Effort:** 4-6 hours for basic implementation

Good luck with the implementation! 🚀
