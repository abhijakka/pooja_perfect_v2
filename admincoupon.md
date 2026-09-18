# Admin Coupon Testing & Implementation Report

> Ponytail Ultra workflow — audit → plan → test → fix → re-test → verify → document.

Status: **COMPLETE and verified.** Admin Coupon CRUD is fully implemented on the backend
and the frontend admin page is wired to the real API (it was previously 100% mocked).
Two real backend bugs were found and fixed. All 40 backend coupon tests, the full
(getting-started unaffected) suite, frontend checks, and a 12/12 live-server
verification pass.

## 1. Actual Implemented Contract (verified from code, not assumed)

Endpoint: `POST /admin/graphql`, gated by `require_admin` via `AdminContext`
(unauthenticated → 401 `{"detail": ...}`; non-admin role → 403).

| Operation | GraphQL | Notes |
| --- | --- | --- |
| List | `coupons(page, pageSize, search, isActive): CouponPage` | excludes soft-deleted; `total` reflects filters |
| Get | `coupon(id: UUID!): CouponType` | 404 if missing/deleted |
| Create | `createCoupon(data: CouponInput!): CouponType` | code uppercased server-side |
| Update | `updateCoupon(id: UUID!, data: CouponInput!): CouponType` | partial via whole-object input |
| Delete | `deleteCoupon(id: UUID!): MutationResult` | soft delete (`deleted_at`), 404 if missing/deleted |
| Toggle | `setCouponActive(id: UUID!, isActive: Boolean!): CouponType` | |

`CouponInput` (camelCase): `code: String!`, `name`, `description`, `couponType`
(`percentage`|`fixed`), `value: Decimal!`, `minimumOrderAmount`, `maximumDiscount`,
`startsAt`, `expiresAt` (dates via JSON scalar), `usageLimit: Int`, `perUserLimit: Int`,
`isActive: Boolean = true`.

`CouponType`: `id`, `code`, `name`, `description`, `couponType`, `value`,
`minimumOrderAmount`, `maximumDiscount`, `startsAt`, `expiresAt`, `usageLimit`,
`perUserLimit`, `isActive`, `usageCount`, `createdAt`, `updatedAt`.

Business errors return GraphQL `errors[0].extensions.code` (409 duplicate, 404 not
found, 422 validation). `code` is unique at the DB level (index), so deleted coupons
cannot be re-created under the same code.

## 2. Static Audit Summary

- Pass: layered backend (model → Pydantic → repository → service → GraphQL), full CRUD
  present, `require_admin` gating, snake_case infra with Strawberry camelCase mapping.
- Gap 1 (backend bug): `usageCount` was always `0` in list/get/toggle responses because
  resolvers built the GraphQL type from ORM objects via
  `getattr(coupon, "usage_count", 0)` — the ORM `Coupon` has no such attribute.
- Gap 2 (backend bug): re-creating a soft-deleted coupon code leaked a raw
  `sqlite3.IntegrityError` (HTTP 500) instead of a clean 409 — DB unique constraint on
  `code` vs. `get_by_code` ignoring deleted rows.
- Gap 3 (frontend dead code): `AdminCouponsPage.tsx` rendered a hardcoded initial list
  and never called any API; `admin.api.ts` lacked `createCoupon`/`updateCoupon`/
  `deleteCoupon` and listed only `{ id }` columns; `AdminCoupon` was `Record<string, unknown>`.

## 3. Issues Found & Fixed

| # | Issue | Fix | Files |
| --- | --- | --- | --- |
| 1 | `usageCount` always 0 in list/get/setActive | `CouponService.list` computes counts in one batched query (`AdminCouponRepository.usage_counts(coupon_ids)`); `get`/`set_active` return `AdminCouponResponse` carrying `usage_count` | `backend/src/app/admin/services/coupon_service.py`; `backend/src/app/admin/repositories/coupon_repository.py` |
| 2 | delete-then-recreate same code → raw `IntegrityError` 500 | create/update commit wrapped in try/except `IntegrityError` → rollback → `DuplicateResourceError("Coupon code already exists")` (409, `extensions.code`) | same files |
| 3 | AdminCouponsPage 100% mocked | Fully rewired to real `adminApi` GraphQL calls (list/search/filter, create, edit, delete, soft toggle, stats, CSV export) | `frontend/services/api/admin.api.ts`; `frontend/app/admin/components/AdminCouponsPage.tsx` |
| 4 | `admin.api.ts` missing coupon CRUD + untyped shape | Added typed `AdminCoupon`, `couponFields`, `getCoupon`/`createCoupon`/`updateCoupon`/`deleteCoupon`; `listCoupons`/`setCouponActive` return full fields | `frontend/services/api/admin.api.ts` |

## 4. Backend Tests (`backend/src/app/tests/test_admin_coupons.py` — 40 tests, all passing)

