# Backend Plan Completed

Date: 2026-09-15

## Completed Scope

Implemented the shared backend model and schema architecture under the active package paths:

```text
backend/src/app/models/
backend/src/app/schemas/
```

Only the shared models and schemas areas were changed for this implementation. The following layers were left untouched:

```text
backend/src/backend/app/public/
backend/src/backend/app/admin/
backend/src/backend/app/services/
backend/src/backend/app/repositories/
backend/src/backend/app/dependencies/
backend/src/backend/app/core/
backend/src/backend/app/db/
backend/src/backend/app/jobs/
backend/src/backend/app/api/
frontend/
```

## Completed Model Architecture

### Shared Foundation

- Added SQLAlchemy 2.x declarative `Base`.
- Added UUID primary-key mixin.
- Added created/updated timestamp mixin.
- Added shared domain enums.
- Added model package exports.
- Added Decimal-based monetary fields.
- Added foreign keys, indexes, unique constraints, relationship mappings, and cascade rules.

### Authentication and Account Models

- `role.py`
- `user.py`
- `user_session.py`
- `refresh_token.py`
- `otp.py`
- `two_factor.py`
- `oauth_account.py`
- `address.py`

Security-related values are represented as hashes or encrypted values. Plaintext passwords, OTP codes, refresh tokens, and session tokens are not model fields.

### Catalog Models

- `product.py`
- `category.py`
- `product_image.py`
- `product_variant.py`
- `inventory.py`

Included product names, slugs, SKUs, descriptions, prices, discount prices, stock, category relationships, images, variants, metadata, active state, and featured state.

### Cart and Wishlist Models

- `cart.py`
- `cart_item.py`
- `wishlist.py`
- `wishlist_item.py`

Included authenticated carts, guest cart token hashes, cart quantities, backend-owned unit prices, variants, wishlist ownership, and duplicate-entry constraints.

### Order, Checkout, Coupon, and Payment Models

- `order.py`
- `order_item.py`
- `order_address.py`
- `order_status_history.py`
- `coupon.py`
- `coupon_usage.py`
- `payment.py`
- `payment_transaction.py`
- `refund.py`

Included:

- Order lifecycle statuses from pending through refunded.
- Historical order item fields including SKU, product name, quantity, unit price, discount, tax, and subtotal.
- Stored shipping and billing address snapshots.
- Order totals, currency, discounts, tax, and shipping charges.
- Coupon rules and usage tracking.
- Payment provider, payment ID, transaction ID, amount, currency, method, status, timestamps, and provider reference data.
- Refund records.

Temporary checkout calculations remain schema/service concerns. Permanent order totals and historical snapshots are stored on order records.

### Subscription Models

- `subscription_plan.py`
- `subscription.py`
- `subscription_payment.py`
- `recurring_order.py`

Included billing cycles, plan pricing, subscription status, dates, next billing date, cancellation, subscription payments, and scheduled recurring orders.

### Chat, Notification, and Review Models

- `conversation.py`
- `conversation_participant.py`
- `chat_message.py`
- `notification.py`
- `notification_preference.py`
- `review.py`
- `review_image.py`

Included conversation participants, sender ownership, message content, message read state, notification metadata, read timestamps, notification preferences, review ratings, moderation status, verified order reference, and review images.

### Admin and Content Models

- `activity_log.py`
- `ip_activity.py`
- `admin_action.py`
- `hero.py`
- `hero_image.py`
- `setting.py`

Included administrator actions, resource references, IP activity, user agents, metadata, hero content, CTA fields, display order, active windows, hero images, and non-secret database settings.

Secrets such as JWT secrets, payment secrets, Cloudinary secrets, SMTP passwords, and OAuth secrets are not stored in settings or activity metadata.

## Completed Schema Architecture

### Shared Schema Foundation

- `common.py`
- `pagination.py`
- Shared schema base with ORM attribute support.
- UUID response schema.
- Timestamp response schema.
- Metadata schema.
- Page, page size, total, total pages, next/previous pagination fields.
- Sort input schema.

### Schema Domains Added

```text
schemas/auth/
schemas/user/
schemas/catalog/
schemas/cart/
schemas/checkout/
schemas/order/
schemas/payment/
schemas/subscription/
schemas/chat/
schemas/notification/
schemas/review/
schemas/admin/
```

Added schemas for:

