# Fix Plan

## A. Project Audit

### Frontend structure
- Next.js app router project with route groups under `frontend/app/`.
- Public storefront under `frontend/app/(public)` and supporting data in `frontend/app/(public)/storefront-data.ts`.
- Auth pages under `frontend/app/(auth)`.
- Customer account pages under `frontend/app/(account)`.
- Admin shell under `frontend/app/admin` with pages and `layout.tsx`.
- Shared reusable UI in `frontend/components/`, API clients in `frontend/services/api/`, and Redux store in `frontend/store/`.
- Current implementation is scaffolded and still uses static/public mock data heavily in storefront and customer account pages.

### Backend structure
- FastAPI backend under `backend/src/app` with GraphQL and REST layers.
- Public GraphQL at `/graphql` and admin GraphQL at `/admin/graphql`.
- Auth REST endpoints under `backend/src/app/api/auth.py`.
- Security helpers in `backend/src/app/core/security.py`.
- Permission enforcement in `backend/src/app/dependencies/auth.py`.
- User model in `backend/src/app/models/user.py` with `role_name` and `status`.
- Core enums in `backend/src/app/models/enums.py` with the backend source-of-truth role values: `customer` and `admin`.

### Authentication implementation
- Backend auth service exists for register/login/refresh/logout and Google OAuth.
- Login returns access and refresh tokens in JSON and also stores them as HTTP-only cookies in `backend/src/app/api/auth.py`.
- `get_current_user()` expects bearer auth from `Authorization: Bearer ...` and `get_current_active_user()` enforces active status.
- Admin access is enforced by `require_admin()` which checks `current_user.role_name == UserRole.ADMIN`.

### JWT implementation
- Access token secret: `settings.jwt_secret_key`.
- Refresh token secret: `settings.jwt_refresh_secret_key`.
- JWT lifetime is configured in `backend/src/app/config.py` (`access_token_expire_minutes` and `refresh_token_expire_days`).
- The backend is already using secure cookie-based auth semantics for token storage and should remain the authority.

### Cookie implementation
- `backend/src/app/api/auth.py::_set_auth_cookies()` sets `access_token` and `refresh_token` as HTTP-only cookies at `/`.
- Cookies are set with `httponly=True`, `samesite="lax"`, `secure=False`, and `path="/"`.
- Frontend currently stores JWTs in localStorage during login in `frontend/app/(auth)/login/page.tsx`, which conflicts with the backend cookie model.

### Session implementation
- Backend user sessions and refresh-token persistence exist in the model layer; refresh tokens are stored in hashed form.
- There is no separate global guest session architecture in the current backend or frontend, so the public guest flow must be unified around existing cart/checkout behavior rather than creating a second session system.

### User model
- `User` has `first_name`, `last_name`, `email`, `phone`, `password_hash`, `role_name`, `status`, etc.
- `role_name` is the canonical role field used by authorization logic.
- The user role requirement is explicit: only `admin` and `customer` are valid runtime roles.

### `userrole`
- The actual backend field is `role_name` in the database model and `role_name` in the user schema.
- Frontend code currently uses a generic `Customer` type and does not read the actual backend `role_name` on authenticated state restoration.

### Customer/admin authorization
- Public GraphQL API is open and customer requests may be optional auth.
- Admin GraphQL API is protected by `require_admin` in `backend/src/app/admin/context.py`.
- Current frontend does not enforce admin gating on routes or session restoration; it mostly relies on route and static UI patterns.

### Existing middleware
- FastAPI CORS is configured in `backend/src/app/main.py` with `allow_credentials=True`.
- Request context is built in admin/public GraphQL context files.

### Existing API architecture
- Frontend uses `frontend/services/api/client.ts` with `fetch` wrappers.
- `authApi` exists but is not wired to cookie-based credentialed requests.
- Admin API is structured separately and there are static mock/admin data flows in several admin pages.

### Public endpoints
- Public storefront pages and cart checkout flows are open.
- Guest access is expected to work without forced login for browsing, cart, checkout, and order creation according to the project design.

### Admin endpoints
- Admin GraphQL routes are protected and require admin auth.
- The frontend admin pages are not yet guarded by any real auth logic or role check.

### Cart flow
- Redux cart slices exist and local storage is used for persistence for wishlist; cart is not yet tied to backend session/guest session architecture.

### Checkout flow
- Frontend has checkout and cart flows but mostly rely on static projections.

### Order flow
- Backend has order-related models and schemas, but the actual public order/checkout UX is not fully connected to real auth and guest session handling.

### IP address handling
- Backend model layer includes `ip_activity` and IP policy-related enums/models under `backend/src/app/models/`.
- No dedicated frontend guest session/IP plumbing is currently implemented at the app level.

### Existing static/mock data
- `frontend/app/(public)/storefront-data.ts` contains a large static product/category dataset.
- Customer account page uses hardcoded profile/order data.
- Admin pages and components rely on local static arrays and fake dashboard metrics.
- This must be removed or isolated so the live backend is the only production data source when backend data is available.

## B. Required Fixes

1. Admin/customer role routing
   - Resolve the active auth state from backend user data and route by `role_name`.
   - Route `customer` to the public homepage.
   - Route `admin` to the existing admin dashboard.

2. Customer authentication
   - Use backend auth endpoints for login.
   - Restore auth state from cookie-backed session info and fetch current user.
   - Keep customer auth alive across refresh while JWT remains valid.