- **Auth**: unauthenticated → 401 detail; customer role → 403; inactive admin → 403; suspended admin → 403.
- **CRUD happy path**: create with all fields (value, min order, max discount, dates, limits, description, name); code uppercased; `usageCount: 0` on create; get by id; update every mutable field (including disabling a previously-set schedule); toggle via `setActive`/`setCouponActive`; delete; delete-not-found 404.
- **Duplicate / not found**: same code on create → 409; same code on update → 409; operations on unknown id → 404; delete twice → 404.
- **Validation** (422, `extensions.code`): `value` 0/negative (fixed & percentage); percentage > 100 rejected while `fixed` value > 100 allowed; negative `minimumOrderAmount`; `usageLimit`/`perUserLimit` < 1; empty code; expiry before start; past expiry.
- **List/query math**: default page + pagination totals; `search` substring match on code/name; `isActive` filter (true/false, inactive excluded from true); page/pageSize respected.
- **Usage stats accuracy**: list/get/toggle all reflect real usage count from `coupon_usage`.
- **Checkout compatibility** (public checkout path): percentage coupon applied — subtotal 400.00 → discount 40.00 → total 360.00 and `usageCount` becomes 1; minimum-order rejection; disabled coupon rejected.
- **Delete-then-recreate**: create → delete → re-create same code → clean 409 GraphQL error (no 500), DB state unchanged.

### Full backend suite
`cd backend; ./.venv/Scripts/python.exe -m pytest src/app/tests -q` → **191 passed, 2 failed**.
The 2 failures are pre-existing breakage from the parallel hero-session
(`test_admin_hero.py`: `name 'MAX_HEROES' is not defined` in
`admin/repositories/hero_repository.py:54`), unrelated to coupons and out of scope.
Coupon suite alone: **40 passed, 0 failed**. Ruff clean on all touched backend files.

## 5. Frontend Verification

- `frontend/app/admin/coupons/page.test.tsx` — render test (new) — **passes**.
- Full `jest` run: **104 passed, 5 failed** — 3 are pre-existing baseline failures
  (landingPage, CategoryNav, PublicHeader), 1 flaky (my-orders, passes standalone),
  1 parallel hero-session mismatch (AdminHeroPage "Media upload" text). None related to coupons.
- `eslint` clean on all touched files; `tsc --noEmit` shows no coupon-related errors
  (pre-existing errors remain only in `AdminCustomersPage.tsx`/`AdminProductsPage.tsx`, untouched).

## 6. Live Server Verification (real HTTP, fresh server)

Fresh single `uvicorn` on `0.0.0.0:8000` (all interfaces so the LAN/phone client that
resolves `environment.apiUrl` to `http://<page-host>:8000` can reach it). Unauthenticated
probe of `/admin/graphql` → 401 confirmed. Then end-to-end against the live server:
**12/12 PASS** — create all-fields → DB row present → get → list+search → update →
`setCouponActive(false)` → list filter `isActive=false` → delete → DB soft-delete
confirmed → delete-then-recreate same code → clean 409 `extensions.code` with DB
unchanged → create+delete second coupon. All test rows purged afterward; dev DB
(`backend/poojapoint.db`) restored to its 4 pre-existing coupons.

## 7. Out-of-scope findings (flagged, not changed)

- Public cart/checkout hardcodes coupon `POOJA10` (frontend `app/(public)` checkout; separate feature area).
- Orphan/unwired public `CouponService`/`CouponType`/`schemas/checkout/coupon.py` duplicate code paths exist but are not referenced by the admin CRUD; left untouched.
- Duplicate CSS utility files (`globals.css` copy variants) present since before this task.
- Admin README documents `/admin/coupons/[couponId]` detail route; implementation uses a single list page with a details modal (no route change made).
- Parallel hero-session refactor was mid-flight at report time (`MAX_HEROES` breakage +
  jest mismatch); resolved by the hero-session follow-up (see Addendum, §9).

## 8. Final Status

- Backend admin coupon CRUD: **PASS**
- Frontend admin coupons page: **PASS**
- Live end-to-end: **PASS (12/12)**
- Regression: coupon work introduces **no new failures** in backend or frontend suites.

## 9. Addendum (follow-up fix — hero `slot` migration)

After this report was finalized, the parallel hero-session's `slot` work hit a runtime
error on the dev DB: `sqlite3.OperationalError: no such column: heroes.slot`. Root cause:
the model referenced `heroes.slot` but the dev database had not been migrated to the
`e5b9c4a1720f` head (it was still at `f7c1e6a3b4d5`, with `a3d9c2f4e6b1` drop-activity-logs
and the hero-slot migration pending).

Fix applied:
- `alembic/versions/e5b9c4a1720f_add_hero_slot_limit.py` rewritten to use
  `op.batch_alter_table` for the `slot` column + UNIQUE(`uq_heroes_slot`) + CHECK
  (`ck_hero_slot_range`) so it works on SQLite (batch is a passthrough on PostgreSQL);
  downgrade updated to match. Also fixed a ruff I001 import-order nit.
- Dev DB upgraded to head (`alembic upgrade head`, from `backend/`). Verified
  `alembic_version = e5b9c4a1720f`, `heroes.slot` present with its constraints, and the
  previously-failing public heroes query now runs.

Current state: **full backend suite = 210 passed, 0 failed** (incl. `test_admin_hero.py`
+ `test_public_hero.py`, 17 hero tests). Live `POST /graphql` `{ heroes { ... } }` returns
hero rows; two live dev heroes hold slots 1 and 2 (distinct, per the unique constraint).