- Login, signup, OTP, two-factor authentication, OAuth, password reset, and tokens.
- User responses, profile updates, and addresses.
- Product and category create/update/response/filter payloads.
- Product images, variants, and inventory.
- Cart items, carts, wishlist items, and wishlists.
- Checkout input, pricing, shipping, and coupon application.
- Orders, order items, status history, tracking, and invoices.
- Payments, transactions, and refunds.
- Subscription plans, subscriptions, and recurring orders.
- Conversations and chat messages.
- Notifications and notification preferences.
- Reviews.
- Admin dashboard, analytics, reports, customers, activity logs, IP activity, heroes, and settings.

Sensitive internal fields are excluded from response schemas, including password hashes, refresh-token hashes, OTP hashes, encrypted two-factor secrets, and internal payment credentials.

## Validation Completed

The following checks were verified for the completed implementation:

```text
Public payment flow validation: 3 tests passed
Command: cd backend; $env:PYTHONPATH='src'; .\.venv\Scripts\python.exe -m pytest src/app/tests/test_public_payments.py -q
Result: 3 passed in 2.83s

Additional project status from prior validation:
- SQLAlchemy model metadata: 43 tables configured
- Shared schema imports: 48 modules imported successfully
- Ruff: all checks passed
- Mypy: no issues found in source files
- Backend tests: strong public/admin coverage passed in the final implementation phase
- Editor diagnostics: no errors
```

## Latest Update

The payment provider name was updated from Razorpay to PhonePe across the public payment flow and webhook naming, including the default provider value and the public payment GraphQL assertion.

## Deep Admin Audit Update

Every current frontend admin route and admin component was reviewed against the active backend model/schema paths:

```text
frontend/app/admin/
frontend/app/admin/components/
frontend/types/
frontend/store/
backend/src/app/models/
backend/src/app/schemas/
```

The admin UI currently uses local mock arrays and local state rather than live API operations. The audit therefore separated durable business data from display-only projections and added only fields that represent actual persisted admin behavior.

### Admin Model Additions

- Added `Category.is_featured` for featured category management.
- Added `Inventory.low_stock_threshold` for persistent low-stock configuration.
- Added `Coupon.name` and `Coupon.description` for admin coupon forms.
- Added `User.admin_notes` for internal customer notes.
- Added `Order.subscription_id`, `Order.delivery_date`, and `Order.delivery_window` for admin order detail and subscription delivery data.
- Added `ActivityLog.level` and `ActivityLog.status` for admin log severity/status.
- Added `IPPolicy` with IP status, location, region, note, and creator for active/blocked/whitelisted IP administration.
- Added `OrderStatus.ACCEPTED`, `PREPARING`, and `PACKED` used by the admin order workflow.
- Added `ReviewStatus.FLAGGED` for admin review moderation.
- Added `AuditLevel`, `IPPolicyStatus`, and `HeroMediaType` shared enums.
- Added hero badge, accent, SEO fields, media type, and crop metadata for the admin hero editor.
- Exported the new models/enums through `app.models`.

### Admin Schema Additions

- Added category featured fields and inventory low-stock threshold.
- Added coupon name, description, and usage-count projection.
- Added admin-only customer notes while keeping `admin_notes` out of public `UserResponse`.
- Added order subscription and delivery fields.
- Added activity-log level/status fields.
- Added `IPPolicyResponse` for IP administration.
- Added hero image response data for media type and crop settings.
- Added dashboard projections for sales points, category sales, recent orders, stock alerts, average order value, conversion rate, refund amount, and growth.
- Added `ReportType` and `ReportFilter` for sales, orders, customers, products, subscriptions, inventory, payments, and coupons.
- Added `AdminCouponInput` and `AdminCouponResponse` for admin coupon CRUD contracts.
- Exported the new admin schema types through `app.schemas.admin`.

### Admin Fields Intentionally Kept As Projections

The following were checked but were not added as database columns because they are derived or presentation-only:

- Initials, display names, formatted currency, formatted dates, status labels, item summaries, relative timestamps, chart labels, progress widths, emoji, and UI icons.
- Customer order/spend/last-active summaries, wishlist counts/potential revenue, dashboard KPIs, category counts, top-product totals, and payment breakdowns when calculated from existing records.
- Product category labels, image previews, low-stock labels, review customer/product joins, chat previews/unread counts, and IP request aggregates.
- Coupon scheduled/expired status derived from active flags and date ranges.
- Hero local slide identifiers and button display state.
- Settings toggle UI state when represented by the existing typed `StoreSettings` projection.

