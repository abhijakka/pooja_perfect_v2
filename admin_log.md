# PonyTail Ultra — Enhanced Activity Log

## Phase 1 — Plan (created BEFORE implementation)

This document is created before implementation. It defines the
SUCCESS / WARNING / ERROR classification rules and the description rules that the
global activity-logging middleware must follow. It is updated AFTER verified
completion with the deployed architecture, integration details and test results.

---

## Objectives

Replace the database-backed admin audit trail with a **global, file-based
activity log** that records a meaningful description for every request:

| Requirement | Notes |
| --- | --- |
| Global middleware | A single Starlette `BaseHTTPMiddleware` registered on the FastAPI app |
| Daily log files | `logs/pooja_DD_MM_YYYY.log`, one file per day |
| No database log table | No `ActivityLog` model / table anywhere in the stack |
| No duplicate logging | The admin logs API reads the same daily files the middleware writes |
| Meaningful descriptions | Every entry answers *"What happened?"* |
| Existing `AdminLogsPage` | UI preserved; only the data mapping is updated |
| No secrets | Passwords, JWT/refresh tokens, API keys, headers, payloads are never logged |

## Level classification

Every request is classified exactly once. Levels use the project-equivalent names
so the existing admin UI and `AuditLevel`-style consumers keep working:

| Level | Meaning | Default HTTP mapping |
| --- | --- | --- |
| `info` → **SUCCESS** | Operation completed as expected | `200, 201, 202, 204` |
| `warning` → **WARNING** | Request reached the app but needs attention (client/request condition) | `400, 401, 403, 404, 409, 422, 429` |
| `error` → **ERROR** | A server/application failure occurred | `500, 502, 503, 504` |
| `security` → **SECURITY** | Blocked / restricted security events (reserved for admin-manual entries) | n/a |

Rules:

1. Started from the HTTP status code (2xx / 4xx / 5xx).
2. For **GraphQL** requests the HTTP status is almost always `200`, so the response
   body is inspected for an `errors` array; each error's ``extensions.code``
   (an HTTP status code raised by `AppError`) is used to re-classify:
   - code `>= 500` → `error`
   - code `4xx` → `warning`
   - error with no code (unhandled exception) → `error`
3. A business operation that fails with a 4xx is logged as **WARNING** with an
   accurate description — never as SUCCESS, never blindly as ERROR.

## Description rules

Every log entry's `DESCRIPTION` line must be prefixed with the level word and must
answer **what happened**, e.g.

```text
SUCCESS - Admin created product successfully via createProduct
WARNING - Order 999 was not found (HTTP 404)
ERROR - Failed to create order because the database operation failed
```

- **SUCCESS** descriptions name the actor, the resource and the verb
  (`loaded`, `created`, `updated`, `deleted`, `logged in`, `logged out`).
- **WARNING** descriptions name the reason (`invalid credentials`,
  `resource not found`, `unauthorized access attempt`, `invalid request parameters`,
  `rate limit reached`).
- **ERROR** descriptions name what failed and the error type / status
  (`internal server error`, `database operation failed`, `authentication service failed`).
- Generic text such as `Request completed`, `Something happened`, `Error occurred`
  is forbidden.

## Log entry structure

Every entry contains, where available: date, time, level, IP, HTTP method, path,
status code, user/guest, action, source and description.

```text
[18-09-2026 04:25:31] SUCCESS
ID: <uuid>
DATE: 18-09-2026
TIME: 04:25:31
IP: 192.168.1.25
METHOD: POST
PATH: /admin/graphql
STATUS: 201
USER: admin
ACTION: Product created
SOURCE: Catalog
RESOURCE: product
RESOURCE_ID: 123
DESCRIPTION: SUCCESS - Admin created product successfully via createProduct
```

The first line carries the human-readable timestamp and level; the rest are
`KEY: VALUE` lines so the admin API can parse them reliably.

## Sensitive-data sanitization

- The middleware never logs request bodies, variables, headers, cookies or tokens.
- For GraphQL the **operation name / first field name** is derived only; variables
  are ignored.
- A "safe error message" is limited to the error type / HTTP status — never a raw
  exception message, token, key or payload.
- All stored values are stripped of newlines and capped in length.

## Execution flow

```text
AUDIT → CREATE admin_log.md → GLOBAL MIDDLEWARE → CLASSIFY → DESCRIBE
      → DAILY LOG FILE → ADMIN LOG API → EXISTING AdminLogsPage → TEST → UPDATE admin_log.md
```

---

## Phase 2 — Completion report (updated AFTER verified implementation)

