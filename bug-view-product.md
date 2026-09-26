# BUG INVESTIGATION — Product View · Cart Persistence · Authorization Flow

**Status:** Investigation complete. No fix implemented yet (section 19 is the approved change set).
**Date:** 2026-09-25
**Stack verified from code:** Next.js `16.3.2` App Router (no `pages/` dir), React `19.2.8`, TypeScript `strict: true`; FastAPI + Strawberry GraphQL (no REST product/cart route). CORS `allow_credentials: true`, origins `localhost:3000` / `127.0.0.1:3000` / `192.168.1.34:3000` (`backend/src/app/main.py:19-29`).

---

## 0. Method

Every statement below was read out of the repository or measured against the live database.
Nothing is inferred. Where a prior claim in this file could not be reproduced it was corrected.

Baseline verification commands run **before** any change (recorded so post-change results are comparable):

```
cd frontend && npx tsc --noEmit   -> 6 pre-existing errors (chat context, AdminChatPage, chat.socket)
cd frontend && npx eslint         -> 3 pre-existing errors (all AdminChatPage.tsx)
cd frontend && npx jest           -> 2 failed suites / 118 passed (both chat suites)
```

All 6 type errors, all 3 lint errors and both failing suites are in `context/ChatContext`,
`components/chat/*`, `services/websocket/chat.socket.ts` and `app/admin/components/AdminChatPage.tsx`.
**None of them are in the product / cart / auth / navbar surface.** They are recorded as baseline
and are explicitly **out of scope** for this task.

---

## 1. Architecture as it actually exists

### 1.1 There is no `public` frontend folder

The task brief asks to inspect a `public` folder. **It does not exist on the frontend.** The
public/customer surface is a Next.js **route group**:

| Concern | Location |
|---|---|
| Public storefront pages | `frontend/app/(public)/` |
| Authentication pages | `frontend/app/(auth)/` |
| Customer account pages | `frontend/app/(account)/` |
| Admin pages | `frontend/app/admin/` |
| Backend public API | `backend/src/app/public/` (`api/graphql`, `services`, `repositories`) |
| Backend admin API | `backend/src/app/admin/` |

Route groups do not change URLs, so `(public)/products/page.tsx` **is** `/products`.

### 1.2 Frontend routes

| URL | Route file | Dynamic param |
|---|---|---|
| `/` | `app/(public)/page.tsx` -> `landingPage.tsx` | — |
| `/products` | `app/(public)/products/page.tsx` -> `ProductsPage.tsx` | — |
| `/products/<slug>` | `app/(public)/products/[slug]/page.tsx` -> `ProductDetailPage.tsx` | **`slug`** |
| `/cart` | `app/(public)/cart/page.tsx` | — |
| `/checkout` | `app/(public)/checkout/page.tsx` | — |
| `/wishlist` | `app/(public)/wishlist/page.tsx` | — |
| `/categories/<slug>` | `app/(public)/categories/[slug]/page.tsx` (`PageStub`, no product fetch) | `slug` |
| `/search` | `app/(public)/search/page.tsx` (`PageStub`) | — |
| `/my-account` | `app/(account)/my-account/page.tsx` | — |
| `/my-orders` | `app/(account)/my-orders/page.tsx` | — |
| `/admin/*` | `app/admin/**` | — |

`[slug]` is the **only** dynamic product segment. There is no `[id]`, `[productId]` or `[uuid]`
product route anywhere in the repo, and `useParams()` is never used — the param is read from the
async server-component `params` prop, which is correct for Next 16.

### 1.3 State management (actual, measured)

| Mechanism | Present? | Evidence |
|---|---|---|
| Redux Toolkit | **Yes — the only real store** | `frontend/store/index.ts`, 7 slices: `cart`, `wishlist`, `chat`, `auth`, `checkout`, `subscription`, `connection` |
| React Context | Yes, but chat only | `context/ChatContext/` (plus 6 barrel `index.ts` stubs that export `{}`) |
| Zustand | No | — |
| React Query / TanStack Query | No | — |
| SWR | **Declared as a dependency (`package.json:23`) but imported nowhere** | — |
| `localStorage` | Wishlist only (effective) + a dead cart mirror | `store/index.ts:23-34` |
| `sessionStorage` | No | — |
| Cookies | Written by the **backend** (`guest_token`, `access_token`, `refresh_token`) | `public/context.py:39-41`, `api/auth.py:35-55` |
| Server state / React Server Components | Only `app/(public)/products/[slug]/page.tsx`, and it does not fetch | see §3 |

There is **exactly one** cart system: the `cart` Redux slice. There is **no** second cart
module. (`services/storage/cart-storage.ts` is a 2-line stub returning `{ items: [] }` and is
imported by nothing.)

---

## 2. Backend product-detail endpoint (verified working)

There is **no REST product route**. The whole product surface is Strawberry GraphQL:

- `backend/src/app/main.py:42` — `app.include_router(public_graphql, prefix="/graphql")`
- `backend/src/app/main.py:50` — `app.include_router(admin_graphql, prefix="/admin/graphql")`

Public single-product field — `backend/src/app/public/api/graphql/schema.py:98`

```python
product: ProductType = strawberry.field(resolver=resolve_product)
```

Resolver — `backend/src/app/public/api/graphql/queries/products.py:95-106`

```python
def resolve_product(self, info: Info, id: uuid.UUID | None = None, slug: str | None = None) -> ProductType:
    svc = ProductService(info.context.db)
    if slug:  product = svc.get_by_slug(slug)
    elif id:  product = svc.get(id)
    else:     raise ValidationError("Provide either id or slug")
    return _to_product_type(product)
```

`slug` takes precedence over `id` when both are supplied.

Repository — `backend/src/app/public/repositories/product_repository.py:90-96`

```python
def get_by_slug(self, slug: str) -> Product | None:
    stmt = (select(Product)
            .where(Product.slug == slug,
                   Product.status == ProductStatus.ACTIVE,
                   Product.is_active.is_(True))
            .options(joinedload(Product.images), joinedload(Product.variants)))
    return self._db.scalars(stmt).unique().first()
```

`ProductService.get_by_slug` raises `NotFoundError("Product not found")` when nothing matches
(`backend/src/app/public/services/product_service.py:49-53`). A passing test already covers it:
`backend/src/app/tests/test_public_products.py::test_get_product_by_slug`.

**Conclusion: the backend already exposes exactly the call the frontend needs — `product(slug: String)`. It is simply never called from the public storefront.**

### 2.1 Canonical product identifier

| Layer | Identifier |
|---|---|
| DB primary key | `products.id` — `uuid.UUID`, `UUIDPrimaryKeyMixin` (`models/base.py:15`), stored as `CHAR(32)` hex in SQLite. There is **no `uuid` and no `_id` column.** |
| Unique URL key | `products.slug` — `String(280)`, `nullable=False`, unique index `ix_products_slug` (`models/product.py:22,31`) |
| GraphQL | `ProductType.id: UUID` and `ProductType.slug: str` (`public/api/graphql/types/product.py:34,36`) |
| Frontend route | `slug` — `/products/[slug]` |
| Frontend cart identity | `productId` (`CartItem.product_id`, `CartItemType.product_id`) |

**Canonical rule for this task: the frontend identifies a product by `slug` for navigation and by
`id` (a UUID string) for any backend cart mutation. `product_id` exists only as a GraphQL
variable name; there is no `productId` concept in the product model.** `_id` / `product_id` as a
product identifier appear nowhere in the frontend product flow.

### 2.2 Live database state (read-only query of `backend/poojapoint.db`, 2026-09-25)

9 `products` rows. Only **3** satisfy the public filter `status='active' AND is_active=1`:

