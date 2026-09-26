# Agent Integration Audit

Branch: `feature/bug-fixing-fronetend` · Base commit: `e60a243` (chat-application)
Scope: four completed agent workstreams (auth persistence, products/cart, chat, Google OAuth)
integrated into one application, checked for collisions and regressions.

---

## 1. Agent / task / file map

### Agent A — Auth persistence (`bug-authentication.md`, `plan-creating.md`)

| Layer | Files |
| --- | --- |
| Backend deps | `backend/src/app/dependencies/auth.py`, `backend/src/app/public/dependencies.py` |
| Backend REST | `backend/src/app/api/auth.py`, `backend/src/app/schemas/auth/__init__.py` |
| Frontend client | `frontend/services/api/client.ts`, `frontend/services/api/auth.api.ts`, `frontend/services/api/account.api.ts` |
| Frontend state | `frontend/app/providers.tsx`, `frontend/store/slices/authSlice.ts` |
| Tests | `backend/src/app/tests/test_auth_persistence.py` (new, 16 tests), `frontend/services/api/client.test.ts`, `frontend/services/api/auth.api.test.ts` |

Outcome: access token is read from the `Authorization` header **or** the HttpOnly
`access_token` cookie; refresh/logout rotate cookies. No JavaScript token storage was
introduced, so the existing cookie architecture is preserved.

### Agent B — Products / cart (`bug-view-product.md`)

| Layer | Files |
| --- | --- |
| API client | `frontend/services/api/products.api.ts`, `frontend/services/api/cart.api.ts`, `frontend/services/api/categories.api.ts` |
| Pages | `frontend/app/(public)/products/[slug]/page.tsx`, `frontend/app/(public)/products/ProductsPage.tsx`, `frontend/app/(public)/cart/page.tsx`, `frontend/app/(public)/landingPage.tsx` |
| State / types | `frontend/hooks/useCart.ts`, `frontend/store/slices/cartSlice.ts`, `frontend/types/cart.ts`, `frontend/store/index.ts` |
| Mapping / SEO | `frontend/app/(public)/storefront-data.ts`, `frontend/app/sitemap.ts` |
| Tests | `frontend/services/api/products.api.test.ts`, `frontend/services/api/cart.api.test.ts`, `frontend/hooks/useCart.test.ts`, `frontend/store/slices/cartSlice.test.ts`, `frontend/app/(public)/products/[slug]/page.test.tsx` |

Outcome: the backend catalog is the source of truth. `toStorefrontProduct()` is the single
mapping from a backend `CatalogProduct` to the storefront shape used by cards, cart rows and
the detail page, replacing three copies of the same inline mapping.

### Agent C — Chat (`chat-bug-investigation.md`, `chat-bug-fix.md`)

| Layer | Files |
| --- | --- |
| Backend service | `backend/src/app/public/services/chat_service.py` |
| Backend GraphQL | `backend/src/app/public/api/graphql/mutations/chat.py`, `backend/src/app/public/api/graphql/queries/chat.py`, `backend/src/app/public/api/graphql/subscriptions/chat.py` |
| Backend identity | `backend/src/app/public/context.py` |
| Frontend socket | `frontend/services/websocket/chat.socket.ts`, `frontend/jest.setup.ts`, `frontend/components/chat/SupportChat.test.tsx` |
| Removed | `frontend/context/ChatContext/index.ts` (dead duplicate context) |
| Tests | `backend/src/app/tests/test_public_chat.py` (+3 security tests), `backend/src/app/tests/test_public_chat_websocket.py` (new) |

Outcome: guest identity handling no longer writes a supplied email onto a registered
account, no longer duplicates the guest name, and read-only queries no longer mint a user
row.

### Agent D — Google OAuth (`google-auth-bug-investigation.md`, `google-fix.md`)

| Layer | Files |
| --- | --- |
| Backend | `backend/src/app/api/auth.py`, `backend/src/app/schemas/auth/oauth.py`, `backend/src/app/public/services/auth_service.py`, `backend/src/app/public/repositories/user_repository.py` |
| Frontend | `frontend/hooks/useGoogleAuth.ts` (new), `frontend/services/google/` (new), `frontend/app/(auth)/login/page.tsx`, `frontend/app/(auth)/signup/page.tsx` |
| Tests | `backend/src/app/tests/test_auth.py` (+397 lines), `frontend/hooks/useGoogleAuth.test.ts`, `frontend/app/(auth)/login/page.test.tsx`, `frontend/app/(auth)/signup/page.test.tsx` |