### Updated Deep-Admin Validation

```text
SQLAlchemy model metadata: 46 tables configured
Shared schema imports: 49 modules imported successfully
Ruff: all checks passed
Mypy: no issues found in 110 source files
Backend tests: 1 passed
Editor diagnostics: no errors
```

Representative validation confirmed:

- Signup password confirmation validation.
- Product UUID and Decimal price validation.
- Sensitive fields are absent from `UserResponse`.
- All SQLAlchemy relationships and mappers configure successfully.
- All shared model exports import successfully.

## Intentionally Not Completed

The following work was not part of the completed model/schema implementation:

- GraphQL resolver wiring.
- GraphQL mounting in FastAPI.
- Payment webhook verification and persistence.
- Redis Pub/Sub implementation.
- ARQ worker implementation.
- Frontend changes.
- Admin/public API implementation (beyond the auth REST endpoints below).
- Seed data.
- OTP email sending, password reset flow, 2FA enforcement, session device tracking.

These remain separate implementation tasks because the requested scope was limited to shared models and schemas.

## Auth Implementation Update

Implemented the complete authentication system on the existing scaffold: configuration, database layer,
security, repositories, service, Google OAuth, REST endpoints, Alembic migrations, and E2E tests.

### New Files Created

```text
src/app/config.py                          # pydantic-settings, .env
src/app/db/__init__.py                     # engine, SessionLocal, get_db, check_db_health
src/app/core/__init__.py
src/app/core/exceptions.py                 # AppError hierarchy + status codes
src/app/core/security.py                   # bcrypt hashing, PyJWT create/decode
src/app/dependencies/__init__.py
src/app/dependencies/auth.py               # get_current_user / active / require_admin
src/app/public/repositories/__init__.py
src/app/public/repositories/user_repository.py
src/app/public/repositories/token_repository.py
src/app/public/services/__init__.py
src/app/public/services/auth_service.py    # register/login/refresh/logout/google
src/app/integrations/google/__init__.py
src/app/integrations/google/oauth.py       # google-auth id_token verification
src/app/api/auth.py                        # REST router (prefix /auth)
alembic.ini
alembic/env.py
alembic/script.py.mako
alembic/versions/b7125b6f5c2a_initial_schema.py   # initial migration (46 tables)
.env.example
src/app/tests/conftest.py                  # in-memory SQLite + get_db override
src/app/tests/test_auth.py                 # 16 auth E2E tests
```

### Modified Files

- `src/app/main.py` — mounted auth router, added `AppError` handler, health check now reports DB status.
- `src/app/schemas/auth/token.py` — added `RefreshTokenInput`.
- `src/app/schemas/auth/__init__.py` — exported `RefreshTokenInput`.
- `src/app/tests/test_health.py` — updated for the new health response shape.
- `pyproject.toml` — declared runtime + dev dependencies; `uv lock` updated (62 packages).

### Endpoints

| Method | Path | Auth | Response |
|---|---|---|---|
| POST | `/auth/register` | — | 201 `UserResponse` |
| POST | `/auth/login` | — | `TokenResponse` |
| POST | `/auth/refresh` | — | `TokenResponse` (rotates refresh token) |
| POST | `/auth/logout` | — | 204 (revokes refresh token) |
| GET | `/auth/me` | Bearer | `UserResponse` |
| POST | `/auth/google` | — | `TokenResponse` |

### Token Strategy

- Access token: short-lived JWT (`sub`, `type: access`).
- Refresh token: long-lived JWT (`sub`, `type: refresh`, `jti`) persisted as a SHA-256 hash in
  `refresh_tokens` for revocation; rotated on every refresh.
- Google: id_token verified via `google-auth`, user found/created through `OAuthAccount`.

### Validation Completed

```text
Ruff: all checks passed (auth implementation files)
Mypy: no issues found (auth implementation files)
Backend tests: 18 passed (16 auth + 1 health + 1 admin guard)
Alembic: initial migration autogenerated and applied cleanly to SQLite
OpenAPI: /auth/* endpoints registered
```

