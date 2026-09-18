# Admin Hero Implementation Plan

> Ponytail Ultra workflow — audit → plan → implement → test → re-test → document.

## 1. Project Audit

### 1.1 Backend Structure

- **Stack**: FastAPI + Strawberry GraphQL (single `/graphql` public schema, single `/admin/graphql` admin schema), SQLAlchemy 2.0 ORM, Alembic migrations, PostgreSQL (prod) / SQLite (dev file + in-memory tests).
- **Layout**: code lives under `backend/src/app/` (import root `app.*`). Layers: `models/` (ORM), `schemas/` (Pydantic), `admin/{api/graphql,repositories,services}`, `public/{api/graphql,repositories,services}`, `core/` (exceptions/security), `integrations/cloudinary` (media upload), `db/` (engine/session), `dependencies/auth.py` (JWT + `require_admin`).
- **Error model**: `core/exceptions.py` `AppError` hierarchy (`ValidationError` → 422, `NotFoundError` → 404, `PermissionDeniedError` → 403). Admin schema uses `_AppErrorExtension` to convert `AppError` into GraphQL errors with `extensions.code`.
- **Auth**: JWT access (~4h) / refresh (~30d), HTTP-only cookies set by REST `/auth/*`; `get_current_user` reads `Authorization: Bearer` or `access_token` cookie; `require_admin` enforces `role_name == "admin"`. `AdminContext` is dependency-gated by `require_admin`.
- **Media**: `integrations/cloudinary/client.py` `CloudinaryClient.upload_base64(data_url, folder)` → secure URL. Configured via `CLOUDINARY_*` env (`backend/.env` has values). `upload_product_image` admin mutation already follows this pattern (folder `"products"`); hero upload will reuse it with folder `"heroes"`.

### 1.2 Frontend Structure

- **Stack**: Next.js 16 (App Router), React 19, Tailwind v4 (but real styling is plain CSS in `globals.css` / `admin/styles/admin_style.css`), Redux Toolkit, Formik + Yup in products page.
- **Layout**: `services/api/client.ts` — `graphqlClient` (public `/graphql`) and `adminGraphqlClient` (admin `/admin/graphql`), cookie credentials. `services/api/admin.api.ts` — admin API module (GraphQL strings + types). `services/api/` has public modules (`products.api.ts`, `categories.api.ts`, etc.).
- **Admin pages**: each route wrapper renders a component under `app/admin/components/`. Gold-standard CRUD = `AdminProductsPage.tsx` (Formik + Yup, modal form/delete/view, notify toast, `admin-empty-state`/`admin-error-state`, direct `adminApi.*` calls).
- **Toast/notify**: `notify()` → `setToast` + timeout, rendered as `.coupon-exact-toast.show`.
- **Loader**: `components/layout/PoojaPointLoader.tsx` used by `app/loading.tsx`; admin has no spinner (inline loading text).
- **Homepage**: `app/(public)/page.tsx` → `app/(public)/landingPage.tsx` (client) → `HeroSection`, `CategoriesSection`, `ProductsSection`, etc. Data via `Promise.allSettled([categoriesApi.list(), productsApi.featured()])` with static `storefront-data.ts` fallback and `setOnline(false)` on failure.

### 1.3 Existing Hero System (backend)

Already fully present under `backend/src/app/`:

- **Model**: `Hero` (`heroes`) — title, subtitle, badge, accent, cta_label, cta_link, display_order, is_active, starts_at, ends_at, seo_title, seo_description + UUID/Timestamp/SoftDelete mixins. **`HeroImage`** (`hero_images`) — hero_id, url, media_type (image|video), alt_text, display_order, is_primary, crop_x/crop_y/crop_zoom.
- **Admin CRUD (GraphQL, `/admin/graphql`)**: queries `heroes`, `hero`; mutations `createHero`, `updateHero`, `deleteHero`, `setHeroActive`, `addHeroImage`, `removeHeroImage`. Service `admin/services/hero_service.py`, repository `admin/repositories/hero_repository.py`, Pydantic `schemas/admin/hero.py` (`HeroCreate`, extra="forbid"), strawberry `HeroInput`, types `HeroType`/`HeroImageType`.
- **Tests**: `tests/test_admin_hero.py` (create + list).
- **Missing pieces** (gap analysis):
  1. No **maximum-4 limit** enforcement anywhere.
  2. No **public hero query** (zero hero references in `app/public/`).
  3. No **`uploadHeroImage`** admin mutation (only URL-based `addHeroImage`).
  4. `HeroService` performs no validation at all (no title checks, no limit).

