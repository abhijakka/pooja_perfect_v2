# ipplan.md — PONYTAIL ULTRA: Admin React IP Address Table

## Summary

The frontend Admin **IP Addresses** page (`/admin/ip-address`) is rendered by a single
component that contains **two React `<table>` elements**. This plan identifies both
tables, removes the FIRST (the **Visitor activity log**), keeps the SECOND (the
**IP Address Management / IP policies** table), and keeps the SECOND table connected
to the existing backend IP APIs. No UI/CSS/design of the SECOND table is changed.

---

## 1. Location of FIRST React table

**Removed table.** "Visitor activity log" table.

- File: `frontend/app/admin/components/AdminIpPage.tsx`
- JSX section: `section.ip-exact-panel` at lines 340–412 (table columns: IP Address, Browser, Device, OS, Action, Page, Visited).
- Data source: `adminApi.listIpActivity(...)` → backend `ip_activity` GraphQL query.

It is the second panel in DOM order, but it is the "first candidate" that must be
removed (it duplicates what the separate `/admin/logs` "Activity Logs" page already
covers, and it is read-only — it can never be the CRUD IP table the task requires to
keep). The task's kept table must support modals/filters/CRUD (per task STEP 7/STEP 13),
which only the IP Policies table supports.

## 2. Location of SECOND React table

**Kept table.** "IP Address Management" (IP policies) table.

- File: `frontend/app/admin/components/AdminIpPage.tsx`
- JSX section: `section.ip-exact-panel` at lines 266–338 (table columns: IP Address, Location, Region, Status, Note, Created, Updated, Actions).
- Wrapper UI that stays: heading "IP Address Management", Export / Add IP / Refresh buttons, summary cards (TOTAL / ACTIVE / BLOCKED / WHITELISTED), search toolbar, status filter, empty state, pagination bar, and the View/Edit/Delete + Create/Edit/Delete-confirm modals.
- Data source: `adminApi.listIpPolicies()` + `createIpPolicy` / `updateIpPolicy` / `deleteIpPolicy`.

## 3. Components used by both

- `AdminIpPage.tsx` is the only component. Both tables live inside it. Shared shell: `AdminHeader`, `AdminSidebar`, `AdminIcon`, `AdminIconSprite`, `admin-dashboard`/`admin-main`/`admin-content` layout, and `coupon-exact-toast` toast.

## 4. API files currently used by both

