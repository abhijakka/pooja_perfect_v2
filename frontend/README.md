# PoojaPoint

PoojaPoint is an e-commerce platform for pooja essentials, subscriptions, order tracking, customer accounts, and store administration.

## Stack

### Frontend

- Next.js 16
- React 19
- TypeScript
- Tailwind CSS 4
- SWR for client-side data fetching and revalidation
- `lru-cache` for lightweight in-memory server caching

### Planned backend and infrastructure

- FastAPI backend
- PostgreSQL database
- Redis for caching and job queues
- ARQ for asynchronous jobs
- FastAPI WebSockets for real-time chat and notifications
- Payment gateway integration
- Cloudinary or object storage for media
- CDN, Nginx, Docker, and VPS/cPanel deployment options

The current repository contains the Next.js frontend scaffold. Backend services and infrastructure should be added as separate top-level areas when implementation begins.

## Getting Started

Requirements:

- Node.js 20 or newer
- npm

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

Create a production build:

```bash
## License

This project is private and not currently published under an open-source license.

### Storefront

- `/` home
- `/products` product listing
- `/products/[slug]` product detail
- `/categories/[slug]` category listing
- `/subscriptions` subscriptions
- `/cart` cart
- `/checkout` checkout
- `/wishlist` wishlist
- `/search` product search
- `/chat` customer chat
- `/order/confirmation` order confirmation
- `/order/track` order tracking
- `/order/invoice` invoice

### Authentication

- `/login`
- `/signup`
- `/otp`
- `/two-factor`

### Customer account

- `/my-account`
- `/my-orders`
- `/my-orders/[orderId]`
- `/addresses`
- `/security`
- `/notifications`

### Administration

- `/admin`
- `/admin/products`
- `/admin/orders`
- `/admin/categories`
- `/admin/coupons`
- `/admin/customers`
- `/admin/wishlist`
- `/admin/chat`
- `/admin/analytics`
- `/admin/reports`
- `/admin/ip-address`
- `/admin/settings`

## Development Notes

Route groups such as `(public)`, `(auth)`, and `(account)` organize pages without changing their URLs. The folders under `components/`, `services/`, and `lib/` provide the planned ownership boundaries for future implementation.

The current pages and feature modules contain scaffold content. Connect them to the FastAPI API, authentication, PostgreSQL data, Redis cache, and payment provider as those backend services are implemented.

## License

This project is private and not currently published under an open-source license.

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.