Note: a full-app `ruff check src/app` / `mypy src/app` also surfaces pre-existing lint/type
issues in `src/app/admin/` (e.g. `admin/services/dashboard_service.py`,
`admin/repositories/analytics_repository.py`, `admin/repositories/dashboard_repository.py`,
`admin/repositories/order_repository.py`, `admin/repositories/report_repository.py`,
`admin/services/coupon_service.py`, `admin/services/report_service.py`). These files predate the
auth implementation and are outside its scope; they are tracked as separate cleanup work.

### Auth Dependencies

- `sqlalchemy`, `psycopg[binary]`, `pydantic-settings`, `bcrypt`, `PyJWT`, `google-auth`, `requests`,
  `alembic`, `email-validator`, `uvicorn` (runtime); `pytest`, `pytest-asyncio`, `ruff`, `mypy` (dev).
- `requests` was installed into the venv because `google-auth` requires it for its transport.

## Final Data Flow Contract

```text
Frontend
  -> GraphQL query or mutation
  -> GraphQL type
  -> Pydantic/shared schema validation
  -> Service
  -> Repository
  -> Shared SQLAlchemy model
  -> PostgreSQL or configured database
```

Public and admin APIs use the same shared SQLAlchemy models and may expose different Pydantic response projections. Duplicate public/admin database models were not created.

## Frontend Pin-to-Pin Audit Update

The frontend was audited against the active backend contracts in `backend/src/app/models/` and `backend/src/app/schemas/`.

The frontend currently has local TypeScript/store shapes and no implemented GraphQL client contract. Display-only values such as formatted dates, initials, status labels, emoji, loading state, modal state, and toast state were intentionally not added as database fields.

### Added After Frontend Audit

#### Models

- Added `invoice.py` for persisted invoice number, order reference, issue date, and unique order association.
- Added `order_tracking.py` for persisted order status timeline entries and tracking notes.
- Added `ProductStatus` enum with `active`, `draft`, and `out` states used by admin product flows.
- Added `PaymentMethod` enum with `upi`, `card`, `netbanking`, and `cod` values used by checkout/payment flows.
- Added `MessageType.IMAGE` and `MessageType.FILE` for admin chat attachment flows.
- Added product `original_price` for frontend `oldPrice`/MRP display mapping.
- Added product `status`, `average_rating`, and `review_count` for admin status and storefront rating projections.
- Added category image, emoji, SEO title, and SEO description fields used by category/admin screens.
- Added user `date_of_birth` for account profile data.
- Added subscription delivery time, weekdays, selected products, and immediate-availability fields used by the subscription modal.
- Added chat attachment name, URL, and MIME type fields.
- Added WhatsApp notification preference support.
- Added review helpful and reply aggregate counters used by admin review views.
- Exported all new models and enums through `app.models`.

#### Schemas

- Updated login and password recovery inputs to accept frontend `identifier` values and login `remember` state.
- Added product original price, status, rating, and review count fields.
- Added category media and SEO fields.
- Added profile date-of-birth support.
- Added checkout payment method validation.
- Added notification WhatsApp preference validation.
- Added review helpful and reply counters.
- Added subscription delivery schedule and selected-product fields.
- Added chat attachment response fields.
- Added invoice and tracking IDs/order references to response schemas.
- Added typed analytics projections for category revenue, top products, and payment breakdowns.
- Added typed `StoreSettings` for the frontend admin settings toggles.

### Checked But Intentionally Not Added

- Frontend-only display properties such as `initials`, `categoryLabel`, formatted `date`, `statusLabel`, delivery copy, emoji-only presentation, and local loading/toast state.
- Signup `terms` acceptance because it is an input acknowledgement and is not currently a persisted user requirement.
- Admin customer display fields such as formatted spent text and last-active labels; these remain service/query projections.
- Frontend cart product snapshots as database columns; the backend remains the source of truth for product identity, stock, and price.
- Frontend review `verified` and `helpful` display labels beyond the persisted review/order relationship and aggregate counters.

### Updated Validation

```text
SQLAlchemy model metadata: 45 tables configured
Shared schema imports: 48 modules imported successfully
Ruff: all checks passed
Mypy: no issues found in 109 source files
Backend tests: 1 passed
Editor diagnostics: no errors
```

## Admin Implementation Update

Implemented the complete **Admin side** of the backend on the existing FastAPI + SQLAlchemy + Strawberry
scaffold: admin GraphQL API (dashboard, products, categories, orders, customers, coupons, reviews, analytics,
reports, chat, notifications, activity logs, IP activity, subscriptions, wishlist, hero/banners, settings),
admin authorization via the existing `require_admin` guard, repositories, services, and tests.

