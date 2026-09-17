# Public Storefront Routes

This folder contains customer-facing shopping routes. `(public)` is a Next.js route group, so it organizes files without changing their URLs.

## Files

```text
(public)/
├── page.tsx                   Home
├── products/page.tsx          Product listing
├── products/[slug]/           Product detail
├── categories/[slug]/         Category listing
├── subscriptions/page.tsx     Subscription plans
├── cart/page.tsx              Shopping cart
├── checkout/page.tsx          Checkout
├── wishlist/page.tsx          Wishlist
├── chat/page.tsx              Customer chat
├── search/page.tsx            Product search
├── order/
│   ├── confirmation/page.tsx  Order confirmation
│   ├── track/page.tsx         Delivery tracking
│   └── invoice/page.tsx       Invoice
└── README.md                  This documentation
```

## Shopping Flow

```text
/ or /search
    -> browse products or categories
    -> /products/[slug]
    -> add item to cart or wishlist
    -> /cart
    -> /checkout
    -> choose address, delivery, coupon, and payment
    -> payment gateway / cash-on-delivery confirmation
    -> /order/confirmation
    -> /order/track or /order/invoice
```

## Routes

| Route | Responsibility |
| --- | --- |
| `/` | Store introduction and primary navigation |
| `/products` | Browse the product catalog |
| `/products/[slug]` | View product details and add to cart |
| `/categories/[slug]` | Browse products in one category |
| `/search` | Search the product catalog |
| `/subscriptions` | Configure recurring product deliveries |
| `/cart` | Review items, quantities, and totals |
| `/checkout` | Collect delivery, coupon, payment, and order information |
| `/wishlist` | View saved products |
| `/chat` | Contact store support |
| `/order/confirmation` | Show successful order information |
| `/order/track` | Show fulfillment and delivery status |
| `/order/invoice` | Show or download invoice details |

## Data Flow

- Product and category data comes from the FastAPI public API.
- Product listings can use Next.js server caching and `lib/cache/` tags.
- Client-side search and interactive data can use SWR.
- Cart and wishlist state can be persisted through `services/storage/` for guests and synchronized with the account after sign-in.
- Checkout creates an order only after server-side price, stock, coupon, and payment verification.
- Payment webhooks, not the browser redirect alone, are the source of truth for paid status.

## Component Ownership

- Product UI belongs under `components/product/`.
- Cart UI belongs under `components/cart/`.
- Checkout UI belongs under `components/checkout/`.
- Subscription UI belongs under `components/subscription/`.
- Orders and invoices belong under `components/orders/` and `components/invoice/`.
- Chat UI belongs under `components/chat/`.
- Shared controls belong under `components/shared/`.

## Guest and Authenticated Customers

Guests may browse, search, and maintain a local cart. Account-only actions such as order history and saved addresses require authentication. At checkout, the backend must recalculate totals and validate inventory instead of trusting values sent by the browser.