| id (PK) | slug | status | is_active | is_featured | stock | category_id | deleted_at |
|---|---|---|---|---|---|---|---|
| `b454f66753414852bcf3e6d688462406` | `sdfg` | active | 1 | 1 | 10 | `07d7a289…` | null |
| `a2ef264a0c6549ed8349ce0b2e20497b` | `sdfgtyyyuuuu` | active | 1 | 1 | 10 | `07d7a289…` | null |
| `7069afe2b66a4fc5a8f70818d19f5d57` | `iouytf` | active | 1 | 1 | 10 | `07d7a289…` | null |
| `0a32a7d3b4e84d36998ee79689fee18a` | `cxzxczcc` | active | 0 | 1 | 10 | `4f5d1d4a…` | set |
| `d70856a996884cdc8cd017a767a41874` | `dddss` | active | 0 | 1 | 10 | `4f5d1d4a…` | set |
| `a6354950689f4b558347bfa1981ac385` | `diya` | out | 0 | 1 | 10 | `4f5d1d4a…` | set |
| `c157f46621574b5bb65e928e6e2cb39a` | `diya-copy-1789558682100` | draft | 0 | 0 | 10 | `4f5d1d4a…` | set |
| `ff6769ebffbd4883b3667b10aecb8b12` | `diya-copy-…-copy-…` | draft | 0 | 0 | 10 | `4f5d1d4a…` | set |
| `771234397a35416eb9d2fdbc58bf0e53` | `fghjj` | active | 0 | 0 | 10 | `07d7a289…` | set |

`cart_items`: **0 rows**. `carts`: 14 rows, **all 14 with a non-null `guest_token_hash`**.
`users`: 22 rows, of which **3 have `is_guest=1`** — i.e. `require_user_or_guest` really has run
in this app and really has persisted guest carts.

**None of the 8 mock slugs in `app/(public)/storefront-data.ts:23-32`
(`premium-brass-pooja-diya`, `elegant-ganesha-idol`, …) exist in the database.**

---

## 3. Bug 1 — Product Details never reaches the backend (all 3 flows)

### 3.1 Trace: Homepage -> Product Details

```
app/(public)/page.tsx:13                <Homepage />
  landingPage.tsx:231                   productsApi.featured({ page: 1, pageSize: 8 })
    products.api.ts:28                  -> productsApi.list({ isFeatured: true })
      client.ts:112-146                 POST {apiUrl}/graphql  { credentials: "include" }
        backend                         products(isFeatured: true) -> Page[ProductType]
  landingPage.tsx:246-257               map CatalogProduct -> storefront Product { id, slug, ... }
  landingPage.tsx:257 / 260             setFeaturedProducts(mapped)  |  setFeaturedProducts(products)  <-- MOCK FALLBACK
  landingPage.tsx -> ProductsSection -> ProductGrid.tsx:56
                                      <Link href={`/products/${product.slug}`}>   <-- correct URL
  ------------------------------------------------------------------------------------
  app/(public)/products/[slug]/page.tsx:9    const { slug } = await params;
  app/(public)/products/[slug]/page.tsx:23   const product = products.find(i => i.slug === slug)  <-- MOCK ARRAY
  app/(public)/products/[slug]/page.tsx:24   if (!product) notFound();                            <-- 404
```

**No HTTP request is made anywhere on the product-detail route.** `products` is a module-level
8-element literal (`app/(public)/storefront-data.ts:23-32`), so the resolution is a synchronous
`Array.find`.

### 3.2 Trace: Products -> Product Details

```
app/(public)/products/page.tsx:16       <ProductsListingPage />
  ProductsPage.tsx:69                   productsApi.list({ page: 1, pageSize: 100 })  -> POST /graphql
  ProductsPage.tsx:71-81                map -> storefront Product (slug: item.slug)
  ProductsPage.tsx:82 / 85              setRequestState("success") | setCatalog(products)  <-- MOCK FALLBACK
  ProductsPage.tsx:190                  <Link href={`/products/${product.slug}`}>
  ------------------------------------------------------------------------------------
  app/(public)/products/[slug]/page.tsx:23-24   same MOCK lookup -> notFound()
```

### 3.3 Trace: Cart -> Product Details

```
app/providers.tsx:100                   cartApi.get() -> POST /graphql  cart { items { ... product { id name slug price images } } }
  providers.tsx:110                     slug: item.product?.slug ?? item.id     <-- may be a CartItem UUID
  store.dispatch(hydrateCart(items))
  app/(public)/cart/page.tsx:106        <Link href={`/products/${item.slug}`}>
  app/(public)/cart/page.tsx:116        <Link href={`/products/${item.slug}`}>
  ------------------------------------------------------------------------------------
  app/(public)/products/[slug]/page.tsx:23-24   same MOCK lookup -> notFound()
```

### 3.4 Evidence — Product View

```
File:              frontend/app/(public)/products/[slug]/page.tsx
Component:         ProductPage (Next.js server component) + generateMetadata
Function:          default export (21-37), generateMetadata (8-19)
Current behavior:  products.find(item => item.slug === slug) against the 8-item hardcoded
                   array in storefront-data.ts:23-32; notFound() on any miss (lines 10, 23, 24).
                   Zero network requests. All 3 real slugs (sdfg, sdfgtyyyuuuu, iouytf) -> 404.
Expected behavior:  POST /graphql { product(slug: $slug) { ... } }, render it, and call
                   notFound() only when the backend has no such product.
Actual API request: NONE. There is no fetch() on this route.
Actual API response: n/a.
Root cause:         The route is bound to a static mock array instead of the products API. The
                   child it renders (ProductDetailPage.tsx:14 `type ProductDetailPageProps = {
                   product: Product }`) only accepts a prop, so nothing downstream can fetch either.
Affected pages:    /products/<slug> reached from Homepage, Products, Cart, Wishlist,
                   search suggestions, related products and the sitemap.
Severity:          BLOCKER — 100% of real product-detail traffic 404s.
Recommended fix:   Add productsApi.bySlug() and call it in both the page and generateMetadata.
```

```
File:              frontend/services/api/products.api.ts
Component:         productsApi
Function:          object literal, lines 18-29
Current behavior:  Only list() and featured() exist. Nothing in the repository can fetch a
                   single product.
Expected behavior:  bySlug(slug) -> graphqlClient<{ product: CatalogProductDetail }>
Root cause:        The single-product client function was never written. The backend resolver
                   resolve_product (queries/products.py:95-106) already supports slug and is
                   proven by the passing test test_get_product_by_slug.
Actual API request: n/a (function does not exist)
Actual API response: n/a
Affected pages:    All three product-view flows.
Severity:          BLOCKER (missing capability)
Recommended fix:   Add bySlug() reusing graphqlClient and its existing error handling.
```

```
File:              frontend/app/providers.tsx
Component:         Providers
Function:          cart hydration useEffect
Line:              110
Current behavior:  slug: item.product?.slug ?? item.id
Expected behavior:  A genuine product slug in `slug`; never a CartItem UUID.
Root cause:        Identifier-namespace collapse. CartApiItem.product is nullable
                   (services/api/cart.api.ts:8-14), so a null nested product stores a CartItem
                   UUID in the slug field, and cart/page.tsx:106/116 builds
                   /products/<cart-line-uuid>.
Actual API request: POST /graphql { cart { items { id productId quantity unitPrice
                             product { id name slug price images { url isPrimary } } } } }
Actual API response: cart.items[].product is null whenever the product row is missing /
                     soft-deleted / inactive, because the backend only populates it from
                     `item.product` (public/api/graphql/mutations/cart.py:72).
Affected pages:    Cart -> Product Details (only when the nested product is null).
Severity:          HIGH
Recommended fix:   Keep the product id in `id`, carry the real slug only when present, and
                   never fall back to the cart-line id.
```

```
File:              frontend/app/(public)/products/ProductsPage.tsx
                    frontend/app/(public)/landingPage.tsx
Component:         ProductsPage / Storefront (homepage)
Function:          catalog loaders (ProductsPage.tsx:67-89, landingPage.tsx:227-295)
Current behavior:  On API rejection — or on a *successful but empty* featured result — the
                   pages substitute the 8 mock products (ProductsPage.tsx:85,
                   landingPage.tsx:260, landingPage.tsx:287). Those mock cards link to
                   /products/premium-brass-pooja-diya etc., slugs that exist in neither the
                   mock detail lookup nor the database, so "View product" 404s with no error shown.
Expected behavior:  A successful-but-empty response is an empty state, never a fallback trigger
                   (this is already the project's documented rule — frontend/frontend-data-plan.md:46).
Root cause:         Silent mock substitution hides the upstream failure; cards render, so the
                   listing page looks healthy and the failure only appears after the click.
Affected pages:    Homepage, Products.
Severity:          MEDIUM (it is what makes Bug 1 look intermittent)
Recommended fix:   Resolve the detail route against the backend FIRST and only then the demo
                   array, so no card can ever link to an unresolvable slug. Do not delete the
                   documented demo fallback.
```

