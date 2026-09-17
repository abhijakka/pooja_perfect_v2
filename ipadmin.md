# ipadmin.md — PONYTAIL ULTRA: Admin IP Address Visitor Tracking

## Summary

Implement complete visitor/IP tracking for **Admin → IP Address** using the
existing database table that already stores visitor IP records and the
existing Admin React page. No new database table, no new React table, no UI
redesign.

---

## 1. Deep audit findings

### Which table is "the existing IP Address table"?

The backend has **two** IP-related tables (no third can be added):

| Table | Model file | Purpose |
| --- | --- | --- |
| `ip_activity` | `backend/src/app/models/ip_activity.py::IPActivity` | Stores **every visitor** IP address, browser, OS, device, visited page (in `metadata_json`), timestamps. Already written by `services/ip_tracking.py`, `middleware/ip_tracking.py` and the public `POST /api/track` endpoint. |
| `ip_policies` | same model file `::IPPolicy` | Admin "allow/block/whitelist" policy rules (status/location/region/note). Separate feature. |

The visitor tracking target is **`ip_activity`** — it is the table that
records visitor IP addresses, devices, OS, browsers, pages and timestamps. It
supplies the data shown on the existing Admin IP Address page flow.
`ip_policies` remains untouched (its APIs stay; no data change).

### Existing `ip_activity` columns (before this task)

- `id` (uuid PK), `user_id` (FK nullable), `ip_address` (String 64)
- `action` (String 100), `user_agent` (String 1024)
- `metadata_json` (JSON — currently holds `path`, `referrer`, `screen`,
  `browser`, `browser_version`, `os`, `os_version`, `device`, `device_type`,
  `is_mobile`)
- `created_at`, `updated_at` (TimestampMixin)

### Required field mapping (requirement vs existing table)

| Required | Field | Present? | Action |
| --- | --- | --- | --- |
| IP Address | `ip_address` | ✅ exists | reuse |
| Device | `metadata_json["device"]` + `["device_type"]` | ✅ (JSON) | reuse; expose via GraphQL |
| Operating System | `metadata_json["os"]` | ✅ (JSON) | reuse; expose via GraphQL |
| Browser | `metadata_json["browser"]` | ✅ (JSON) | reuse; expose via GraphQL |
| Visited Page | `metadata_json["path"]` | ⚠️ only in JSON | **add `path` column**, backfill from JSON |
| Visit Count | (none) | ❌ | **add `visit_count` column** |
| Timestamp | `created_at` / `updated_at` | ✅ | reuse |

> **No new database table will be created. Required fields will be added/updated
> only in the existing IP Address table (`ip_activity`).**

### Existing backend audit

- Model: `backend/src/app/models/ip_activity.py`
- Single writer: `backend/src/app/services/ip_tracking.py::record_ip_activity`
- Server-side capture: `backend/src/app/middleware/ip_tracking.py` (HTML page nav only, skipped paths/suffixes, 60 s in-process dedupe)
- Public beacon: `backend/src/app/api/tracking.py` — `POST /api/track`
- Admin read API: `admin/graphql` query `ipActivity` (page + `ip_address` filter) → `IPActivityType` exposing derived `browser/os/device/path/...`
- Admin policy CRUD: `ipPolicies` + `createIpPolicy/updateIpPolicy/deleteIpPolicy` (left unchanged)
- Repo/service: `admin/repositories/ip_activity_repository.py`, `admin/services/ip_activity_service.py`
- Migrations: Alembic (`backend/alembic/`), head `d2e6f8a41b03`
- Auth: Admin GraphQL gated by `require_admin` (`admin/context.py`); public `/api/track` is open (no login) and non-blocking.
- `IPActivity` currently has NO admin create/update/delete GraphQL mutations → must be added to complete STEP 12 CRUD on the tracking table.

### Existing frontend audit