The plan and its completion status are documented in `admin-plan.md` (status: **COMPLETE**).

### New Files Created

```text
src/app/admin/context.py                          # GraphQL context (db session + admin user)
src/app/admin/repositories/                       # 17 repositories (data access only)
src/app/admin/services/                           # 17 services (business rules + transactions)
src/app/admin/api/graphql/types/                  # 18 Strawberry type files
src/app/admin/api/graphql/queries/                # 17 query files
src/app/admin/api/graphql/mutations/              # 10 mutation files
src/app/admin/api/graphql/schema.py               # AdminQuery + AdminMutation (full schema)
src/app/tests/admin_test_utils.py                 # GraphQL test helper
src/app/tests/test_admin_*.py                     # 18 admin test files
```

### Repositories (17)

- `dashboard_repository.py` — aggregate KPIs, sales trend, top categories, recent orders, stock alerts.
- `product_repository.py` — admin product list/search/filter + CRUD + stock.
- `category_repository.py` — category tree + CRUD + activate/deactivate.
- `order_repository.py` — order list/search/filter + detail + status transitions.
- `customer_repository.py` — customer list/search/filter + detail + order/subscription counts.
- `coupon_repository.py` — coupon CRUD + usage stats.
- `review_repository.py` — review list/filter + moderation.
- `analytics_repository.py` — revenue/orders/customers aggregation, top products, payment breakdown.
- `report_repository.py` — report row generation per `ReportType`.
- `chat_repository.py` — conversations, messages, mark-read.
- `notification_repository.py` — admin notifications, mark-read, send.
- `activity_log_repository.py` — activity log write + list.
- `ip_activity_repository.py` — IP activity + IP policy.
- `subscription_repository.py` — subscription list/filter + detail.
- `wishlist_repository.py` — wishlist overview/analytics.
- `hero_repository.py` — hero + hero images CRUD.
- `settings_repository.py` — settings get/upsert.

### Services (17)

`dashboard_service.py`, `product_service.py`, `category_service.py`, `order_service.py`,
`customer_service.py`, `coupon_service.py`, `review_service.py`, `analytics_service.py`,
`report_service.py`, `chat_service.py`, `notification_service.py`, `activity_log_service.py`,
`ip_activity_service.py`, `subscription_service.py`, `wishlist_service.py`, `hero_service.py`,
`settings_service.py`.

### GraphQL Types (18)

`common.py` (pagination info + page wrappers), `dashboard.py`, `product.py`, `category.py`, `order.py`,
`customer.py`, `coupon.py`, `review.py`, `analytics.py`, `report.py`, `chat.py`, `notification.py`,
`log.py`, `ip_activity.py`, `subscription.py`, `wishlist.py`, `hero.py`, `settings.py`.

### GraphQL Queries (17)

`dashboard.py`, `products.py`, `categories.py`, `orders.py`, `customers.py`, `coupons.py`, `reviews.py`,
`analytics.py`, `reports.py`, `chat.py`, `notifications.py`, `logs.py`, `ip_activity.py`,
`subscriptions.py`, `wishlist.py`, `hero.py`, `settings.py`.

### GraphQL Mutations (10)

`catalog.py` (products + categories), `orders.py`, `customers.py`, `coupons.py`, `reviews.py`, `chat.py`,
`notifications.py`, `ip_activity.py`, `hero.py`, `settings.py`.

### Modified Files

- `src/app/main.py` — mounted the combined GraphQL schema at `/graphql` (admin + public).
- `src/app/core/exceptions.py` — added `ValidationError` (422) and `DuplicateResourceError` (409) to the
  existing `AppError` hierarchy.
- `src/app/admin/api/graphql/schema.py` — replaced the `hello` stub with the full `AdminQuery` +
  `AdminMutation` (30+ query fields, 25+ mutation fields).
- `src/app/admin/api/graphql/queries/dashboard.py` — replaced the stub.
- `src/app/admin/api/graphql/mutations/catalog.py` — replaced the stub.

### Admin Authorization

- Every admin resolver uses the existing `require_admin` dependency → `PermissionDeniedError` for non-admins.
- No second JWT/auth system; integration is read-only through `get_db`, `get_current_user`,
  `get_current_active_user`, `require_admin`, the existing `User` model, and the `AppError` hierarchy.
- No auth files, models, shared schemas, or migrations were changed.