### 3.5 Findings that are NOT the cause (checked, not assumed)

- **Wrong route name / wrong param** — `[slug]` and `params.slug` are consistent in all 6 card copies.
- **Wrong UUID format** — no UUID ever reaches the detail route; `ProductType.id` is `UUID!`.
- **Wrong slug produced by a card** — Homepage, Products, Cart and Wishlist all send the real
  `product.slug` from the API when the API succeeds.
- **Duplicate product-detail routes** — there is exactly one, `app/(public)/products/[slug]/`.
  (The *card* markup is duplicated 6 times — `ProductsPage.tsx:190`, `ProductGrid.tsx:45-71`,
  `RecommendationsCarousel.tsx:44-70`, `ProductDetailPage.tsx:100`, `wishlist/page.tsx:63-66`,
  `cart/page.tsx:105-155` — but every copy builds the same href.)
- **`ProductCard.tsx` / `CartItem.tsx`** — both are 1-line stubs rendering no link, so they are
  not the failure point.
- **Backend filter mismatch** — `get_by_slug` does not filter `deleted_at` while
  `admin/repositories/product_repository.py:37` does. Real but not causal (the 3 visible products
  are not soft-deleted). Recorded as an observation, **not** a fix target.
- **Dead/duplicate identifiers that hide the mismatch** — `types/product.ts:1` has no `slug` and is
  imported by nothing; `app/sitemap.ts:7` advertises the 8 mock URLs; `landingPage.tsx:24-195` is a
  172-line commented-out duplicate catalog.

---

## 4. Bug 2 — Cart does not persist across navigation or refresh

### 4.1 The complete current data flow (traced end to end)

```
Product Card "Add to Cart"
  landingPage.tsx:508/525 | ProductsPage.tsx:143 | ProductDetailPage.tsx:63
  cart/page.tsx:43 | wishlist/page.tsx:40 | my-orders/page.tsx:65
        |
        v
useCart().addItem(product, quantity)                      hooks/useCart.ts:16
        |  dispatch(addItem({ product, quantity }))        <-- END OF THE LINE
        v                                                   NO HTTP CALL
Redux  cartSlice.items                                       store/slices/cartSlice.ts:16-25
        |
        +--> store.subscribe -> localStorage["poojapoint-cart"]   store/index.ts:29-32
        |
        X   (never reaches the backend)
```

Reading side, on **every** app mount (`app/providers.tsx:91-124`):

```
1. localStorage["poojapoint-cart"]  -> store.dispatch(hydrateCart(JSON.parse(saved)))   line 95-96
2. cartApi.get()  -> POST /graphql { cart { ... } }                                     line 100
3. store.dispatch(hydrateCart(itemsFromBackend))      <-- UNCONDITIONAL OVERWRITE       line 114
```

Because **nothing ever writes to the backend cart**, step 2 always returns
`{ items: [], itemCount: 0 }` and step 3 therefore always wipes whatever localStorage restored in
step 1.

### 4.2 The backend cart is fully built, fully tested, and completely unused

`cartApi` (`services/api/cart.api.ts`) implements `get`, `add`, `update`, `remove`, `clear`.
A repo-wide search for `cartApi.` returns **exactly one call site**: `app/providers.tsx:100`
(`cartApi.get()`). `add`, `update`, `remove` and `clear` are **dead code**.

The backend side is complete and covered by `backend/src/app/tests/test_public_cart.py`
(guest cart creation, add, insufficient stock, update, remove, clear — all passing).

### 4.3 What mechanism identifies a cart (measured, not assumed)

| Layer | Mechanism | Evidence |
|---|---|---|
| Guest identity | **`guest_token` cookie** — `secrets.token_urlsafe(32)`, `httponly`, `samesite=lax`, `path=/`, `max_age=30d` | `public/context.py:39-41` |
| Cart lookup for a guest | `hash_token(cookie)` -> `Cart.guest_token_hash` | `public/context.py:57-58` |
| Cart row for a first-time guest | creates a `User(is_guest=True, role_name=customer)` **and** a `Cart(user_id, guest_token_hash)` | `public/context.py:63-79` |
| Cart lookup for a logged-in user | `Cart.user_id == user.id` | `public/repositories/cart_repository.py:24-25` |
| Authenticated identity | `Authorization: Bearer <jwt>` **and/or** the `access_token` cookie | `public/dependencies.py:26-40`, `api/auth.py:63-70` |
| Persistence | **SQLite table `carts` / `cart_items`** (no Redis, no session store) | `models/cart.py`, `models/cart_item.py`; live DB has 14 `carts` rows, all guest-keyed |
| Frontend transport | `graphqlClient` always sends `credentials: "include"` | `services/api/client.ts:130` |

So: **guest cart = `guest_token` HTTP-only cookie -> `hash_token` -> `carts.guest_token_hash` ->
`carts` row -> `cart_items` rows.** It is stable across pages and across refreshes, and the cookie
is 30 days long. The identifier is sound. **The frontend simply never uses it for writes.**

### 4.4 Why the user sees "navigate away and the cart is empty"

Two independent mechanisms, both measured:

**(a) The backend response overwrites local state on every mount.** `providers.tsx:114`
dispatches `hydrateCart` from the server response unconditionally. Since the server cart is
permanently empty (nothing writes to it), **every full page load empties the cart**. This is why
the symptom is intermittent in dev (client-side `<Link>` navigation keeps the store alive) and
reproducible in production / on refresh.

**(b) The navbar performs full document navigations, not client-side ones.**
`components/layout/PublicHeader/CategoryNav.tsx:52-56` renders

```tsx
<a href={item.href} key={item.label}>{item.label}</a>
```

Raw `<a href>` performs a **full document load**. The entire React tree — including `Providers`
and the Redux store — is destroyed and rebuilt, which guarantees mechanism (a) runs.
`PublicFooter.tsx:24,28` has the same pattern (`<a href="#products">`, `<a href="#support">`), and
`PublicHeader`'s search suggestions use `<a href={/products/${product.slug}}>`
(`SearchBar.tsx:32`). `MobileBottomNav` correctly uses `next/link`.

So the reported sequence is exact:

```
Add to cart            -> Redux + localStorage populated, backend cart still empty
Home / Shop / Categories click  (CategoryNav <a href>) -> FULL RELOAD
   -> providers.tsx:95  localStorage hydrate  (1 item, correct)
   -> providers.tsx:100 cartApi.get()         (0 items, backend truth)
   -> providers.tsx:114 hydrateCart([])       -> CART EMPTY
Return to Cart         -> empty
```

### 4.5 Evidence — Cart Persistence

```
File:              frontend/hooks/useCart.ts
Component:         useCart
Function:          addItem (16), removeItem (18), updateQuantity (19), clearCart (20)
Current behavior:  Each is a one-line dispatch of a pure Redux action. No cartApi call.
Expected behavior:  Add must persist via addToCart; update via updateCartItem; remove via
                   removeCartItem; clear via clearCart — then the response becomes the state.
Actual API request: NONE for add / update / remove / clear.
Actual API response: n/a
Root cause:        The four existing cart mutations in services/api/cart.api.ts are never called,
                   so the backend cart is permanently empty while the UI keeps a parallel
                   client-only cart. Providers then treats the empty backend response as truth.
Affected pages:    /, /products, /products/<slug>, /wishlist, /cart, /my-orders, /checkout.
Severity:          BLOCKER
Recommended fix:   Wire useCart to the existing cartApi. Do NOT add a second cart API.
```

