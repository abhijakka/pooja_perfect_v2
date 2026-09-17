# Admin Routes

This folder contains the PoojaPoint store administration area. Every route is available under `/admin` and is wrapped by `layout.tsx`, which provides the admin shell and navigation back to the storefront.

## Files

```text
admin/
├── layout.tsx                 Shared admin layout
├── page.tsx                   Dashboard
├── analytics/page.tsx         Performance analytics
├── categories/page.tsx        Category management
├── chat/page.tsx              Customer conversations
├── coupons/page.tsx           Coupon management
├── customers/page.tsx         Customer management
├── hero/page.tsx              Hero section management
├── ip-address/page.tsx        Access/IP activity
├── orders/page.tsx            Order management
├── products/page.tsx          Product management
├── reviews/page.tsx           Product review moderation
├── reports/page.tsx           Reports
├── settings/page.tsx          Store settings
├── wishlist/page.tsx          Wishlist overview
└── README.md                 This documentation
```

## Route Flow

1. An administrator opens `/admin`.
2. `layout.tsx` renders the shared admin navigation and an outlet for the selected page.
3. `page.tsx` displays dashboard metrics and recent activity.
4. The administrator selects a section from the navigation.
5. The section page loads data through `services/api/admin.api.ts` or its feature-specific API module.
6. Mutations are validated, authorized, persisted by the FastAPI backend, and reflected in the UI.

## Sections

| Route | Responsibility |
| --- | --- |
| `/admin` | Store overview, sales summary, and recent orders |
| `/admin/analytics` | Revenue, order, and customer trends |
| `/admin/categories` | Create, edit, organize, and remove categories |
| `/admin/chat` | Reply to customer conversations in real time |
| `/admin/coupons` | Create coupons and manage their status |
| `/admin/customers` | Search customers and inspect account activity |
| `/admin/hero` | Edit the storefront hero banner and promotional slides |
| `/admin/ip-address` | Review access and security activity |
| `/admin/orders` | Review orders and update fulfillment status |
| `/admin/products` | Create, edit, publish, and manage products |
| `/admin/reviews` | Moderate customer product reviews and ratings |
| `/admin/reports` | Filter and export operational reports |
| `/admin/settings` | Configure store, payment, delivery, notification, and security settings |
| `/admin/wishlist` | Review customer wishlist activity |

## Data and Security Flow

```text
Admin browser
    -> Next.js admin route
    -> authenticated admin session
    -> FastAPI admin endpoint
    -> authorization check
    -> PostgreSQL transaction
    -> Redis cache invalidation / ARQ job
    -> updated admin response
```

Admin pages must be protected by server-side authorization. Hiding links is not security. Each admin API endpoint must verify the authenticated user has the required role or permission, validate input, record important changes, and avoid exposing private customer data unnecessarily.

## Planned Detail Routes

The current scaffold has list pages only. Detail and creation routes can be added as needed:

- `/admin/orders/[orderId]`
- `/admin/products/new`
- `/admin/products/[productId]`
- `/admin/categories/[categoryId]`
- `/admin/coupons/[couponId]`
- `/admin/customers/[customerId]`

## Component Ownership

Admin UI components belong under `components/admin/`. Shared controls belong under `components/shared/`. API calls belong under `services/api/`; data models belong under `types/`; charts, formatting, and cache helpers belong under `lib/`.