- Admin page: `frontend/app/admin/ip-address/page.tsx` → `frontend/app/admin/components/AdminIpPage.tsx`
  - Single `<table className="ip-exact-table">` (currently bound to `ipPolicies`)
  - Toolbar search + `<select>` status filter, summary cards, empty state, pagination bar, View/Form/Delete modals, toast, Export button. CSS classes `ip-exact-*` (admin_style.css). **All preserved — no CSS changes.**
- API service: `frontend/services/api/admin.api.ts` (`adminApi.listIpPolicies`, policy CRUD; **no activity API present** since the old activity log was removed)
- Client: `frontend/services/api/client.ts` → `adminGraphqlClient` (cookie auth)
- Tracking beacon: `frontend/hooks/useVisitorTracking.ts` (fires **once per app mount** only), `frontend/lib/tracking.ts` (client detection), `frontend/services/api/tracking.api.ts` (`POST /api/track`, fire-and-forget). Mounted in `frontend/app/providers.tsx`.
- Route-aware page tracking is **missing**: the beacon must fire on route changes, deduped against rerenders/Strict Mode.

---

## 2. Backend changes required

1. **Model** — add `path` (String 500, nullable) and `visit_count` (Integer, default/server 1) to `IPActivity`.
2. **Migration** — new Alembic revision that ALTERs `ip_activity` only:
   - `op.add_column` → `path`, `visit_count`
   - backfill `path` from `metadata_json`
   - add index `ix_ip_activity_ip_path_created_at`. Downgrade drops them.
   - No table creation.
3. **Tracking writer** (`services/ip_tracking.py`) — update `record_ip_activity`:
   - write/refresh `path` + `visit_count`
   - **upsert semantics**: one row per `(ip_address, action, path)`; a repeat within the 60 s dedupe window only refreshes metadata (no double count from middleware + beacon); otherwise `visit_count += 1`.
4. **Middleware** (`middleware/ip_tracking.py`) — record all HTML page navigations with `action="page_view"` so server-side and beacon writes share one dedupe key (prevents duplicate admin-page rows).
5. **Admin API** — extend the existing files (no new API system):
   - `IPActivityType`: add `path`, `visit_count`
   - `ip_activity` query resolver: map `path` (column, fallback metadata) and `visit_count`
   - new mutations in `mutations/ip_activity.py`: `createIpActivity`, `updateIpActivity`, `deleteIpActivity` (admin-gated via `require_admin`); wire into `AdminMutation` in `schema.py`
   - repo/service: `get_activity`, `create_activity`, `update_activity`, `delete_activity`
6. **Schemas** — add `path`, `visit_count` to `IPActivityResponse`.
7. **Tests** — extend `test_admin_ip_activity.py` (CRUD + new fields).

## 3. Frontend changes required

1. **`admin.api.ts`** — add `AdminIpActivity` type, `listIpActivity`, `createIpActivity`, `updateIpActivity`, `deleteIpActivity` (same `adminGraphqlClient`, same naming style). Policy APIs stay.
2. **`AdminIpPage.tsx`** — rebind the **same** table/clear modal/shell to tracking data:
   - source: `listIpActivity`
   - columns: IP Address · Device · OS · Browser · Visited Page · Visits · Last Visited · Actions (same 8-column count)
   - search across IP/device/OS/browser/page; `<select>` becomes device filter (All/Desktop/Mobile/Tablet) — same toolbar UI
   - summary cards → TOTAL VISITS / UNIQUE IPS / PAGES VISITED / TRACKED TODAY (same 4-card layout, existing icons)
   - CRUD: Add IP (create), Edit (update), Delete (delete) on `ip_activity` rows; toasts; `load()` refresh
   - export → tracking CSV
3. **`useVisitorTracking.ts`** — fire the beacon on route changes (`usePathname`) with a last-path ref to dedupe rerenders / Strict Mode / remounts. Non-blocking.
4. **`ip-address/page.test.tsx`** — update to new column/placeholder bindings (still asserts the single table + management heading).

## 4. Constraints honored