```
File:              frontend/app/providers.tsx
Component:         Providers
Function:          cart bootstrap useEffect (91-124), line 114
Current behavior:  store.dispatch(hydrateCart(itemsFromBackend)) runs unconditionally on every
                   mount and silently discards the localStorage cart.
Expected behavior:  The backend cart is the source of truth and is the only cart. Local state
                   must never be overwritten by an empty response that was produced by a write
                   path that does not exist yet — after the useCart fix the two agree by
                   construction.
Root cause:        Read path and write path are not connected, so the read path always wins.
Actual API request: POST /graphql { cart { id itemCount subtotal items { ... } } }
Actual API response: { "cart": { "itemCount": 0, "items": [] } } — because no mutation has
                   ever been issued for this visitor.
Affected pages:    Every page; the cart count badge in PublicHeader and the cart page body.
Severity:          BLOCKER
Recommended fix:   Drop the localStorage cart mirror (the project's own
                   frontend-data-plan.md:13 says localStorage must not replace backend state),
                   keep the single cartApi.get() hydrate, and add an in-flight guard so the
                   response cannot clobber a cart mutated while the request was open.
```

```
File:              frontend/components/layout/PublicHeader/CategoryNav.tsx
Component:         CategoryNav
Function:          CategoryNav render, lines 52-56
Current behavior:  <a href={item.href}> — a full document navigation that tears down Providers
                   and the Redux store on every navbar click.
Expected behavior:  Client-side navigation (next/link), like every other in-app link in the repo.
Root cause:        Raw anchors were used instead of next/link.
Affected pages:    The whole navbar; it is the direct amplifier of the cart-loss symptom.
Severity:          HIGH
Recommended fix:   Render with <Link href>. The existing `.category-nav a` CSS applies to
                   next/link anchors, so this needs NO CSS change.
```

### 4.6 Cart count

`HeaderActions.tsx:33-36` renders `<span className="badge">{cartCount}</span>` where `cartCount`
comes from `useCart().count` -> `selectCartCount` (`cartSlice.ts:47-49`, sums `quantity`).

- **In-session:** correct — it is driven by the same Redux slice the cart page renders.
- **After any full page load:** resets to 0, because the store is rebuilt and then overwritten
  with the empty backend cart (§4.4). Same root cause as the cart body.
- Backend `cart { itemCount }` is computed the same way (`queries/cart.py:78`), so the two agree
  by construction once writes are wired.

**`HeaderActions` is a `"use client"` component, and the cart count flows from the single Redux
store — no per-page duplication, no second count source. This part is architecturally correct.**

---

## 5. Cart API inventory (actual project endpoints)

There is **no REST `/cart*` route in the backend.** Everything is one GraphQL document per
operation, all on the public router mounted at `/graphql` with optional auth.

| # | Endpoint | Method | Auth | Guest | Request | Response | Cart identifier | Used by |
|---|---|---|---|---|---|---|---|---|
| 1 | `/graphql` — `query Cart` | POST | none required | yes | none | `Cart!` — `id, itemCount, subtotal, items { id productId variantId quantity unitPrice product {…} }` | `guest_token` cookie, else `user_id` from Bearer | **only** `app/providers.tsx:100` |
| 2 | `/graphql` — `mutation AddToCart` | POST | none required | yes | `productId: UUID!`, `quantity: Int!`, `variantId: UUID` | `Cart!` | same | **NOBODY** (dead code) |
| 3 | `/graphql` — `mutation UpdateCartItem` | POST | none required | yes | `itemId: UUID!`, `quantity: Int!` | `Cart!` | same | **NOBODY** (dead code) |
| 4 | `/graphql` — `mutation RemoveCartItem` | POST | none required | yes | `itemId: UUID!` | `Cart!` | same | **NOBODY** (dead code) |
| 5 | `/graphql` — `mutation ClearCart` | POST | none required | yes | none | `Cart!` | same | **NOBODY** (dead code) |

Client wrappers: `frontend/services/api/cart.api.ts` — `cartApi.get/add/update/remove/clear`
(lines 27, 49, 65, 81, 97). Resolvers: `public/api/graphql/queries/cart.py:83` and
`public/api/graphql/mutations/cart.py:84,97,104,111`. Wiring: `schema.py:111` (query) and
`schema.py:167-170` (four mutations).

**Naming note:** the operations are `cart`, `addToCart`, `updateCartItem`, `removeCartItem`,
`clearCart` — Strawberry camelCases the snake_case Python arguments. There is no
`/cart/items`, `/cart/add`, `/cart/count` or `/cart/update` in this project. The count is
`cart { itemCount }` on the `cart` query, not a separate endpoint.

### 5.1 Two identifier gaps in the current write path (must be solved by the fix)

1. `addToCart` needs a **product UUID** (`productId`). The cards carry `product.id` — a real
   UUID for backend products, but a non-UUID string such as `"diya"` / `"lotus-diyas"` for the
   8 demo products and for `landingPage.tsx:510` (`sub-${plan}-${Date.now()}`) and the
   Pay-As-You-Go lines (`landingPage.tsx:525-538`). Those mutations will fail at GraphQL
   variable coercion. This must degrade gracefully, not crash.
2. `updateCartItem` / `removeCartItem` need a **CartItem UUID**, not a product id. The Redux
   `CartItem` type (`types/cart.ts:12`) stores only `id` (= product id). The cart-line id is
   present in the API response (`CartApiItem.id`) but is **thrown away** by
   `providers.tsx:102-113`, which never reads `item.id` into the Redux item. So today the
   frontend physically cannot call operations 3 and 4.

---

## 6. Guest -> login transition

### 6.1 Current behaviour (measured from code)

**Guest-cart merging is NOT supported anywhere.**

- `AuthService.login` (`public/services/auth_service.py:72-82`) only validates credentials and
  calls `_issue_tokens`. It never touches `Cart` or `Cart.guest_token_hash`.
- `POST /auth/login` (`api/auth.py:85-93`) only sets the `access_token` / `refresh_token` cookies.
- `GET /auth/me` (`api/auth.py:125-135`) only reads the token.
- `require_user_or_guest` (`public/context.py:52-80`) returns `ctx.user` the moment a valid
  Bearer token is present, and never merges the `guest_token_hash` cart.
- GraphQL `mutate_login` / `mutate_signup` (`public/api/graphql/mutations/auth.py`) are the same
  story.

Therefore, on login:

```
Guest adds 2 items  ->  cart R1 (guest_token_hash = H, user_id = guest user G)
User logs in         ->  auth cookies set; no merge; R1 untouched
Next cart request    ->  require_user_or_guest returns the real customer U
                       CartService.get -> get_by_user(U.id) -> None -> creates cart R2
                       CART IS EMPTY. The 2 guest items are orphaned on R1/G.
```

On logout the same happens in reverse: `access_token`/`refresh_token` are deleted
(`api/auth.py:58-60`) but `guest_token` is **not**, so the guest cart R1 becomes visible again.
`logout` also never clears the Redux cart, so the UI keeps showing the customer's items until the
next mount overwrites them.

### 6.2 Required architecture for a merge (documented, not invented)

To support `Guest Cart -> Authenticated Cart` with the **existing** schema (no new tables, no new
API), the merge is a single ownership transfer on the token-issuing path:

```
on login / signup / google_login, before issuing tokens:
    token_hash = hash_token(guest_token cookie)
    guest_cart = SELECT * FROM carts WHERE guest_token_hash = token_hash
    if guest_cart and guest_cart.user_id != user.id:
        target = SELECT * FROM carts WHERE user_id = user.id
        if target is None:
            guest_cart.user_id = user.id            # adopt the guest cart in place
        else:
            for item in guest_cart.items:           # merge lines
                upsert into target by (product_id, variant_id), summing quantity
            delete guest_cart
        (optionally mark the guest User row merged/disabled)
```

`carts.user_id` and `cart_items.cart_id` already exist and already support this; no migration is
required. The frontend then needs no change beyond a cart re-read after login, because the cart
identifier becomes the stable user id.

**This is a real behaviour change and is therefore NOT in the minimum fix set.** It is documented
here and listed in §19 as a separately-approved item.

---

## 7. Authorization, navbar visibility and admin

### 7.1 Auth state

`store/slices/authSlice.ts` holds `user`, `isAuthenticated`, `isReady`, `accessTokenExpiresAt`,
`sessionExpired`. `app/providers.tsx:43-73` (`AuthBootstrap`) calls `authApi.me()` once on mount
and dispatches `setUser`; on failure it dispatches `setSessionExpired()` + `logout()`. So
`isAuthenticated` correctly reflects the server, and `isReady` prevents the nav from flickering on
"logged out" before `me()` resolves.