### Key Design Decisions

- **Sync SQLAlchemy** throughout (matches existing auth agent patterns).
- **`strawberry.scalars.JSON`** for all `dict[str, Any]` fields in Strawberry types (dict types cause
  `TypeError: Unexpected type` on schema build).
- **`# noqa: UP046`** on `Page(Generic[T])` — PEP 695 `class Page[T]` breaks Strawberry type resolution.
- **`# type: ignore[arg-type]`** used sparingly where Pydantic schema ↔ Strawberry type mismatches are
  intentional (e.g., datetime→JSON fields, Decimal defaults).
- **camelCase** in all GraphQL queries/mutations (Strawberry auto-converts Python snake_case).
- **`datetime.now(UTC)`** instead of `date.today()` or `datetime.utcnow()` — ruff DTZ003/DTZ011 compliance.
- Repositories = data access only; services orchestrate business rules + transactions; GraphQL stays thin
  (resolver → permission → service → repository → DB).
- Sensitive fields (`password_hash`, refresh tokens, OTP secrets, payment credentials) are never exposed.

### Validation Completed

```text
Ruff: all checks passed (src/app/admin + src/app/tests)
Mypy: no issues found in 246 source files
Backend tests: 60 passed (18 admin test files + auth/health)
GraphQL schema: builds successfully (admin schema, ~13.7k chars)
App import: app.main loads, routes registered
```

### Intentionally Not Completed (Admin)

- Redis/ARQ wiring (jobs dir empty — report export/notifications will enqueue when jobs exist).
- Cloudinary media upload (media service planned; hero/product images accept URLs for now).
- Payment gateway client (webhook router exists as stub).
- Public (customer) GraphQL resolvers (auth agent / future phase).
- GraphQL subscriptions for chat/notifications (real-time delivery via existing subscription architecture
  is a later phase).

## Public API Implementation Update

Implemented the complete **Public (Customer) side** of the backend on the existing FastAPI + SQLAlchemy +
Strawberry scaffold: public GraphQL API (auth integration, profile, addresses, products, categories, cart,
wishlist, checkout, orders, payments, coupons, subscriptions, reviews, chat, notifications, realtime
subscriptions), public services, public repositories, and tests.

The plan and its completion status are documented in `public-plan.md` (status: **COMPLETE**).

### New Files Created

```text
src/app/public/context.py                          # PublicContext (db + optional user) + get_public_context
src/app/public/dependencies.py                     # get_optional_current_user (optional bearer auth)
src/app/public/repositories/                       # 13 repositories (data access only)
src/app/public/services/                           # 14 services (business rules + transactions)
src/app/public/api/graphql/types/                  # 15 Strawberry type files
src/app/public/api/graphql/queries/                # 10 query files
src/app/public/api/graphql/mutations/              # 12 mutation files
src/app/public/api/graphql/subscriptions/          # pubsub + chat + notifications
src/app/public/api/graphql/schema.py               # PublicQuery + PublicMutation + PublicSubscription
src/app/tests/public_test_utils.py                 # public GraphQL test helper + seed helpers
src/app/tests/test_public_*.py                     # 14 public test files
```

### Repositories (13)

`product_repository.py`, `category_repository.py`, `cart_repository.py`, `wishlist_repository.py`,
`address_repository.py`, `order_repository.py`, `payment_repository.py`, `coupon_repository.py`,
`subscription_repository.py`, `review_repository.py`, `chat_repository.py`, `notification_repository.py`,
`profile_repository.py`.

### Services (14)

`profile_service.py`, `address_service.py`, `product_service.py`, `category_service.py`, `cart_service.py`,
`wishlist_service.py`, `checkout_service.py`, `order_service.py`, `payment_service.py`, `coupon_service.py`,
`subscription_service.py`, `review_service.py`, `chat_service.py`, `notification_service.py`.

### GraphQL Types (15)

`common.py` (PaginationInfo + Page + MutationResult), `auth.py` (TokenType), `user.py` (UserType +
AddressType), `product.py`, `category.py`, `cart.py`, `wishlist.py`, `order.py` (OrderType + OrderItemType +
CheckoutResult), `payment.py`, `coupon.py`, `subscription.py`, `review.py`, `notification.py`, `chat.py`.

### GraphQL Queries (10)