- No new database table (only ALTER `ip_activity`).
- No duplicate APIs — extend `admin.api.ts` + existing GraphQL files.
- No UI/CSS redesign — same classes, layout, modals, buttons, loaders.
- Real backend data only — the page no longer reads `ipPolicies` as its primary dataset; no static/mock visitor rows.
- Auth unchanged — tracking open `.uris` no-login; admin CRUD via `require_admin`.
- Tracking failures never break the website (try/catch, sendBeacon/fetch keepalive, middleware exception guard).

## 5. Implementation status

**Completed.** Final alembic head is now `f7c1e6a3b4d5` (applied to the dev DB,
54 existing rows backfilled from `metadata_json`, `visit_count=1`). No new
tables were created.

| Item | Status | Evidence |
| --- | --- | --- |
| Plan created before implementation | ✅ | This file |
| Model: `path` + `visit_count` added to `IPActivity` | ✅ | `models/ip_activity.py` |
| Migration `f7c1e6a3b4d5` (ALTER only, backfill, index) | ✅ | `alembic/versions/f7c1e6a3b4d5_add_ip_tracking_fields.py`, applied |
| `record_ip_activity` upsert + 60 s dedupe + `visit_count` | ✅ | `services/ip_tracking.py` |
| Middleware action unified to `page_view` | ✅ | `middleware/ip_tracking.py` |
| Admin repo/service CRUD (`get/create/update/delete_activity`) | ✅ | `admin/repositories/ip_activity_repository.py`, `admin/services/ip_activity_service.py` |
| GraphQL `IPActivityType.path` + `visit_count` | ✅ | `admin/api/graphql/types/ip_activity.py`, verified `visitCount: Int!` in schema |
| GraphQL `createIpActivity` / `updateIpActivity` / `deleteIpActivity` wired into `AdminMutation` | ✅ | `admin/api/graphql/mutations/ip_activity.py`, `mutations/__init__.py`, `schema.py` |
| Pydantic `IPActivityResponse` fields | ✅ | `schemas/admin/ip_activity.py` |
| Backend tests | ✅ | `pytest src/app/tests/test_admin_ip_activity.py` → 4 passed; full suite 146 passed |
| Backend lint | ✅ | `ruff check` clean on all touched files |
| Frontend `admin.api.ts` activity API | ✅ | `listIpActivity`, `createIpActivity`, `updateIpActivity`, `deleteIpActivity` + `AdminIpActivity` type |
| `AdminIpPage.tsx` rebound to tracking data | ✅ | columns IP/Device/OS/Browser/Visited Page/Visits/Last Visited/Actions; device filter; TOTAL VISITS/UNIQUE IPS/PAGES VISITED/TRACKED TODAY; CRUD; CSV export; all `ip-exact-*` classes preserved |
| Route-change visitor tracking | ✅ | `useVisitorTracking.ts` uses `usePathname` + last-path ref dedupe (Strict Mode safe) |
| Frontend test updated | ✅ | `ip-address/page.test.tsx` passes |
| Frontend lint / tsc | ✅ | Changed files lint-clean; tsc has only pre-existing errors in `AdminCustomersPage.tsx`/`AdminProductsPage.tsx` (untouched by this task) |
| Full jest suite | ✅ | 105 passed; only pre-existing failures remain (`landingPage.test.tsx`, `CategoryNav.test.tsx` fail on original code; `PublicHeader.test.tsx` is flaky — passes standalone) |

### How it was verified

- `python -m pytest src/app/tests/test_admin_ip_activity.py -q` → 4 passed.
- `python -m pytest -q` (backend full) → 146 passed.
- `ruff check` on all touched backend files → clean.
- Admin GraphQL schema builds and exposes `visitCount: Int!`.
- `npx eslint` on `AdminIpPage.tsx`, `admin.api.ts`, `useVisitorTracking.ts`, `page.test.tsx` → clean.
- `npx jest app/admin/ip-address/page.test.tsx` → passed (matches existing minimal admin test style).
- `npx tsc --noEmit` → no errors in any file touched by this task.
- No new tables: only `ALTER TABLE ip_activity` via migration.
- `ip_policies` and the policy CRUD APIs left fully intact.