### 7.2 Route protection (already correct — do not touch)

| Guard | File | Rule |
|---|---|---|
| Account routes | `app/(account)/layout.tsx:10-16` | `!isAuthenticated \|\| role !== "customer"` -> redirect to `/admin` when role is `admin`, else `/`; renders `null` otherwise |
| Admin routes | `app/admin/layout.tsx:11-15` | `!isAuthenticated \|\| role !== "admin"` -> redirect `/`; renders `null` otherwise |

Role separation is strict and correct: `admin` is **never** treated as `customer`, and an admin
landing on `/my-account` is redirected to `/admin`. The profile button honours the same split
(`HeaderActions.tsx:19-23`): admin -> `/admin`, customer -> `/my-account`, guest -> `/login`.

**This satisfies the "do not accidentally treat admin as customer" and "preserve the existing admin
redirect" requirements with no change.**

### 7.3 The navbar authorization defect

`components/layout/PublicHeader/PublicHeader.tsx:20-31` renders exactly three regions:

```tsx
<div className="top-bar">…</div>
<header className="navbar"><Logo /> <SearchBar /> <HeaderActions /></header>
<CategoryNav />
```

**Neither `My Account` nor `My Orders` exists anywhere in the public navigation.**
A repo-wide search for `My Account` / `My Orders` finds them only in
`app/(account)/my-account/page.tsx:112` — the sidebar of the account page itself, which is behind
the `AccountLayout` guard.

So the current state is:

| User | `My Account` / `My Orders` in navbar | Correct? |
|---|---|---|
| Unauthorized | absent | yes (accidentally correct) |
| Customer | **absent** | **NO — requirement not met** |
| Admin | absent | yes |

`HeaderActions` already has everything needed: it is `"use client"`, already calls
`useAuth()` (`HeaderActions.tsx:5,17`) and already branches on `user?.role_name === "admin"` /
`"customer"`. The auth state is available; only the links are missing.

**Where they must go, without touching CSS:** the horizontal nav row is
`.category-nav` (`globals.css:90-95`), and its only rule is `.category-nav a` — a plain anchor
with hover underline. `next/link` renders an `<a>`, so appending
`<Link href="/my-account">My Account</Link>` and `<Link href="/my-orders">My Orders</Link>` to
`CategoryNav` inherits the existing styling exactly. That satisfies "navbar shows Home / Shop /
Categories / Cart / …" plus the two account links, with **zero CSS edits**.

### 7.4 Evidence — Authorization / Navbar

```
File:              frontend/components/layout/PublicHeader/PublicHeader.tsx
Component:         PublicHeader
Function:          PublicHeader (20-31)
Current behavior:  Renders TopBar + navbar(Logo, SearchBar, HeaderActions) + CategoryNav.
                   No My Account and no My Orders link exists for ANY user.
Expected behavior:  Authenticated customers see "My Account" -> /my-account and
                   "My Orders" -> /my-orders in the navbar. Unauthorized users and admins do not.
Actual API request: n/a (static nav)
Actual API response: n/a
Root cause:        The account links were never added to the public header, even though
                   HeaderActions already reads useAuth() and the (account) routes already exist
                   and are already guarded.
Affected pages:    Every public page (PublicHeader is rendered by /, /products, /products/[slug],
                   /cart, /checkout, /wishlist, /categories/*, /search, /my-account, /my-orders,
                   /order/*, not-found, 503, timeout, and the (auth) pages).
Severity:          HIGH (requirement 3.2 unmet)
Recommended fix:   Render both links in CategoryNav gated on
                   isAuthenticated && user.role_name === "customer". No CSS change.
```

### 7.5 Public purchase is already supported by the backend — must not be restricted

| Operation | Resolver | Auth used | Guest allowed |
|---|---|---|---|
| `query cart` | `queries/cart.py:83` | `require_user_or_guest` | **yes** |
| `mutation addToCart` | `mutations/cart.py:84` | `require_user_or_guest` | **yes** |
| `mutation checkout` | `mutations/checkout.py:68-104` | `require_user_or_guest` | **yes** |
| `query products` / `product` | `queries/products.py:63,95` | no auth at all | **yes** |
| `query categories` / `category` | `queries/categories.py:30,36` | no auth at all | **yes** |
| `query currentUser` | `queries/profile.py` | `require_user` | no |
| `query orders` / `mutation cancelOrder` | `queries/orders.py`, `mutations/orders.py` | `require_user` | no (correct — order history) |
| `query wishlist` / `mutate addToWishlist` | `queries/wishlist.py`, `mutations/wishlist.py` | `require_user` | no |

`get_optional_current_user` (`public/dependencies.py:26-40`) uses
`HTTPBearer(auto_error=False)` and returns `None` when absent — **no public endpoint demands a
token.** The existing business flow is: browse -> add to cart -> checkout as a guest, with an
order record attached to a generated guest user. The frontend checkout page
(`app/(public)/checkout/page.tsx`) collects a shipping address inline and calls `checkoutApi`
without any auth, consistent with that.

**No authentication is to be added to any of these.** The fix set in §19 touches none of them.

---

## 8. Flow comparison (actual findings)

| Flow | Authentication | Product View | Add Cart | Navigate Away | Return Cart | Status |
|---|---|---|---|---|---|---|
| Public User | Unauthorized | `/products/sdfg` etc. -> **HTTP 404** (mock-array lookup, no API call). All 8 demo cards also 404. | Works **on screen only** — Redux + localStorage. Backend cart stays empty (`cart_items` = 0 rows in the live DB). | Navbar `<a href>` = full reload; `providers.tsx:114` overwrites with the empty backend cart. | **Cart empty, count 0.** | **BUG** (product view + cart persistence) |
| Customer | Authorized | Identical to public — the detail route has no auth branch, so it fails the same way. | Same as public: never persisted to the backend. On login a **brand-new** cart is created (§6.1), so the customer's own cart is empty too. | Same full-reload wipe; plus, because `CartService` looks the cart up by `user_id` while the writes went nowhere, the empty response is consistent. | **Cart empty, count 0.** | **BUG** (product view + cart persistence + no guest merge) |
| Admin | Admin | Same 404 (the route is role-agnostic). Browsing works via the navbar. | Same: client-only. `HeaderActions.tsx:20` sends admins to `/admin`, and `admin/layout.tsx` correctly blocks non-admins. | Same wipe. | Empty. | **BUG** (product view + cart persistence). **Admin routing itself is correct and untouched.** |

Reference: `app/(account)/layout.tsx` and `app/admin/layout.tsx` role routing, `/auth/me` session
restore, and `HeaderActions` role branching all behave as specified.

---

## 9. Product view comparison (actual findings)

| Page | Product Identifier | Route | Product API | Status |
|---|---|---|---|---|
| Homepage `/` | `product.slug` from `productsApi.featured` — real slugs `sdfg` / `sdfgtyyyuuuu` / `iouytf` (`landingPage.tsx:254`); on rejection or an empty result, mock slugs (`landingPage.tsx:260`, `:287`) | `/products/${product.slug}` built at `ProductGrid.tsx:56` | List: `POST /graphql { products(page,pageSize,isFeatured) }` (`products.api.ts:19-26`). **Detail: no request at all.** | **BUG** |
| Products `/products` | `product.slug` from `productsApi.list` — real slugs (`ProductsPage.tsx:79`); on rejection, mock slugs (`ProductsPage.tsx:85`) | `/products/${product.slug}` built at `ProductsPage.tsx:190` | List: `POST /graphql { products(page,pageSize) }`. **Detail: no request at all.** | **BUG** |
| Cart `/cart` | `item.slug` from `providers.tsx:110` — a real slug, **or a CartItem UUID when `item.product` is null** | `/products/${item.slug}` built at `cart/page.tsx:106` and `cart/page.tsx:116` | Cart read: `POST /graphql { cart { items { … product { … } } } }`. **Detail: no request at all.** | **BUG** |
| Wishlist `/wishlist` (extra) | `product.slug` — always a mock slug (`wishlist/page.tsx:29,63-66`) | `/products/${product.slug}` | none (mock catalog only) | **BUG** |
| Search suggestions (extra) | `product.slug` — mock slugs (`SearchBar.tsx:32`) | `/products/${product.slug}` | none | **BUG** |