- `frontend/services/api/admin.api.ts` (the project's single admin API service; the shared `adminGraphqlClient` from `services/api/client.ts` performs the authorized requests).

## 5. Backend endpoints used by each

- FIRST (removed) table → `listIpActivity` → admin GraphQL query `ipActivity`.
- SECOND (kept) table → `listIpPolicies` → admin GraphQL query `ipPolicies`; `createIpPolicy` / `updateIpPolicy` / `deleteIpPolicy` mutations.

Both are mounted on the Admin GraphQL endpoint `/admin/graphql` (see `backend/src/app/admin/api/graphql/schema.py`).

## 6. Backend model/table supplying the data

- FIRST (removed) table ← `IPActivity` model, table `ip_activity` (`backend/src/app/models/ip_activity.py`).
- SECOND (kept) table ← `IPPolicy` model, table `ip_policies` (same model file, lines 28–39).

No new backend models/tables are created and none are removed.

## 7. Fields returned by the backend

- `IPPolicy` (`IPPolicyType`): `id`, `ip_address`, `status`, `location`, `region`, `note`, `created_by_id`, `created_at`, `updated_at`.
- `IPActivity` (`IPActivityType`): `id`, `user_id`, `ip_address`, `action`, `user_agent`, `metadata_json`, `created_at`, `updated_at`, plus derived `browser`, `browser_version`, `os`, `os_version`, `device`, `device_type`, `path`, `screen`, `referrer`, `is_mobile`.

Backend enums (`backend/src/app/models/enums.py`): `IPPolicyStatus` = `active` | `blocked` | `whitelisted` — already matches the frontend `IpStatus` union.

## 8. CRUD operations currently implemented

- FIRST (removed) table: READ only (list activity, paginated). No CRUD.
- SECOND (kept) table: full CRUD — READ (`listIpPolicies`), CREATE (`createIpPolicy`), UPDATE (`updateIpPolicy` + block/unblock via `updateIpPolicy`), DELETE (`deleteIpPolicy`). Search + status filter run client-side over the full backend list; pagination is client-side UI + backend total (= list length since policies are returned whole).

## 9. Duplicate functionality found

- The "Visitor activity log" on the IP Addresses page duplicates the `/admin/logs` "Activity Logs" page (which already lists events with IP addresses via `listActivityLogs`). It consumes a second IP API (`ipActivity`) and a second IP type (`AdminIpActivity`) that are used by nothing else.
- There is no static/mock IP data in the current data flow — both tables read real backend data. The only static visuals are decorative (policy pagination page buttons, summary card labels), which are part of the kept table's UI and must be preserved.

## 10. Which component will be removed

- The **Visitor activity log** `<section>` (and its exclusive state/handlers/helpers) inside `AdminIpPage.tsx`; plus the exclusively-used API members `listIpActivity` and `AdminIpActivity` in `admin.api.ts`.
- `app/admin/components/AdminIpPage.tsx` and the route `app/admin/ip-address/page.tsx` remain (they host the kept SECOND table).

## 11. Which component will remain

- The **IP Address Management (IP policies)** table plus its full surrounding UI (actions, summary, toolbar, filter, table, pagination, view/form/delete modals, toast) with all CRUD wired to the backend `ipPolicies` endpoints.

## 12. How the SECOND table will be connected

- Already connected to the backend; the plan keeps that connection and removes only the activity-log wiring:
  - READ: `adminApi.listIpPolicies()` → maps backend `AdminIpPolicy` fields (`ipAddress` → `ip`, `status`, `location`, `region`, `note`, `createdAt`, `updatedAt`).
  - CREATE: form modal → `adminApi.createIpPolicy(ip, status, location, region, note)`.
  - UPDATE: edit modal + block/unblock → `adminApi.updateIpPolicy(id, status, note)`.
  - DELETE: delete modal → `adminApi.deleteIpPolicy(id)`.
  - All mutations re-run `load()` to refresh the table; failures surface via the existing toast.

## 13. Files to modify

- `frontend/app/admin/components/AdminIpPage.tsx` — remove activity-log section + its exclusive state/hooks/helpers; simplify the initial load to `listIpPolicies` only.
- `frontend/services/api/admin.api.ts` — remove `listIpActivity` and the `AdminIpActivity` type (used exclusively by the removed table).
- `ipplan.md` — updated after implementation (STEP 15).

## 14. Files to delete

- No files are deleted. (The route `app/admin/ip-address/page.tsx`, the component, CSS in `app/admin/styles/admin_style.css`, and backend files all stay.)

## 15. UI preservation requirements

- Do NOT change any CSS, colors, fonts, layout, table design, columns, buttons, icons, search/filter/pagination design, modal/form design, loader CSS, or responsive behavior of the kept SECOND table.
- Nothing outside the IP Addresses page and its exclusively-owned API helpers is touched (no navbar, sidebar, dashboard, product/order/user pages, global or loader CSS).

## 16. Testing plan

- **Static checks:** `npm run lint` and `npx tsc --noEmit` (or build) must pass.
- **Frontend tests:** run the existing Jest suite; add/confirm an IP Addresses route render test like the hero/reviews admin tests (columns and controls remain).
- **Backend tests:** run `test_admin_ip_activity.py` to confirm the IP APIs (list policies/activity + CRUD mutations) still pass unmodified.
- **Manual CRUD (documented in ipplan.md after implementation):**
  - READ: page opens → `ipPolicies` loads → policies table shows real records.
  - CREATE: Add IP → `createIpPolicy` → table refreshes with the new record.
  - UPDATE: Edit / Block-Unblock → `updateIpPolicy` → table refreshes.
  - DELETE: Delete → `deleteIpPolicy` → record removed from table.
  - SEARCH/FILTER: typo-filter and status filter operate over the backend list.
  - PAGINATION: pagination bar reflects the backend list length.
  - ERROR handling: backend down (empty state), unauthorized (401 from `require_admin`), duplicate IP (backend `DuplicateResourceError`), validation failure (note/toast) — no fake success.
- **Auth:** Admin GraphQL is permission-gated by `require_admin` in `backend/src/app/admin/context.py`; requests use `credentials: "include"` cookie auth (no new auth system).

Implementation status will be recorded at the bottom of this file after STEP 15.

---

# IMPLEMENTATION COMPLETED

## Files changed

| File | Change |
| --- | --- |
| `frontend/app/admin/components/AdminIpPage.tsx` | Removed the FIRST table (Visitor activity log) and all code used only by it; kept the SECOND table (IP Address Management) with its full CRUD, modals, filters, pagination and UI unchanged. Simplified the initial load to `listIpPolicies` only and extracted a `toIpPolicy` mapper shared by the initial load and `load()`. |
| `frontend/services/api/admin.api.ts` | Removed the `AdminIpActivity` type and `listIpActivity()` function (used only by the removed table). Kept `AdminIpPolicy`, `listIpPolicies`, `createIpPolicy`, `updateIpPolicy`, `deleteIpPolicy`. |
| `frontend/app/admin/ip-address/page.test.tsx` | Added a route render test asserting the IP Addresses page renders its single IP policy table and not the removed activity-log search. |
| `ipplan.md` | This file — completion status recorded. |

No files were deleted. No backend files were modified. No CSS was changed.

## STEP checklist

| Check | Status | Evidence |
| --- | --- | --- |
| FIRST table (Visitor activity log) removed | ✅ | `AdminIpPage.tsx` has no activity section; grep for `listIpActivity`, `AdminIpActivity`, `Visitor activity`, `activityQuery`, `filteredActivity`, `uniqueIps`, `mobileVisits`, `deviceIcon`, `actionLabel`, `formatTime`, `ActivityRecord` → 0 matches. |
| SECOND table (IP Address Management) kept | ✅ | Exactly one `ip-exact-table` remains (`AdminIpPage.tsx:192`); `/admin/ip-address` routes to it. |
| SECOND table connected to real backend IP APIs | ✅ | `listIpPolicies` (READ), `createIpPolicy` (CREATE), `updateIpPolicy` (UPDATE + block/unblock), `deleteIpPolicy` (DELETE) all called from `AdminIpPage.tsx`, hitting admin GraphQL `ipPolicies`/`createIpPolicy`/`updateIpPolicy`/`deleteIpPolicy`. |
| Duplicate/mock IP tables removed | ✅ | Only one `<table>` on the page; the activity log (which duplicated `/admin/logs`) is gone; no static IP dataset remains in the data flow. |
| No exclusively-used API members left behind | ✅ | The policy CRUD functions are referenced only by `AdminIpPage.tsx`; the activity members were removed. |
| UI/CSS/design of the kept table unchanged | ✅ | Kept JSX is byte-identical for heading, Export/Add IP/Refresh actions, summary cards, search toolbar, status filter, 8 table columns, empty state, pagination, and the View/Form/Delete modals. No CSS touched. |
| Unrelated pages/CSS untouched | ✅ | Changes confined to `AdminIpPage.tsx`, `admin.api.ts`, the new route test, and this plan. |
| Lint | ✅ | `npx eslint app/admin/components/AdminIpPage.tsx services/api/admin.api.ts app/admin/ip-address/page.tsx app/admin/ip-address/page.test.tsx` → exit 0. |
| TypeScript (IP files) | ✅ | `npx tsc --noEmit` reports **no** errors in any IP-related file. |
| TypeScript (whole project) | ⚠️ | Pre-existing errors remain in untouched `app/admin/components/AdminCustomersPage.tsx` and `AdminProductsPage.tsx` (missing `createCustomer`/`updateCustomer`/`deleteCustomer`/`updateCustomerNotes`/`uploadProductImage`/`removeProductImage` in `admin.api.ts`). Out of scope for this task; not introduced by these changes. |
| Frontend Jest suite | ⚠️ | Could not execute in this environment. The modified Next.js `next/jest` loader fails at setup (`Cannot find module '@testing-library/jest-dom'` / `Can't resolve main package.json file`) for **all** suites, including untouched `hero`/`reviews` tests, so it is a pre-existing infra issue. The new `ip-address/page.test.tsx` is written but unexecuted. |
| Backend tests | ⚠️ | Not executed. No backend file was changed; the IP GraphQL queries/mutations and models are untouched. |
| Manual end-to-end CRUD | ❌ | Not executed (requires a running backend + frontend). Handlers were verified by static review only. |

## Manual CRUD test matrix (to run against the live app)

| Case | Expected |
| --- | --- |
| Open `/admin/ip-address` | `ipPolicies` loads; the single IP Address Management table shows real records (or the existing empty state). |
| Add IP → submit | `createIpPolicy` succeeds; modal closes; toast "IP policy created successfully"; table refreshes. |
| Edit → Save Changes | `updateIpPolicy` succeeds; toast "IP policy updated successfully"; table refreshes. |
| Block / Unblock row action | `updateIpPolicy` with status `blocked`/`active`; toast reflects the change; table refreshes. |
| Delete → Delete Policy | `deleteIpPolicy` succeeds; toast "<ip> deleted"; record disappears. |
| Search / status filter | Filters the backend list client-side; count updates in the toolbar. |
| Pagination | Reflects the backend list length. |
| Backend down | Existing empty state; errors surface via the existing toast (no fake success). |
| Unauthorized | 401 from `require_admin`; no data mutation. |

## Notes

- The FIRST/SECOND naming was mapped by capability (per STEP 7/13): the kept table is the **IP Address Management / IP policies** table because it is the one with CRUD, modals and filters; the removed table is the read-only **Visitor activity log** (which duplicates the `/admin/logs` page).
- Git state note: a `git stash`/`git stash pop` baseline check mid-task briefly left conflict markers in the working tree. This was fully recovered by restoring the working tree from the (dangling) stash commit tree; the final repository contains no conflict markers and the task files are correct.