Outcome: one Google endpoint pair (`GET /auth/google/config`, `POST /auth/google`) shared by
login and signup. The client secret stays on the backend; the browser only receives the
client id. There is exactly one Google implementation in the tree.

---

## 2. Shared files and collision analysis

| Shared file | Agents | Finding |
| --- | --- | --- |
| `frontend/app/providers.tsx` | A, B | **Blocking collision** — see D1 |
| `frontend/services/api/client.ts` | A, D | Compatible. Google calls go through the same client, so 401 → refresh → retry applies uniformly. |
| `backend/src/app/api/auth.py` | A, D | Compatible. A added cookie-aware refresh/logout; D added `/auth/google/*`. Disjoint handlers, shared session helpers. |
| `backend/src/app/dependencies/auth.py` | A, C | **Blocking collision** — see D2 |
| `backend/src/app/public/dependencies.py` | A, C | **Blocking collision** — see D2 |
| `backend/src/app/public/context.py` | A, C | **Blocking collision** — see D2 |
| `frontend/app/(public)/cart/page.tsx` | B | Self-consistent. `payGo` rows are no longer wrapped in a `Link href="#"`. |
| `frontend/app/(public)/storefront-data.ts` | B | `Product.category` widened from a 4-value union to `string` so backend category slugs are representable; `ProductGrid.StoreProduct` widened in step. |
| `frontend/app/sitemap.ts` | B | Product URLs removed from the static sitemap so the demo array is no longer advertised as real catalog. |
| `backend/src/app/models/**`, `backend/alembic/**` | — | **Untouched.** No agent changed a model or migration, so no schema migration is required. |

Duplicate-implementation sweep: one `store` (`frontend/store/index.ts`), one `ChatProvider`,
one Google module, one `chat.socket.ts`, one cart API client. No duplicated auth system.

---

## 3. Integration defects found and fixed

### D1 — Application-wide crash: Redux hooks above the store (blocking)

`frontend/app/providers.tsx` called `useAppSelector` in the `Providers` component body, but
`Providers` is what *creates* the redux `<Provider>`. Every page using that store threw
`could not find react-redux context value; please ensure the component is wrapped in a
<Provider>` at runtime. `tsc` and the existing suite were both green because no test rendered
`Providers` itself.

Fixed by moving the store-aware bootstrap into a `StoreBootstrap` child rendered beneath
`<Provider>`, and dropping the superseded revision counter / store ref. Covered by
`frontend/app/providers.test.tsx`, verified to fail when the bad hook is reintroduced.

### D2 — Realtime chat was completely non-functional (blocking)

Agent C documented the WebSocket problem but did not implement the fix, and no test exercised
the WebSocket transport. Every chat test posts to `/graphql` over HTTP, so the suite stayed
green while the feature was dead.

Reproduced against the real ASGI websocket path:

```
TypeError: HTTPBearer.__call__() missing 1 required positional argument: 'request'
```

for both anonymous and bearer clients — the handshake never completed, so no subscription
could ever be delivered.

Cause: `HTTPBearer` requires an `http` scope, and the public context injected HTTP-only
`Request`/`Response`. Fixed by resolving the token from an `HTTPConnection` (valid for both
transports) in `app/dependencies/auth.py` and `app/public/dependencies.py`, and by taking an
`HTTPConnection` in `get_public_context` while skipping the `guest_token` `Set-Cookie` on a
WebSocket, which has no response to write to. Token precedence (Bearer header, then cookie)
is unchanged, so no security was weakened. `app/admin/context.py` inherits the fix through
`require_admin`.

`subscribe_chat_message` was also changed from an async generator function to a plain function
returning one, so the participant check runs while the `subscribe` message is handled. A
non-participant is now refused at subscribe time instead of receiving a stream that silently
never delivers.

Covered by `backend/src/app/tests/test_public_chat_websocket.py` (4 tests) over the real
`graphql-transport-ws` transport.

### D3 — Admin wishlist: five fields the backend never had