Common to every row: the outgoing URL is built correctly from a real slug; the destination page
never queries the API and therefore 404s.

Identifier resolution that actually happens on the destination page, all flows:

| Layer | Value used |
|---|---|
| Card link | `product.slug` (real when the API succeeded, mock when it did not) |
| Route param | `params.slug` — name is correct (`products/[slug]/page.tsx:9,22`) |
| Resolution performed | `products.find(item => item.slug === slug)` against the 8-item mock array |
| Backend capability available but unused | `product(slug: String) -> ProductType!` via `POST /graphql` |

---

## 10. ROOT CAUSE

### Product View

**The product-detail route is bound to a hardcoded mock array instead of the backend, and the
client has no function that can fetch a single product.**

1. `frontend/app/(public)/products/[slug]/page.tsx` resolves `params.slug` with
   `products.find(item => item.slug === slug)` against the 8-element literal in
   `frontend/app/(public)/storefront-data.ts:23-32` (lines 10 and 23) and calls `notFound()` on a
   miss (line 24). The route performs **no data fetching**; the client component it renders
   (`ProductDetailPage.tsx:14`) only accepts a `product` prop, so nothing downstream can fetch
   either. All three real catalog slugs return HTTP 404.
2. `frontend/services/api/products.api.ts` exposes only `list()` and `featured()`. The correct fix
   has nothing to call. The backend resolver `resolve_product`
   (`backend/src/app/public/api/graphql/queries/products.py:95-106`, wired at
   `schema.py:98`) already accepts `slug` and is proven by the passing
   `test_get_product_by_slug`. The gap is purely frontend.
3. Secondary — identifier-namespace collapse: `frontend/app/providers.tsx:110` writes
   `item.id` (a **CartItem** UUID) into the `slug` field when the nested product is null, producing
   `/products/<cart-line-uuid>`.
4. Contributing — `ProductsPage.tsx:85`, `landingPage.tsx:260` and `landingPage.tsx:287` replace
   real data with the mock catalog on rejection **or on a successful empty response**, so the
   listing pages look healthy while every "View product" click 404s.

### Cart Persistence

**The cart write path does not exist, while the cart read path unconditionally overwrites local
state with the empty backend response on every app mount — and the navbar forces that mount with
full document navigations.**

1. `frontend/hooks/useCart.ts:16-20` — `addItem`, `updateQuantity`, `removeItem` and `clearCart`
   are pure Redux dispatches. `cartApi.add/update/remove/clear`
   (`services/api/cart.api.ts:49,65,81,97`) are **dead code** (the only `cartApi.` call site in the
   repository is `cartApi.get()` at `app/providers.tsx:100`). The backend `carts`/`cart_items`
   tables therefore stay empty — confirmed: `cart_items` has 0 rows.
2. `frontend/app/providers.tsx:114` — on every mount, `hydrateCart(...)` is dispatched from the
   `cartApi.get()` response with no guard, so the always-empty backend response wipes the
   localStorage-restored cart. Race-prone as well: a response that lands after a local mutation
   discards it.
3. `frontend/components/layout/PublicHeader/CategoryNav.tsx:52-56` renders raw
   `<a href={item.href}>`, so **every navbar click is a full document load** that destroys
   `Providers` and the Redux store and re-triggers step 2. `PublicFooter.tsx:24,28` and
   `SearchBar.tsx:32` do the same. This is what turns an intermittent loss into a reproducible
   one.
4. Two structural gaps block the obvious fix and must be closed with it:
   `CartApiItem.id` (the CartItem UUID required by `updateCartItem`/`removeCartItem`) is discarded
   by `providers.tsx:102-113`, and demo/non-catalog products have non-UUID ids, so `addToCart`
   variable coercion will fail for them.

**The cart identifier itself is NOT the problem.** `guest_token` httponly cookie (30 days) ->
`hash_token` -> `carts.guest_token_hash` -> `carts` -> `cart_items`
(`public/context.py:39-41,57-79`) is stable across pages and refreshes, `credentials: "include"`
is already set on every GraphQL call (`services/api/client.ts:130`), CORS allows credentials, and
the live DB shows 14 working guest-keyed carts. Nothing in the identification layer needs to
change.

### Authentication / Authorization

**Route protection and role separation are already correct. The defect is that the public navbar
never renders the account links at all.**

1. `frontend/app/(account)/layout.tsx:10-16` and `frontend/app/admin/layout.tsx:11-15` are strict
   and mutually exclusive: `admin` is never accepted as `customer`, an admin hitting
   `/my-account` is redirected to `/admin`, and unauthenticated users are redirected to `/`.
   `providers.tsx:43-73` restores the session from `/auth/me` and `isReady` prevents nav flicker.
   **Nothing here needs to change.**
2. `frontend/components/layout/PublicHeader/PublicHeader.tsx:20-31` has no `My Account` /
   `My Orders` link for anyone. They exist only in the guarded account sidebar
   (`app/(account)/my-account/page.tsx:112`). So requirement §3.2 (customer sees them) is unmet,
   while §3.1 (guest does not) holds only by accident.
3. `HeaderActions.tsx:5,17,19-23` already reads `useAuth()` and already branches admin vs customer
   vs guest, so the auth state needed for the gate is already in place at the header.
4. **Guest -> login merging is not supported** (§6.1). `AuthService.login` /
   `api/auth.py:login` / `mutate_login` never touch `Cart`, so logging in abandons the guest cart
   on a guest user row and starts an empty customer cart. Logging out leaves `guest_token` intact.
   This is a missing feature, not a regression, and the required architecture is documented in
   §6.2.
5. `logout` in `store/slices/authSlice.ts:23-27` does not clear the cart, so after logout the UI
   briefly shows the previous customer's items until the next mount overwrites them.

### Navbar Visibility

**The two required links are absent from the navbar for every user type; the fix is to add them
gated on `isAuthenticated && role_name === "customer"`, reusing the existing `.category-nav a`
styling so no CSS is touched.**

1. `PublicHeader.tsx:20-31` renders only TopBar, Logo, SearchBar, HeaderActions and CategoryNav.
2. `CategoryNav.tsx:49-57` is the horizontal link row (`.category-nav`, styled by the existing
   `.category-nav a` rule at `globals.css:92`) and currently receives no auth information and
   emits no account links. It is already a `"use client"` component, so `useAuth()` is available
   with no new plumbing.
3. `useAuth()` (`hooks/useAuth.ts`) returns `user`, `isAuthenticated`, `isReady`, `sessionExpired`;
   `types/customer.ts:5` types `role_name` as `"customer" | "admin"`, which is exactly the gate
   needed.

### Explicitly verified as already working — do not "fix"

- Backend public product list + detail resolver, incl. the `slug` branch and its 404 behaviour.
- Backend guest cart identification and the full guest + customer cart GraphQL surface
  (`test_public_cart.py` passes).
- Backend guest checkout (`mutate_checkout` -> `require_user_or_guest`).
- Optional-auth dependency: no public endpoint requires a JWT.
- `(account)` and `admin` route guards, admin-vs-customer separation, admin redirect.
- Session restore via `/auth/me` and `isReady` gating.
- The Redux store is a single instance in the root layout, so client-side navigation already
  preserves cart state and the cart count — the loss is caused by the full-reload path and the
  missing writes, not by store placement.
- `selectCartCount` semantics match the backend's `cart { itemCount }`.

---

## 11. RECOMMENDED FIX

Implementation is **not** authorised by this file. This is the proposed minimum change set.

### Product View

1. Add `productsApi.bySlug(slug)` to `frontend/services/api/products.api.ts`, issuing
   `product(slug: $slug) { id name slug price originalPrice discountPrice averageRating
   reviewCount stock categoryId shortDescription description images { url isPrimary } }` to the
   existing `POST /graphql` via the existing `graphqlClient`, and add a `CatalogProductDetail`
   type. Reuse the existing `ApiError` / `GraphQLError` behaviour in `services/api/client.ts:133-146`;
   do not swallow errors. No new endpoint, no duplicate query.
