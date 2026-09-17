# Account Routes

This folder contains authenticated customer account pages. `(account)` is a Next.js route group, so its name does not appear in the URL.

## Files

```text
(account)/
├── my-account/page.tsx        Personal account details
├── my-orders/page.tsx         Order history
├── my-orders/[orderId]/       Individual order details
├── addresses/page.tsx         Saved delivery addresses
├── security/page.tsx          Password and security settings
├── notifications/page.tsx     Notification preferences
└── README.md                  This documentation
```

## Route Flow

1. The customer opens an account route such as `/my-account` or `/my-orders`.
2. The route checks the authenticated customer session.
3. Unauthenticated visitors are sent to `/login`.
4. The page loads customer-specific data through `services/api/`.
5. The customer edits details, addresses, security settings, or notification preferences.
6. The API validates ownership and input before writing changes to PostgreSQL.
7. The page refreshes its cached data and displays the saved state.

## Routes

| Route | Responsibility |
| --- | --- |
| `/my-account` | View and update personal information |
| `/my-orders` | List the customer's orders and statuses |
| `/my-orders/[orderId]` | Show one order, items, totals, and delivery progress |
| `/addresses` | Add, edit, select, and remove delivery addresses |
| `/security` | Change password and manage account security |
| `/notifications` | Configure email, order, delivery, and chat notifications |

## Order Flow

```text
Customer
    -> /my-orders
    -> selects an order
    -> /my-orders/[orderId]
    -> views status and items
    -> /order/track or /order/invoice
```

Order details must be authorized by customer ownership. The backend must never return another customer's order merely because its ID is known.

## Component and State Ownership

- Account UI belongs under `components/account/`.
- Order UI belongs under `components/orders/`.
- Authentication state belongs in `context/AuthContext/` and `hooks/useAuth.ts`.
- Order and customer contracts belong under `types/`.
- Browser-safe preferences may use `services/storage/`; private account data must come from the API.