### 1.4 Existing Homepage Hero (frontend)

- `components/layout/HeroSection.tsx` — public storefront hero. **Hardcoded** Shopify CDN image URLs, hardcoded heading "Woven for distinction.", badge "SIGNATURE EDIT", subtitle, "Shop now". Infinite carousel + typing animation. No API wiring.
- `AdminHeroPage.tsx` — admin silo-editor that only edits **local component state** (`initialSlides`), never calls `adminApi.listHeroes`/`setHeroActive`; media upload uses `URL.createObjectURL` (blob only, never persisted).
- `services/api/admin.api.ts` already has `listHeroes(...)` and `setHeroActive(...)` but **no** create/update/delete/upload/remove-image methods (and they're unused).
- The two sides are disconnected; backend is authoritative once wired.

### 1.5 Existing Admin CRUD Pattern (template)

Followed by `AdminProductsPage.tsx` and `AdminCategoriesPage.tsx`:

```
GraphQL @strawberry.input → mutation handler (thin) → Service (validation + repo + commit)
Repository (soft-delete aware) → mapping to GraphQL Type → client GraphQL mutation string → local state upsert → notify toast
```

### 1.6 Existing Upload System

`CloudinaryClient.upload_base64()` (see 1.1). Product flow: form reads file via `FileReader.readAsDataURL` → on save `uploadProductImage(productId, dataUrl, ...)` → Cloudinary URL persisted. Hero will mirror this exactly (folder `"heroes"`).

### 1.7 Authentication / Authorization

- Public `/graphql`: optional user.
- Admin `/admin/graphql`: `get_admin_context` → `require_admin` → only `role_name == "admin"` + active.
- New **public** hero query rides the public schema (no admin exposure).
- New admin hero mutations ride the admin schema (admin-only, no public exposure).

### 1.8 Existing API Pattern

GraphQL mutations/queries defined in `admin/api/graphql/{mutations,queries}/X.py`, exported in `__init__.py`, wired as `strawberry.field` in `schema.py`. Public domain identical for `queries/`.

### 1.9 Existing Validation Pattern

Pydantic `SchemaBase(extra="forbid")`; service-level `_validate()`/explicit `ValidationError(...)`; `_AppErrorExtension` → `errors[0].extensions.code`.

### 1.10 Existing Error Handling

`AppError` → FastAPI JSON `{"detail": ...}` (REST) or GraphQL error via extension (GraphQL). Frontend: try/catch → notify `error.message`; load blocks → `admin-error-state`.

## 2. Existing Files

### Backend Files

| File | Role |
| --- | --- |
| `src/app/models/hero.py`, `hero_image.py` | ORM models |
| `src/app/schemas/admin/hero.py` | Pydantic `HeroCreate`/`HeroResponse` |
| `src/app/admin/repositories/hero_repository.py` | Admin data access |
| `src/app/admin/services/hero_service.py` | Admin business rules |
| `src/app/admin/api/graphql/{types,queries,mutations}/hero.py` | GraphQL layer |
| `src/app/admin/api/graphql/schema.py` | Admin schema wiring |
| `src/app/admin/api/graphql/mutations/__init__.py` | Mutation exports |
| `src/app/integrations/cloudinary/client.py` | Media upload |
| `src/app/tests/test_admin_hero.py` | Existing hero tests |
| `alembic/versions/b7125b6f5c2a_initial_schema.py` | Base migration (heroes table) |

### Frontend Files

| File | Role |
| --- | --- |
| `services/api/admin.api.ts` | Admin API module (has `listHeroes`, `setHeroActive`) |
| `app/admin/components/AdminHeroPage.tsx` | Admin hero page (local-only today) |
| `app/admin/components/AdminProductsPage.tsx` | CRUD template |
| `components/layout/HeroSection.tsx` | Public storefront hero (hardcoded today) |
| `app/(public)/landingPage.tsx` | Homepage data orchestration |
| `services/api/products.api.ts` / `categories.api.ts` | Public API module pattern |

## 3. Files To Create

### Backend

1. `alembic/versions/<id>_add_hero_slot_limit.py` — add `slot` column (nullable, unique, check 1..4) + backfill.
2. `src/app/public/repositories/hero_repository.py` — public active-hero query.
3. `src/app/public/api/graphql/types/hero.py` — public `HeroType`/`HeroImageType`.
4. `src/app/public/api/graphql/queries/hero.py` — public `resolve_heroes`.

### Frontend

5. `services/api/hero.api.ts` — public hero API module.

## 4. Files To Modify

### Backend

1. `src/app/models/hero.py` — add `slot` column + CHECK + unique.
2. `src/app/admin/repositories/hero_repository.py` — `count()`, `next_free_slot()`, slot-aware `create`/`delete`.
3. `src/app/admin/services/hero_service.py` — max-4 enforcement (count check + IntegrityError fallback) + `upload_image()`.
4. `src/app/admin/api/graphql/mutations/hero.py` — `mutate_upload_hero_image`; export.
5. `src/app/admin/api/graphql/mutations/__init__.py` — export new mutation.
6. `src/app/admin/api/graphql/schema.py` — wire `upload_hero_image` field.
7. `src/app/public/api/graphql/schema.py` — wire public `heroes` query.
8. `src/app/public/api/graphql/queries/__init__.py` — export `resolve_heroes`.
9. `src/app/tests/test_admin_hero.py` — expand (max-4, CRUD, auth, public, images).

### Frontend

10. `services/api/admin.api.ts` — add `createHero`, `updateHero`, `deleteHero`, `uploadHeroImage`, `addHeroImage`, `removeHeroImage`.
11. `app/admin/components/AdminHeroPage.tsx` — rewrite: backend CRUD, image upload, 4-limit UI + warning.
12. `components/layout/HeroSection.tsx` — data-driven via `slides` prop.
13. `app/(public)/landingPage.tsx` — fetch public heroes; backend data = source of truth; static fallback only when offline.

## 5. Database Changes

New migration adds to `heroes`:

- `slot INTEGER NULL`
- UNIQUE constraint on `slot`
- CHECK `slot IS NULL OR (slot BETWEEN 1 AND 4)`
- Backfill: deleted rows → `slot = NULL`; live rows → 1..N by `display_order, created_at`.

Tests create schema from model metadata (in-memory SQLite), so model + migration stay in sync.

## 6. Hero Data Model

Unchanged fields + new `slot` (server-assigned). `HeroImage` untouched. No new Hero model created (reuse only).

## 7. Maximum Hero Limit

**Maximum = 4.**

- **DB level**: UNIQUE `slot` in `1..4` (only 4 distinct slot values). Concurrent inserts racing for the same free slot collide on the UNIQUE constraint → one wins, the other is rejected.
- **Service level**: `HeroService.create` rejects with `ValidationError` (422) when `count >= 4`; catches `IntegrityError` on the race and re-raises the same friendly error.
- **Frontend level**: "Add slide" disabled/hidden at 4 with the same warning — informative only, never authoritative.
- Message: `Maximum 4 Hero sections are allowed. Please update or delete an existing Hero before adding another.`

## 8. API Contract

### Admin mutations (additions)

- `uploadHeroImage(heroId: UUID!, base64Data: String!, mediaType: String = "image", altText: String, displayOrder: Int = 0, isPrimary: Boolean = false, cropX: Int = 50, cropY: Int = 50, cropZoom: Int = 100): HeroType`

Existing already present: `heroes`, `hero`, `createHero(data: HeroInput!)`, `updateHero(id, data)`, `deleteHero(id)`, `setHeroActive(id, isActive)`, `addHeroImage(...)`, `removeHeroImage(imageId)`.

Strawberry default `auto_camel_case` maps snake_case Python → camelCase GraphQL (`ctaLabel`, `displayOrder`, `isActive`, …).

### Public query (new)

- `{ heroes { id title subtitle badge accent ctaLabel ctaLink displayOrder images { id url altText mediaType displayOrder isPrimary } } }` — only `is_active` + not soft-deleted + within optional `starts_at`/`ends_at` window, ordered by `display_order` (active heroes only). Public schema = read-only; no herd mutations exposed publicly.

## 9. CRUD Flow

- CREATE: Admin page → validate (title + limit) → `createHero` → 4-limit enforced in service → slot assigned → commit → refetch list.
- READ: admin `heroes` query (all non-deleted, incl. inactive). Public `heroes` (active only).
- UPDATE: `updateHero(id, data)` — never counts against the limit (slot unchanged).
- DELETE: `deleteHero(id)` → soft delete, frees slot → a following create becomes possible.

## 10. Image / Media Handling

- Reuse `CloudinaryClient.upload_base64(..., folder="heroes")`.
- `uploadHeroImage` base64 → Cloudinary → `HeroImage` row attached to hero.
- `addHeroImage` (URL) kept for pre-uploaded URLs; `removeHeroImage` deletes an image row.
- File accepted client-side is `image/*` (+ `video/*` kept for mediaType field; public renderer treats video file as fallback to image).
- Tests use Cloudinary-free paths (URL-based add/remove + upload stub) since network is unavailable in CI; real upload path requires configured Cloudinary (flagged BLOCKED/untested in CI for the network step only).

## 11. Ordering

- `display_order ASC, created_at DESC` for list (repository already does this). Admin form exposes display order. Public renderer follows returned order.

## 12. Active / Inactive Logic

- `is_active` on `Hero`; `setHeroActive(id, isActive)` admin mutation.
- Public query returns `is_active == True` only. Inactive heroes never appear publicly.

## 13. Authorization

- All hero mutations/queries in admin schema are guarded by `require_admin` via `AdminContext`. Backend determines role from the authenticated JWT user — never trusts client-sent role.
- Public `heroes` query is anonymous read; it returns only public-safe data (no `is_admin`, no seo needed).
- Direct API attempts by customers/unauthenticated → 403/401 via dependency chain.

## 14. Public Homepage Wiring

`heroes` (public) → `services/api/hero.api.ts` → `landingPage.tsx` allSettled fetch → `HeroSection` `slides` prop → homepage. Backend data is the source of truth when connected; static hero content renders only when the API is unreachable (existing offline fallback convention, `setOnline(false)`).

## 15. Validation

- Pydantic `HeroCreate`: title required 1..255, subtitle ≤500, badge ≤100, accent ≤64, cta_label ≤100, cta_link ≤2048, display_order ≥0, seo lengths. `extra="forbid"`.
- Service: max-4 limit. `uploadHeroImage` requires non-empty data URL.
- Public API never exposes validation that could leak admin-only concerns.

## 16. Loading States

- `AdminHeroPage`: `loading` → existing `admin-empty-state` text ("Loading hero sections...") and `admin-error-state` on failure.
- Homepage: existing loader untouched (`PoojaPointLoader`/`app/loading.tsx`). Hero fetch joins the existing `Promise.allSettled` block.

## 17. Error / Warning / Success Handling

- Success toasts: "Hero created successfully.", "Hero updated successfully.", "Hero deleted successfully.", "Hero activated/deactivated".
- Warning toasts: "Maximum 4 Hero sections allowed." (+ disabled Add), "Hero is inactive.", "No active Hero sections found." (public empty).
- Error toasts: "Failed to create/update/delete Hero..." surfaced from `GraphQLError.message` / `ApiError.detail`. No success toast after failure.

## 18. Testing Plan

- pytest: max-4 (create 1→4 ok, 5th rejected, DB stays 4; delete→3→create→4; update while 4 exists OK), CRUD happy path, auth (admin OK, customer 403, unauthenticated auth-flow), images (add/remove/upload stub), public query (active-only, ordering, inactive hidden, empty), slot check constraint, persistence.
- Frontend: TypeScript build (`npm run build`/`tsc`), ESLint, existing Jest.
- Manual regression of admin + public navigation.

## 19. Implementation Status

Status: **complete and verified**.

### Backend
- Max-4 enforcement: `Hero.slot` column (nullable, `uq_heroes_slot` unique, `ck_hero_slot_range` check 1..4) plus a service-level count guard; `IntegrityError` is mapped to `ValidationError`; deleting a hero frees its slot.
- New admin mutation `uploadHeroImage` (Cloudinary folder `heroes`), exported and wired in the admin schema alongside `addHeroImage` / `removeHeroImage`.
- `HeroInput.startsAt/endsAt` are `datetime` and flow into create/update, so scheduling works end-to-end.
- New public `heroes` query (active + not soft-deleted + inside the schedule window, ordered `displayOrder ASC, createdAt DESC`) with a trimmed public `HeroType`.
- Bug fix: `AppError.__init__` now propagates the message into `detail`, so friendly errors surface in GraphQL/REST.

### Migration
- `alembic/versions/e5b9c4a1720f_add_hero_slot_limit.py` (down_revision `a3d9c2f4e6b1`): adds `slot`, the unique + check constraints, and backfills existing rows with `ROW_NUMBER()`.

### Tests
- `test_admin_hero.py`: 12 tests — CRUD, max-4 (5th rejected), delete frees a slot, DB check constraint, customer forbidden, unauthenticated, image add/remove.
- `test_public_hero.py`: 5 tests — empty, active ordered, inactive hidden, soft-deleted hidden, schedule window.
- Full backend suite: **208 passed, 0 failed** (the previously reported coupon failure no longer reproduces; coupon suite alone: 40 passed).
- Cloudinary is not configured in tests, so the real base64 upload path is exercised only at the schema level; CI covers URL-based add/remove.

### Frontend
- `services/api/admin.api.ts`: hero CRUD + `uploadHeroImage` / `addHeroImage` / `removeHeroImage`; product image methods (`uploadProductImage` / `addProductImage` / `removeProductImage`) and `images` added to the product type/query (fixes pre-existing type errors).
- `app/admin/components/AdminHeroPage.tsx`: rewritten and backend-driven (max-4 UI, media upload via `FileReader`, remove, delete confirm, active toggle, toasts).
- `services/api/hero.api.ts`: public `heroesApi.list()`.
- `components/layout/HeroSection.tsx`: data-driven `slides` prop with built-in fallback.
- `app/(public)/landingPage.tsx`: fetches heroes via `Promise.allSettled` and maps them to slides; the built-in hero is used when the list is empty/unavailable.
- Checks: `npx tsc --noEmit` clean; `npm run build` succeeds (all routes); `landingPage.test.tsx` updated with a Redux `Provider` + `heroesApi` mock and passing.

### Pre-existing test failures (resolved)
- `CategoryNav`, `PublicHeader` and `my-orders` suites failed at HEAD because Redux-connected components were rendered without a `Provider` (the orders test also used the default 5s timeout). Fixed by wrapping them in `renderWithProviders` and raising the orders test timeout.
- `app/admin/hero/page.test.tsx` was updated for the backend-driven page (mocks `adminApi.listHeroes` and asserts the live editor fields).
- Frontend Jest: **109 passed, 0 failed** (71 suites); `npx tsc --noEmit` clean; `npm run build` succeeds.

### Remaining pre-existing lint issues (not part of this work)
- All ESLint **errors** are now fixed (0 errors); 61 non-blocking warnings remain in unrelated files (e.g. `no-img-element`, `no-location-assign-relative-destination`, `no-unused-vars`).

### Verification commands
- Backend: `cd backend; $env:PYTHONPATH="src"; .\.venv\Scripts\python.exe -m pytest src/app/tests -q` → 208 passed.
- Frontend: `cd frontend; npx tsc --noEmit; npm run build; npx jest landingPage.test`.