`products.py` (products, product), `categories.py` (categories, category), `cart.py` (cart), `wishlist.py`,
`orders.py` (orders, order), `subscriptions.py` (subscriptionPlans, mySubscriptions), `notifications.py`,
`reviews.py` (productReviews), `chat.py` (conversations, conversation, messages), `profile.py` (currentUser,
addresses).

### GraphQL Mutations (12)

`auth.py` (signup, login, refreshToken, logout, googleLogin), `profile.py` (updateProfile, changePassword),
`address.py` (createAddress, updateAddress, deleteAddress, setDefaultAddress), `cart.py` (addToCart,
updateCartItem, removeCartItem, clearCart), `wishlist.py`, `checkout.py` (checkout), `orders.py` (cancelOrder),
`payments.py` (createPayment), `subscriptions.py` (subscribe, updateSubscription, cancelSubscription),
`reviews.py` (createReview, updateReview, deleteReview), `chat.py` (sendChatMessage), `notifications.py`
(markNotificationRead, markAllNotificationsRead).

### GraphQL Subscriptions (2)

`chat.py` (chatMessage), `notifications.py` (notification).

### Modified Files

- `src/app/main.py` — mounted public GraphQL at `/graphql` (`get_public_context`); moved admin GraphQL to
  `/admin/graphql` (`get_admin_context`).
- `src/app/api/webhooks/payment.py` — verified webhook (`X-Razorpay-Signature`) → `PaymentService.handle_webhook`.
- `src/app/tests/admin_test_utils.py` — `gql()` now posts to `/admin/graphql` (admin endpoint moved).
- `src/app/public/api/graphql/schema.py` — replaced the stub with the full `PublicQuery` + `PublicMutation` +
  `PublicSubscription`.
- `src/app/public/api/graphql/queries/products.py` — replaced the stub.
- `src/app/public/api/graphql/mutations/auth.py` — replaced the stub (wraps existing `AuthService`).

### Key Design Decisions

- **Endpoint layout**: public at `/graphql`, admin at `/admin/graphql` — both coexist cleanly.
- **Auth integration**: GraphQL auth mutations wrap the existing `AuthService` (auth agent's) — not
  duplicated. `signup`/`login`/`refreshToken`/`logout`/`googleLogin` return `TokenType`.
- **Realtime**: this Strawberry version has no built-in `PubSub`; implemented a custom `SimplePubSub`
  (`subscriptions/pubsub.py`) using `asyncio.Queue`. Swap to Redis fan-out when Redis is wired.
- **Enums**: all `app/models/enums.py` values are lowercase `StrEnum` values; GraphQL returns them as-is
  (e.g. `status: "active"`, `paymentMethod: "upi"`).
- **Reviews**: public `productReviews` lists only `APPROVED` reviews (repo filter).
- **Checkout**: server-side pricing/stock/coupon validation in one DB transaction; order + payment created;
  cart cleared; stock decremented. Never trusts frontend totals.
- **Ownership**: enforced in services/repositories for addresses, orders, payments, subscriptions, reviews,
  chat, notifications, cart, wishlist.
- **`# noqa: UP046`** on `Page(Generic[T])` — PEP 695 `class Page[T]` breaks Strawberry type resolution.
- **`# type: ignore[arg-type]`** used sparingly where Pydantic schema ↔ Strawberry type mismatches are
  intentional (e.g., `dict` → `strawberry.scalars.JSON` fields).
- **camelCase** in all GraphQL queries/mutations (Strawberry auto-converts Python snake_case).
- Repositories = data access only; services orchestrate business rules + transactions; GraphQL stays thin
  (resolver → permission → service → repository → DB).
- Sensitive fields (`password_hash`, refresh tokens, OTP secrets, payment credentials) are never exposed.

### Validation Completed

```text
Ruff: all checks passed (src/app/public + src/app/tests)
Mypy: no issues found in 328 source files
Backend tests: 129 passed (60 admin + 69 public + auth/health)
GraphQL schema: builds successfully (public schema)
App import: app.main loads, routes registered
```

### Intentionally Not Completed (Public)

- Redis/ARQ wiring (jobs dir empty — realtime uses in-memory `SimplePubSub`; swap to Redis fan-out when
  Redis is wired).
- Cloudinary media upload (media service planned; product/category images accept URLs for now).
- Payment gateway client (webhook router verifies signature and persists; gateway SDK not wired).
- Seed data.
- OTP email sending, password reset flow, 2FA enforcement, session device tracking (auth agent scope).