3. JWT cookies
   - Keep access/refresh tokens in cookies as the backend expects.
   - Ensure frontend requests use credentialed fetches where auth cookies are required.
   - Remove localStorage-based JWT persistence as the primary auth mechanism.

4. JWT lifetime
   - Preserve the backend-defined lifetime values from `settings` and avoid frontend overrides.
   - Refresh tokens remain the mechanism for renewing expired access tokens if the backend supports such rotation.

5. Guest session
   - Reuse one global guest session for public storefront/cart/checkout screens.
   - Keep guest order flow available without forced login.
   - Do not create per-page or per-component guest sessions.

6. Global cookie session
   - Prefer the backend session/cookie mechanism if it exists.
   - Avoid duplicate cookie keys or parallel session models.

7. IP address handling
   - Preserve the backend request IP association for sessions and guest operations.
   - Do not trust client-supplied IP information for security-sensitive flows.

8. Guest orders
   - Keep checkout and order creation flow available for guest users when the backend supports it.
   - Do not force login for guest checkout.

9. Customer My Account
   - Replace hardcoded account data with real backend data loaded for the authenticated customer.

10. Customer My Orders
   - Load actual orders for the signed-in customer only.
   - Guard against cross-user order leakage.

11. Header profile behavior
   - Logged-out profile icon goes to `/login`.
   - Authenticated customer profile icon goes to `/my-account`.
   - Authenticated admin profile behavior stays on the admin area.

12. Admin endpoint protection
   - Protect UI routes and backend endpoints.
   - Customer and guest must receive 401/403 from the backend when attempting admin actions.

13. Public functionality
   - Ensure guest browsing, cart, product pages, categories, search, and checkout remain accessible without login.

14. Backend-only data
   - The backend remains authoritative for user identity, roles, orders, and session ownership.
   - Frontend uses API response data, not local-only derived assumptions.

15. Static data removal/fallback behavior
   - Remove or isolate static storefront/admin data when a live backend response is available.
   - Only show backend data in production connected mode.
   - Keep offline/demo behavior clearly separated from backend mode.

16. API organization
   - Centralize auth and admin requests in existing API service patterns.
   - Reuse the existing HTTP client and backend URL configuration.

17. Frontend/backend integration
   - Connect frontend auth and route state to the backend cookie-based auth layer.
   - Use backend `role_name` as the final router and UI guard decision.

## C. Files To Modify

Before implementation, the likely modification set includes:
- `backend/src/app/api/auth.py`
- `backend/src/app/dependencies/auth.py`
- `backend/src/app/core/security.py`
- `backend/src/app/config.py`
- `backend/src/app/main.py`
- `frontend/app/(auth)/login/page.tsx`
- `frontend/app/(account)/my-account/page.tsx`
- `frontend/app/(account)/my-orders/page.tsx`
- `frontend/components/layout/PublicHeader/PublicHeader.tsx`
- `frontend/components/layout/PublicHeader/HeaderActions.tsx`
- `frontend/hooks/useAuth.ts`
- `frontend/store/slices/authSlice.ts`
- `frontend/store/index.ts`
- `frontend/app/providers.tsx`
- `frontend/services/api/client.ts`
- `frontend/services/api/auth.api.ts`
- `frontend/types/auth.ts`
- `frontend/types/customer.ts`
- `frontend/app/(public)/storefront-data.ts`
- any route guards or admin layout files required for real auth enforcement

## D. Files NOT To Modify

- All CSS files
- All loader CSS/components styling
- Any CSS reset or styling files
- `frontend/app/globals.css`
- `frontend/styles/**`
- `frontend/app/admin/styles/**`
- static design-only files unless required by backend/data logic

## E. Testing Plan

- Guest flow: homepage, products, category search, cart, checkout, guest order.
- Customer flow: login, redirect by role, cookie persistence, refresh restore.
- Admin flow: admin login, admin dashboard access, route protection, backend auth enforcement.
- JWT flow: token issuance, refresh rotation, expired token behavior.
- Cookies: access and refresh cookies set and cleared in browser.
- Session: guest session reuse and customer login migration behavior.
- IP address: backend request IP bindings remain consistent with session/cart/order flow.
- Cart/checkout/orders: guest and customer flows, ownership and data isolation.
- Public APIs: storefront endpoints remain accessible without forced login.
- Admin APIs: only active admins receive access.
- Route protection: customer/guest on admin routes blocked.
- Static data: no fake data appears in connected backend mode.
- Backend unavailable state: error/empty/loading patterns remain clear and do not pretend data exists.

## Implementation status

Status: Core implementation completed and validated; remaining admin screens are now backend-connected where supported.

### Completed
- Cookie-backed JWT authentication and session restoration.
- Backend role-based admin/customer route guards.
- Public profile routing for guest, customer, and admin users.
- HTTP-only guest session cookie with backend-owned guest cart/order checkout flow.
- Live backend catalog, customer profile/address/order overview, and order history loading.
- Real checkout mutation replacing client-generated fake orders.
- Frontend TypeScript validation and focused auth/account/header tests.
- Backend authentication regression suite: 18 tests passing.
- Admin analytics, reports, settings, IP policy, and wishlist summary screens now use backend API contracts.
- Connected admin list screens no longer render seeded business rows when backend data is absent.

### Remaining
- Wire hero and chat screens to their existing backend conversation/hero mutations and remove their remaining seeded state.
- Wire customer profile/address/password form submissions to backend mutations.
- Add dedicated guest checkout and admin authorization integration tests.
- Remove remaining unused demo constants and unsupported export/download success toasts.