2. In `frontend/app/(public)/products/[slug]/page.tsx`, replace both `products.find(...)` lookups
   (line 10 in `generateMetadata`, line 23 in the page) with an awaited `productsApi.bySlug(slug)`.
   Keep the `[slug]` param name and the `notFound()` contract, but call `notFound()` **only** when
   the backend reports no product.
3. Resolve in a fixed order — **backend first, demo array second, `notFound()` last** — so a card
   can never link to a slug the route cannot open, while the project's documented demo fallback
   (`frontend-data-plan.md:48-53`) still works when the backend is down. This removes the need to
   touch `ProductsPage.tsx`, `landingPage.tsx` or `app/sitemap.ts` for correctness.
4. `generateMetadata` must stop returning `{}` for products the backend knows about.
5. In `frontend/app/providers.tsx`, stop writing the cart-line id into `slug`. Keep the product id
   in `id`, carry a real slug only when `item.product` is present, and guard `name` the same way.
   This removes the whole `/products/<cart-line-uuid>` class of 404.

### Cart Persistence

6. Wire `frontend/hooks/useCart.ts` to the **existing** `cartApi`:
   `addItem` -> `cartApi.add(productId, quantity)`; `updateQuantity` -> `cartApi.update(cartItemId, quantity)`;
   `removeItem` -> `cartApi.remove(cartItemId)`; `clearCart` -> `cartApi.clear()`. Dispatch the
   returned `Cart` as the new state through the existing `hydrate` action so the backend response
   becomes the state (and `itemCount`/`subtotal` stay consistent). Optimistic local update first
   so the UI stays responsive, and on failure dispatch the existing `setOnline(false)` and leave
   the optimistic value — matching the offline pattern already used in `providers.tsx:116-119` and
   `CategoryNav.tsx:38-42`. **No new slice, no new hook, no new endpoint.**
7. Carry the cart-line id: add an optional `cartItemId?: string` to `CartItem` in
   `frontend/types/cart.ts` and populate it in a single shared mapper (see item 8). This is what
   makes operations 3 and 4 callable at all.
8. Put that mapper in `frontend/services/api/cart.api.ts` as `toCartItems(cart)` so
   `app/providers.tsx` and `hooks/useCart.ts` share one mapping instead of duplicating it a
   third time. Also de-duplicate the five identical item-selection blocks in `cart.api.ts` into a
   single shared field string.