Status: **complete and verified**.

### Deployed components

| Component | Path | Role |
| --- | --- | --- |
| Global middleware | `backend/src/app/middleware/activity_log.py` | Classifies every request and appends one entry |
| File store | `backend/src/app/core/activity_logging.py` | Classification, description builder, daily-file CRUD |
| Config | `backend/src/app/config.py` | `activity_log_dir` (default `<repo>/logs`), `activity_log_enabled` |
| Admin query | `backend/src/app/admin/api/graphql/queries/logs.py` | Reads the daily files (newest first, filters) |
| Admin mutations | `backend/src/app/admin/api/graphql/mutations/logs.py` | create / update / delete / clear, file-only |
| GraphQL type | `backend/src/app/admin/api/graphql/types/log.py` | Adds `method`, `path`, `user`, `source`, `statusCode` |
| Admin UI | `frontend/app/admin/components/AdminLogsPage.tsx` | UI preserved; maps the new fields |
| API client | `frontend/services/api/admin.api.ts` | Extended `AdminActivityLog` + field selection |

### No database log table

- Deleted `models/activity_log.py`, `admin/services/activity_log_service.py`,
  `admin/repositories/activity_log_repository.py`, `schemas/admin/activity_log.py`.
- Alembic revision `a3d9c2f4e6b1` (down_revision `f7c1e6a3b4d5`) drops `activity_logs`.
- The `AuditLevel` enum is retained for compatibility but is no longer used by logs.
- There is a single logging pipeline: the middleware writes files, the admin API reads them.

### Integration details and fixes found during verification

1. **Level round-trip.** The file header stores the human level word
   (`SUCCESS` / `WARNING` / `ERROR` / `SECURITY`); the parser maps it back to the
   internal `info` / `warning` / `error` / `security` level via `_LEVEL_BY_WORD`.
2. **GraphQL streaming responses.** Strawberry's `GraphQLRouter` returns a
   streaming response, so `response.body()` raises. The middleware buffers the body
   from `body_iterator` before inspecting GraphQL `errors` and re-streams it.
3. **Unhandled exceptions.** `dispatch` catches exceptions from `call_next`, records
   an `ERROR` entry with status `500`, then re-raises so Starlette still returns 500.
4. **Status vs status code.** The GraphQL `status` field stays the display word used
   by the existing badge (`Success` / `Warning` / `Failed` / `Blocked`); the raw HTTP
   code is exposed as `statusCode` and shown next to `METHOD PATH` in the Activity cell.
5. **Timestamp hygiene.** Files and entries use UTC (`datetime.now(tz=UTC)`), matching
   the project's existing `models/base.py` convention.
6. **Admin list page size.** `AdminLogsPage` requested `pageSize: 200`, but
   `PaginationInput` caps `page_size` at `100`, so the query returned a validation
   error and the page silently rendered empty. The page now requests `100` and shows
   a toast if loading fails.

### Tests and verification

| Check | Command | Result |
| --- | --- | --- |
| Backend tests | `.venv\Scripts\python.exe -m pytest -q` | **157 passed** |
| New log tests | `pytest src/app/tests/test_admin_logs.py -q` | **17 passed** |
| Backend lint | `ruff check <changed files>` | clean |
| Backend types | `mypy <changed files>` | clean |
| Frontend lint | `eslint app/admin/components/AdminLogsPage.tsx services/api/admin.api.ts` | clean |
| Frontend types | `tsc --noEmit` | only pre-existing errors in `AdminCustomersPage` / `AdminProductsPage` (unrelated) |
| Frontend tests | `jest` | 3 pre-existing failures (`landingPage`, `PublicHeader`, `CategoryNav`: missing redux `Provider`), unrelated |

`test_admin_logs.py` covers: HTTP classification, GraphQL error classification,
meaningful SUCCESS/WARNING/ERROR descriptions, `pooja_DD_MM_YYYY.log` naming, the
health-check skip, unauthorized admin requests, the buffered GraphQL error path,
the admin list API (`statusCode`, `status`, `method`, `path`, `user`, `source`),
search/level filters, file-backed create/get/delete/clear mutations, and
newline sanitization.

### Known limitations

- Daily file names and entry timestamps use UTC, so the file rolls over at UTC midnight.
- The admin API lists, mutates and clears **today's** file only.
- `SECURITY` remains reserved for future admin-manual entries; the middleware never emits it.

### Runtime artifact

Daily files are written to `<repo>/logs/` and are ignored by the repository via a
root `.gitignore` entry (`logs/`).