`frontend/services/api/admin.api.ts` queried
`wishlistOverview { itemCount wishlistCount productCount potentialRevenue }` and
`topWishlistProducts { ... price }`, but `WishlistOverviewType` exposes only
`total_wishlists` / `total_items` and `TopWishlistProductType` has no `price`. The admin
wishlist page would have failed at runtime. Found by validating every frontend GraphQL
document against the assembled Strawberry schemas.

Resolved in favour of the backend, which is the implemented contract and matches
`test_admin_wishlist.py`: the frontend now queries `totalWishlists` / `totalItems`, and `price`
was added to the backend type, resolver and repository because the page genuinely renders a
Price column and derives potential revenue from it.

### D4 — Admin wishlist `wishlistCount` was always 0

`resolve_top_wishlist_products` read `row.get("wishlist_count", 0)` while
`WishlistRepository.top_products` returns the key as `"count"`, so the default silently won on
every row. The existing test only asserted `productName`, which is why it was never caught.
Fixed to read `count`, and `test_admin_wishlist.py` now asserts both the count and the price.

### D5 — Cart was not re-read after a client-side sign-in

`StoreBootstrap` re-read the backend cart only when `auth.isReady` flipped, which happens once
when `/auth/me` settles. A sign-in afterwards never re-flips it, so the store kept showing the
guest cart while the backend resolved the customer's cart — the intent stated in the code
comment was not met. `isAuthenticated` is now a dependency of the same effect, covering both
sign-in and sign-out. Covered by a new case in `frontend/app/providers.test.tsx`, verified to
fail when the dependency is removed.

---

## 4. Verification performed

| Check | Command | Result |
| --- | --- | --- |
| Backend suite | `pytest src/app/tests -q -p no:randomly` | **272 passed**, 0 failed |
| Frontend suite | `npx jest` | **78 suites / 175 tests** passed |
| Types | `npx tsc --noEmit` | exit 0 |
| Production build | `npx next build` | exit 0, 42 static pages |
| Lint | `npx eslint` | 3 errors, 62 warnings — all pre-existing, see below |
| GraphQL contracts | `python -m src.app.tests.check_frontend_graphql_contracts` | **89 documents validated, 0 invalid** |
| WebSocket chat | `pytest src/app/tests/test_public_chat_websocket.py` | 4 passed |
| Byte-compile | `python -m compileall -q src/app` | exit 0 |

`backend/src/app/tests/check_frontend_graphql_contracts.py` is a new integration check: it
extracts every GraphQL document the frontend actually sends (resolving `${FIELD_FRAGMENT}`
interpolations), routes each to the public or admin schema, and validates it. It caught D3.

---

## 5. Pre-existing issues (not introduced by any agent, left unchanged)

- **3 ESLint errors** in `frontend/app/admin/components/AdminChatPage.tsx`
  (`react-hooks/set-state-in-effect`). The file is unmodified at `e60a243`, so these predate
  the integration work. Fixing them means restructuring untouched admin code, which is outside
  this scope.
- **Chat test flakiness.** 6 failures were observed across 2 early runs, with
  `PermissionDeniedError: Authentication required` and `NotFoundError: Conversation not found`.
  They did not reproduce in 7 subsequent runs (6 targeted + 2 full suites, all green). The
  plausible mechanism is the tie-break weakness Agent C recorded as H1/C3:
  `TimestampMixin` uses `server_default=func.now()` with 1-second resolution, while
  `chat_repository.py:41`, `:136` and `:162` order by `updated_at` / `created_at` with no
  tie-breaker, so equal-timestamp rows can be returned in any order. Fixing it means changing
  timestamp behaviour for every model, which is a separate decision.
- **Product static fallback.** `frontend/app/(public)/products/[slug]/page.tsx` falls back to
  the `storefront-data` demo array when the backend call fails. This is deliberate per
  `bug-view-product.md`, and the backend remains the source of truth whenever it responds, but
  it does mean an unreachable backend shows demo data rather than an error. Flagged for a
  product decision rather than changed unilaterally.

## 6. Not covered

- Live Google OAuth against a real Google account (no credentials or browser available).
- Browser click-through E2E, console/network inspection, and refresh/back-forward checks.
- Running the server and applying migrations against a live database. No model changed, so no
  migration is expected to be missing, but `alembic upgrade` was not executed.