9. In `frontend/app/providers.tsx`, remove the localStorage cart read (lines 95-96) and keep only
   the `cartApi.get()` hydrate, and remove the cart localStorage write in
   `frontend/store/index.ts:29-32`. This follows the project's own rule
   (`frontend/frontend-data-plan.md:13`: "Local storage … must not replace authenticated backend
   state") and makes the backend the single source of truth. The **wishlist** localStorage mirror
   stays untouched.
10. Add an in-flight/mutation guard so a `cartApi.get()` response that resolves after a local
    mutation cannot clobber the newer state.
11. Gracefully degrade for non-UUID product ids (demo products, `landingPage.tsx:510` subscriptions,
    Pay-As-You-Go lines): skip the mutation, keep the local state, do not throw. This prevents
    GraphQL variable-coercion errors from reaching the console during offline/demo use.
12. `frontend/components/layout/PublicHeader/CategoryNav.tsx`: replace raw `<a href>` with
    `next/link`'s `<Link>` so navbar navigation is client-side and the store is not torn down.
    Also update `PublicFooter.tsx:24,28` and `SearchBar.tsx:32` for in-app destinations. The
    existing `.category-nav a` / footer CSS applies unchanged to `next/link` anchors — **no CSS
    edit**.

### Public Purchase

13. **No change.** `/products`, `/products/[slug]`, `/cart`, `/checkout`, the product/category
    queries and the guest checkout mutation stay unauthenticated, exactly as
    `get_optional_current_user` and `require_user_or_guest` already provide. No JWT is added to any
    public endpoint. Items 1-5 and 6-12 only make these flows *work*; they do not restrict them.

### Authorized Purchase

14. **No change to the backend auth path.** The same cart endpoints serve authenticated customers
    through `Cart.user_id`; item 6 makes the frontend actually use them for logged-in users too.
15. **Explicitly not implemented, documented instead (§6.2): guest-cart -> authenticated-cart
    merging on login.** It requires a backend ownership transfer on the token-issuing path
    (`AuthService.login` / `signup` / `google_login`) using only the existing `carts` /
    `cart_items` tables. It is a behaviour change and needs sign-off; it is not required for any
    of the flows in §24 to pass.
16. Clear the Redux cart on `logout` (`store/slices/authSlice.ts`) so a signed-out session cannot
    briefly display the previous customer's items, and consider clearing `guest_token` on logout so
    a shared browser does not surface a stale guest cart.

### Navbar

17. In `frontend/components/layout/PublicHeader/CategoryNav.tsx`, render
    `<Link href="/my-account">My Account</Link>` and `<Link href="/my-orders">My Orders</Link>`,
    gated on `isAuthenticated && user?.role_name === "customer"` from the existing `useAuth()`
    hook. Both routes already exist and are already guarded by
    `app/(account)/layout.tsx`. Admin and unauthorized users get the unchanged public navigation.
    No CSS change (the `.category-nav a` rule at `globals.css:92` already styles them).
18. Do not touch `app/(account)/layout.tsx`, `app/admin/layout.tsx` or `HeaderActions.tsx`'s role
    branching — verified correct.

---

## 12. FILES TO MODIFY

```
Frontend:
- frontend/app/(public)/products/[slug]/page.tsx      fetch by slug from the API; notFound() only on a backend miss
- frontend/services/api/products.api.ts               add bySlug() + CatalogProductDetail; de-duplicate item fields
- frontend/services/api/cart.api.ts                   add shared toCartItems() mapper; reuse one item-field block
- frontend/hooks/useCart.ts                           call the existing cartApi; keep signatures
- frontend/app/providers.tsx                          drop the localStorage cart read; fix the slug/id collapse; re-read the cart after auth settles
- frontend/store/index.ts                             drop the cart localStorage write (keep the wishlist mirror)
- frontend/components/layout/PublicHeader/CategoryNav.tsx  next/link instead of <a>; auth-gated My Account / My Orders
- frontend/app/(public)/storefront-data.ts            widen `category`/`categoryLabel` to string so real backend categories fit; mock values unchanged
- frontend/types/cart.ts                              add optional cartItemId
- frontend/app/(public)/cart/page.tsx                 render the product link only when a real slug is present
- frontend/app/sitemap.ts                             stop advertising mock-only product URLs
- focused tests for the above
```

```
Backend:
- none required for the minimum fix set.
  `product(slug:)`, all four cart mutations, guest cart identification and guest checkout already
  exist and are covered by passing tests.
```

```
Shared/types:
- frontend/types/cart.ts (optional cartItemId) and frontend/app/(public)/storefront-data.ts
  (category fields widened from a literal union to string) — the only two type-level edits, both
  required so real backend data fits the existing components.
```

```
CSS:
- none. `.category-nav a` (globals.css:92) already styles the two new nav links.
```

### Verification commands

```
cd frontend && npx tsc --noEmit   # must stay at the 6 pre-existing errors, none in the changed files
cd frontend && npx eslint         # must stay at the 3 pre-existing errors (all AdminChatPage.tsx)
cd frontend && npx jest           # must stay at 2 pre-existing chat-suite failures, no new ones
cd backend  && python -m pytest src/app/tests/test_public_products.py src/app/tests/test_public_cart.py src/app/tests/test_public_checkout.py -v
```

---

## 13. Test matrix status (pre-implementation)

| Public user | Status | Customer | Status | Admin | Status |
|---|---|---|---|---|---|
| View Homepage | Working | View Homepage | Working | Admin auth | Working |
| View Products | Working | View Products | Working | Admin redirect | Working |
| View Product Details | **BUG (404)** | View Product Details | **BUG (404)** | Admin routes protected | Working |
| Add to Cart (on screen) | Working | Add to Cart (on screen) | Working | Customer nav not exposed | Working (links absent) |
| Cart shows product | Working in-session | Cart shows product | Working in-session | My Account / My Orders shown to customer | **BUG (absent)** |
| Navigate away | **BUG (full reload)** | Navigate away | **BUG (full reload)** | Admin functionality | Working |
| Return to Cart — product still there | **BUG (empty)** | Return to Cart — product still there | **BUG (empty)** | | |
| Cart count correct after navigation | **BUG (0)** | Cart count correct after navigation | **BUG (0)** | | |
| Continue public purchase flow | **BUG (cart is empty at checkout)** | Purchase product | **BUG (cart is empty at checkout)** | | |
| My Account hidden | Working | My Account visible | **BUG (absent)** | | |
| My Orders hidden | Working | My Orders visible | **BUG (absent)** | | |

| Product view check | Status | Cart persistence check | Status |
|---|---|---|---|
| Homepage -> Product Details | **BUG** | Add -> Cart | Working in-session |
| Products -> Product Details | **BUG** | Cart -> Home -> Cart | **BUG** |
| Cart -> Product Details | **BUG** | Cart -> Products -> Cart | **BUG** |
| Correct product loaded | **BUG** | Cart -> Product Details -> Cart | **BUG** |
| Product ID correct | Correct as built (`slug`); wrong only when `item.product` is null | Cart count persists | **BUG** |
| Direct product URL | **BUG** (mock slugs only) | Multiple products persist | **BUG** |
| Refresh | **BUG** (no data fetched) | Quantity persists | **BUG** |
| Invalid product ID | 404 correctly, but for the wrong reason (mock miss, not a backend miss) | Remove item works | On-screen only; no backend write |
| | | Backend remains source of truth | **NO — the backend is never written** |

---

## Appendix A — Additional finding: `Decimal` is serialized as a JSON string

Discovered while implementing the fix above, and it affects any code that consumes
`price` / `originalPrice` / `discountPrice` / `averageRating` / `unitPrice`.

Verified against the installed Strawberry build:

```
>>> strawberry.Schema(query=Q).execute_sync("{ price }").data
{'price': '549.00'}      # str, not float
```

`ProductType.price`, `ProductType.originalPrice`, `ProductType.discount_price`,
`ProductType.average_rating` (`public/api/graphql/types/product.py:41-47`) and
`CartItemType.unit_price` are all `Decimal`, so they arrive as strings on the wire. The
frontend response types declared them as `number` (`services/api/products.api.ts:6`,
`services/api/cart.api.ts:6,11`), which is a lie that silently yields `NaN` arithmetic
(e.g. the `Math.round((1 - price / oldPrice) * 100)` discount badges) for any caller that
forgets `Number()`.

- **Current behaviour:** every existing consumer happens to wrap the value in `Number()`
  (`ProductsPage.tsx:76-78`, `landingPage.tsx:251-253`), so no live bug — but the types
  do not protect the next caller.
- **Root cause:** GraphQL client types written by hand without checking the scalar's
  wire representation.
- **Severity:** MEDIUM (latent, not currently user-visible).
- **Fix applied:** `CatalogProduct.price` / `originalPrice` / `discountPrice` /
  `averageRating` and `CartApiItem.unitPrice` / `CartApiItem.product.price` are now typed
  `number | string`, and the coercion happens exactly once, in `toStorefrontProduct`
  (`app/(public)/storefront-data.ts`) and `toCartItems` (`services/api/cart.api.ts`).

---

## Appendix B — Implementation status

Implemented from §11 / `plan-creating.md`. Frontend only; **no backend change**, **no CSS change**.

| Fix | File | Done |
|---|---|---|
| 1-4 single-product fetch + backend-first route | `services/api/products.api.ts`, `app/(public)/products/[slug]/page.tsx`, `app/(public)/storefront-data.ts` | yes |
| 4 shared mapper reused by Homepage + Products | `app/(public)/products/ProductsPage.tsx`, `app/(public)/landingPage.tsx` | yes |
| 5 no cart-line id in `slug` | `app/providers.tsx`, `app/(public)/cart/page.tsx`, `app/sitemap.ts` | yes |
| 6-8 `useCart` wired to the existing `cartApi` | `hooks/useCart.ts`, `services/api/cart.api.ts`, `types/cart.ts` | yes |
| 9 localStorage cart mirror removed (wishlist kept) | `app/providers.tsx`, `store/index.ts` | yes |
| 10 stale-response guard | `app/providers.tsx` | yes |
| 11 non-UUID ids degrade gracefully | `services/api/cart.api.ts`, `hooks/useCart.ts` | yes |
| 12 `next/link` in the navbar/footer/search | `CategoryNav.tsx`, `PublicFooter.tsx`, `SearchBar.tsx` | yes |
| 16 cart cleared on logout | `store/slices/cartSlice.ts` (`extraReducers` on `logout`) | yes |
| 17 auth-gated `My Account` / `My Orders` | `CategoryNav.tsx` | yes |
| 15 guest-cart merge on login | backend | yes — see Appendix C |

Verification (baseline in §0 for comparison):

```
npx tsc --noEmit  -> 0 errors tree-wide
npx eslint        -> 3 errors, all in app/admin/components/AdminChatPage.tsx (pre-existing,
                     untouched by this work); 0 errors in any file changed here
npx jest          -> 78 suites / 175 tests, all pass
backend pytest    -> 276 passed (full suite, including the new test_public_cart_merge.py)
```

---

## Appendix C — Guest cart -> customer cart hand-over (implemented)

Closes the §6.1 gap. Uses only the existing `carts` / `cart_items` tables: **no migration, no new
table, no new endpoint, no second cart system.**

### The constraint that drives the design

`carts.user_id` and `carts.guest_token_hash` are both `UNIQUE` (`backend/src/app/models/cart.py:18,20-23`),
so exactly one row can hold either identity. The hand-over therefore has two shapes, and must
choose between them:

- customer has **no** cart -> adopt the guest row in place;
- customer **has** a cart -> fold the guest lines in by `(product_id, variant_id)`, summing
  `quantity`, then drop the guest row.

`guest_token_hash` is cleared on adoption. Leaving it set would let whoever still holds that
cookie resolve to the signed-in customer's basket via `require_user_or_guest`.

### Files

| File | Change |
|---|---|
| `backend/src/app/public/repositories/cart_repository.py` | `get_by_guest_token_hash()` — the inverse of the existing `get_by_user()` |
| `backend/src/app/public/services/cart_service.py` | `CartService.merge_guest_cart(user, guest_token_hash) -> bool`, idempotent |
| `backend/src/app/public/services/auth_service.py` | `bind_guest_cart()`; the merge runs in `_issue_tokens` so no entry point can forget it |
| `backend/src/app/api/auth.py` | `POST /auth/login` and `POST /auth/google` bind the `guest_token` cookie |
| `backend/src/app/public/api/graphql/mutations/auth.py` | `mutate_login` / `mutate_google_login` / `mutate_signup` bind `ctx.guest_token` |
| `backend/src/app/tests/test_public_cart_merge.py` | new — 4 tests over the real HTTP + GraphQL flow |

### Two deliberate decisions

1. **`refresh` never merges.** `refresh()` nulls the pending guest hash before calling
   `_issue_tokens`, because continuing an existing session is not a sign-in. Without this,
   a returning customer's refresh would adopt whatever guest cart the cookie now points at.
2. **A merge failure never blocks sign-in.** `_issue_tokens` wraps the merge in
   `try/except SQLAlchemyError` + `rollback`. The tokens are already committed at that point,
   so a hand-over problem must not turn a valid login into a 500.

### Frontend

No change was needed. `app/providers.tsx` re-reads the cart on `[authReady, isAuthenticated]`,
and the login page dispatches `setUser(...)` directly, so a client-side sign-in re-keys the cart
and the merged contents appear without a reload.

### Tests

`test_public_cart_merge.py` covers, through the real endpoints rather than mocks:

- guest adds 2 -> signs in -> same 2 items on the customer's cart (adopt path);
- customer already had the same product at qty 1, guest adds qty 3 -> one line at qty 4, one
  `carts` row, `guest_token_hash is None` (fold path);
- signing in with no guest cart leaves the customer cart untouched;
- signing in twice does not double the quantity (idempotence).
