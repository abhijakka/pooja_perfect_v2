# Frontend API Deep Audit & Implementation Plan

> Created **before** any implementation. Based on a full recursive inspection of `frontend/` and the implemented backend API surface (`backend/src/app/`).

---

## 1. Current API Architecture

### API folder
`frontend/services/api/` — the only API folder. Contains **13 files**, all stubs:

| File | Content |
|------|---------|
| `client.ts` | `apiClient<T>(_path, _init)` → `throw new Error("API client is not configured")` |
| `client.test.ts` | Asserts the client throws until configured |
| `auth.api.ts` | `export const authApi = {}` |
| `products.api.ts` | `export const productsApi = {}` |
| `categories.api.ts` | `export const categoriesApi = {}` |
| `cart.api.ts` | `export const cartApi = {}` |
| `wishlist.api.ts` | `export const wishlistApi = {}` |
| `orders.api.ts` | `export const ordersApi = {}` |
| `checkout.api.ts` | `export const checkoutApi = {}` |
| `payment.api.ts` | `export const paymentApi = {}` |
| `subscription.api.ts` | `export const subscriptionApi = {}` |
| `chat.api.ts` | `export const chatApi = {}` |
| `coupon.api.ts` | `export const couponApi = {}` |
| `admin.api.ts` | `export const adminApi = {}` |

**None of these stubs are imported anywhere** in the frontend (verified by recursive search).

### API client structure
- `services/api/client.ts` is a single throw-away stub. No axios, no fetch wrapper, no interceptors, no base URL handling.
- `config/environment.ts` exposes `environment.apiUrl` from `NEXT_PUBLIC_API_URL` (empty by default — **no `.env*` files exist**).

### Authentication flow
- Redux slice `store/slices/authSlice.ts` holds `{ user: Customer | null, isAuthenticated }` with `setUser`/`logout` reducers. **No API calls.**
- `hooks/useAuth.ts` reads the slice via `useAppSelector`.
- No token storage, no refresh logic, no interceptors, no Authorization headers anywhere.
- `app/(auth)/login` and `app/(auth)/signup` simulate success with `window.setTimeout` — no real request.

### Public/admin API separation
- None. No public or admin API files are implemented.

### Existing API conventions
- Naming: `<domain>.api.ts` exporting a single `xxxApi` object.
- No established request/response typing (types are minimal and don't match the backend).

### Backend API surface actually implemented (`backend/src/app/`)
Only auth is real. Everything else is planned (GraphQL via Strawberry, not yet built):

| Endpoint | Method | Request | Response |
|----------|--------|---------|----------|
| `/auth/register` | POST | `SignupInput` | `UserResponse` (201) |
| `/auth/login` | POST | `LoginInput` | `TokenResponse` |
| `/auth/refresh` | POST | `RefreshTokenInput` | `TokenResponse` |
| `/auth/logout` | POST | `RefreshTokenInput` | 204 |
| `/auth/me` | GET | Bearer token | `UserResponse` |
| `/auth/google` | POST | `OAuthLoginInput` | `TokenResponse` |
| `/webhooks/payment` | POST | — | — |
| `/graphql` | POST | admin GraphQL | — |
| `/health` | GET | — | — |

---

## 2. APIs Found Outside API Folders

**None.** Recursive search across all `.ts`/`.tsx`/`.js`/`.jsx` for `axios`, `fetch(`, `XMLHttpRequest`, `/api/`, `http://`, `https://`, `baseURL`, `Authorization`, `Bearer`, `.get(`, `.post(`, `.put(`, `.patch(`, `.delete(` found **zero** API calls. Pages/components/hooks use mock data (`storefront-data.ts`) and `window.setTimeout` to simulate latency. There is nothing to migrate into the API folder.

---

## 3. Existing API Duplicates

**None.** The 12 API stubs are never imported or referenced anywhere. No duplicate endpoints, clients, or functions exist.

---

## 4. New API Files Required

Only what the implemented backend actually supports. Everything else is YAGNI (backend endpoints don't exist yet).

| File | Action | Reason |
|------|--------|--------|
| `services/api/client.ts` | **Implement** (exists as stub) | Foundation for all requests; currently throws |
| `services/api/auth.api.ts` | **Implement** (exists as stub) | Backend auth API is real and tested (18 backend tests pass) |
| `types/auth.ts` | **Create** | Auth request/response contracts matching backend schemas |

**Deliberately left as stubs** (backend has no such endpoints yet): `products`, `categories`, `cart`, `wishlist`, `orders`, `checkout`, `payment`, `subscription`, `chat`, `coupon`, `admin`. Creating them now would be speculative.

---

## 5. Files That Need Migration

**None.** No page/component/hook/service contains API logic to migrate. The auth pages use mock timeouts, not API calls. Wiring them to the real API would break the standalone demo because `NEXT_PUBLIC_API_URL` is empty by default — this violates the "preserve existing functionality" rule. Documented as a next step, not done now.

---

## 6. API Architecture Rules

- **Client**: single `apiClient<T>(path, init, token?)` in `services/api/client.ts`. Uses native `fetch` (no axios — no new dependency). Reads `environment.apiUrl`. Throws a clear `ApiError` on HTTP errors; throws "API client is not configured" when no base URL is set (preserves existing behavior/test).
- **Naming**: keep existing `<domain>.api.ts` + `xxxApi` object convention.
- **Auth**: `authApi` functions pass the access token to `apiClient` for protected calls (`me`). No token storage/interceptors yet — not needed until pages are wired.
- **Types**: new auth types live in `types/auth.ts` following the existing `types/` folder convention. Reuse `types/api.ts` only if it matches the backend contract — it does not (backend returns raw JSON, not `{data, error}`), so auth types are standalone.
- **Error handling**: `ApiError` carries `status` + backend `detail` (FastAPI returns `{"detail": ...}`). Network errors propagate as-is.
- **Exports/imports**: import alias `@/*` → project root (tsconfig `paths`). API files import the client via relative path (existing convention in `client.test.ts`).

---

## 7. Validation Plan

- **TypeScript**: `npx tsc --noEmit` (or `npm run build` which type-checks).
- **Lint**: `npm run lint` (eslint).
- **Tests**: `npx jest --silent` — existing `client.test.ts` must still pass; new `auth.api.test.ts` added.
- **Build**: `npm run build`.
- **API audit**: re-run recursive search for `axios`, `fetch(`, `/api/`, `Authorization`, `Bearer`, `baseURL` — confirm no new scattered API calls and no duplicates.
- **Import check**: verify no broken/unused imports after changes.

---

## Review Notes (Phase 3)

- Plan is consistent with the actual frontend: API folder exists but is 100% stubs; zero API usage anywhere; backend only implements auth.
- No redesign of project architecture. Existing `services/api/` layout and `xxxApi` naming are preserved.
- Scope is intentionally minimal (Ponytail Ultra): implement only the client + auth API, the only pieces the backend supports.