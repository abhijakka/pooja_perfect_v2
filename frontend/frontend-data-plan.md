# Frontend Data Plan

Status markers are updated only after implementation and executable validation.

## Audit Inventory

### Backend-connected or partially connected

- Public product listing: `app/(public)/products/ProductsPage.tsx` calls `services/api/products.api.ts`, but starts with static catalog data, has no loading state, and ignores successful empty responses.
- Public product detail: `app/(public)/products/[slug]/ProductDetailPage.tsx` and its route require verification of API/error/empty handling.
- Admin products: `app/admin/components/AdminProductsPage.tsx` calls `adminApi.listProducts`, but starts with static products and local-only mutations.
- API layer: `services/api/client.ts` provides REST and public/admin GraphQL clients. Domain service modules exist for auth, products, categories, cart, checkout, orders, payments, wishlist, subscriptions, chat, coupons, and admin.
- Redux store: cart, wishlist, chat, auth, checkout, and subscription state. Local storage is appropriate for wishlist persistence and must not replace authenticated backend state.

### Static-only or mixed business data requiring classification

- `app/(public)/storefront-data.ts`: product catalog, pay-as-you-go products, subscription plans, delivery options, and category display data. Product and category records are business data; delivery options and plan presentation remain static only where no backend contract exists.
- `app/admin/components/dashboard-data.ts`: dashboard KPIs, sales, categories, orders, and stock alerts are business data and must be fallback-only once API state exists.
- Admin component pages under `app/admin/components/`: inspect each for hardcoded products, orders, customers, categories, coupons, reviews, logs, analytics, reports, settings, wishlist, chat, and hero data.
- Public/account/auth pages: inspect forms and account/order/address/notification pages for hardcoded user or order data. Static labels, navigation, validation messages, and fixed UI choices are legitimate frontend configuration.

### Routes to audit

- Public: home, products, product detail, categories, search, subscriptions, cart, checkout, wishlist, chat, order confirmation, tracking, invoice.
- Auth: login, signup, OTP, two-factor, forgot password.
- Account: my account, orders, order detail, addresses, security, notifications.
- Admin: dashboard, products, orders, order detail, categories, coupons, customers, wishlist, chat, analytics, reports, IP address, logs, reviews, settings, hero.

## Existing API Endpoints / Operations

- Public GraphQL: `/graphql` through `graphqlClient` for products and categories; other domain services need call-site verification.
- Admin GraphQL: `/admin/graphql` through `adminGraphqlClient` for dashboard, products, categories, orders, customers, coupons, reviews, and mutations.
- REST client: `apiClient` for REST services such as auth/payment/media where applicable.
- Auth credentials: `poojapoint-access-token` local-storage key is currently read by admin products; standardize token access without duplicating clients.
- Environment: `config/environment.ts` owns the API URL; services must not hardcode hosts.

## Required Data State Contract

Every dynamic request must distinguish:

- `loading`: render the existing loader/skeleton; never fallback.
- `success`: render exactly the backend payload, including an empty array/object.
- `error`: render fallback data only where offline/demo behavior is intentional, with a non-sensitive connection indicator.
- `unauthorized` / `forbidden`: preserve existing auth/permission handling; do not substitute fake authenticated data.

A successful empty response is an empty state, never a fallback trigger. Backend data must never be concatenated with fallback data.

## Fallback Policy

- Keep existing static catalog/dashboard data only in clearly named fallback modules until each backend contract is available.
- Fallbacks are selected only after a request has rejected or the backend is explicitly unavailable.
- Remove hardcoded business data from successful render paths.
- Keep static UI configuration: navigation, icons, labels, validation rules, legal text, fixed delivery choices, and visual constants.

## Files To Modify

- First slice: `app/(public)/products/ProductsPage.tsx`, `app/admin/components/AdminProductsPage.tsx`.
- Shared request-state/token utility only if existing service patterns cannot express the contract without duplication.
- Subsequent slices: public detail/category/search/home, account/order/cart/wishlist/notifications, admin dashboard and CRUD pages, and their focused tests.
- Tests for each changed request path and state transition.

## Files To Create

- This plan: `frontend-data-plan.md`.
- Only create a shared data-state abstraction or fallback directory if an existing local pattern cannot be reused and the first focused slice proves the need.
- Completion record: `plan-completed.md` after implementation and testing.

## Implementation Sequence

1. [COMPLETED] Audit the repository notes, frontend README, API client, product/category/admin services, and representative public/admin pages.
2. [COMPLETED] Record the audit inventory and backend-first state contract in this plan.
3. [COMPLETED] Fix public product listing loading, success, empty, error/fallback behavior without mixing datasets.
4. [NOT COMPLETED] Fix admin product listing and CRUD mutations to use backend responses; read fallback and create/update are implemented, but embedded featured/delete handlers remain local-only.
5. [NOT COMPLETED] Apply the same state contract to every dynamic public/account/admin page.
6. [NOT COMPLETED] Audit and classify every remaining static business-data source and move fallback data out of successful render paths.
7. [NOT COMPLETED] Add focused loading/success-empty/error/auth/permission and mutation tests for each updated slice.
8. [NOT COMPLETED] Run frontend Jest, TypeScript, lint, and a final static/API search; record exact results in `plan-completed.md`.

## Testing Matrix

- API loading: loader/skeleton, no fallback content.
- API success with rows: backend rows only; differing fallback rows absent.
- API success empty: explicit empty state.
- API rejection/network/5xx: fallback only where policy permits, with safe status text.
- 401: existing auth flow.
- 403: existing permission flow.
- Successful mutation: render returned backend entity or refetched backend list.
- Failed mutation: no local success fiction and no locally generated persisted entity.
