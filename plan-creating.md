# Plan — Fix Authentication Persistence

Derived from `bug-authentication.md`. Goal: a logged-in customer stays logged in across
navigation, direct URLs and browser refresh, while the public browse/cart/purchase flow and
admin authentication keep working.

Constraint set held throughout: **one** JWT system (HttpOnly cookies + PyJWT, unchanged),
**one** auth provider (`app/providers.tsx`, no new context), no cookie attribute changes, no
CORS changes, no `localStorage` token copy, no route-protection removal, no CSS.

---

## Step 1 — Backend: public GraphQL must read the auth cookie  (ROOT CAUSE)

`backend/src/app/dependencies/auth.py`
- Extract the Bearer-header-then-cookie resolution that `get_current_user` already performs
  (lines 32-36) into one reusable helper.
- `get_current_user` and `require_admin` call the helper. Behaviour is byte-for-byte identical.

`backend/src/app/public/dependencies.py`
- `get_optional_current_user` takes `Request` and, when no `Authorization` header is present,
  falls back to `request.cookies["access_token"]` via the shared helper.
- Keeps returning `None` on missing/expired/invalid tokens so the public catalog and guest
  cart keep working for anonymous visitors.

Acceptance: with only the cookies present, `currentUser` / `addresses` / `orders` / `wishlist`
/ `notifications` return data for a logged-in customer, and `/graphql { cart }` returns the
customer's own cart rather than a fresh guest cart.

## Step 2 — Backend: make `/auth/refresh` and `/auth/logout` cookie-callable

`backend/src/app/api/auth.py`
- Declare the request body explicitly optional on both endpoints so the existing
  `or request.cookies.get("refresh_token")` fallback is reachable (today both return 422 when
  called with no body, which is exactly how `services/api/auth.api.ts` calls them).
- `_extract_access_token` delegates to the Step 1 helper.

Acceptance: `POST /auth/refresh` with cookies only → 200 + rotated cookies;
`POST /auth/logout` with cookies only → 204 + `Set-Cookie` deletions + refresh token revoked
(a follow-up refresh with the same token returns 401).

## Step 3 — Frontend: refresh once before ending the session

`frontend/services/api/client.ts`
- Add a module-level session-refresher hook, mirroring the existing
  `setUnauthorizedHandler` slot, plus a single-flight promise so a burst of concurrent 401s
  triggers exactly one `POST /auth/refresh`.
- On an auth failure (HTTP 401 or an auth-flavoured GraphQL error), attempt the refresh and
  replay the original request once. Call `notifyUnauthorized()` only when the refresh itself
  fails. Bound the retry so it cannot recurse.
- No change to `PUBLIC_AUTH_PATHS`, `credentials`, or the absence of a `Bearer` header.

Acceptance: a request rejected because the access token expired succeeds after one silent
refresh; `notifyUnauthorized` fires only when the refresh is rejected.

## Step 4 — Frontend: replace the expiry logout with proactive refresh

`frontend/app/providers.tsx`
- Register `setSessionRefresher` → `authApi.refresh()` → dispatch the new `expires_at`.
- `endSession` returns immediately when `isAuthenticated` is false, so an anonymous visitor's
  expected `401` from `/auth/me` can no longer bounce them off a public page.
- The `restoreSession` catch redirects only when a session actually existed.
- Swap the 1-second expiry interval for one `setTimeout` ~60 s before `accessTokenExpiresAt`.
- `isReady` semantics are untouched, so the Loading / Unauthenticated distinction that
  `(account)/layout.tsx` and `admin/layout.tsx` rely on is preserved.

Acceptance: a session older than 30 minutes keeps working; a browser refresh with an expired
access token recovers silently via the `/auth/me` retry; an anonymous visitor deep-linking to
`/products` stays on `/products`.

## Step 5 — Frontend: correct the account GraphQL query

`frontend/services/api/account.api.ts`
- `current_user` → `currentUser`, `page_size` → `pageSize`, and the `AddressType`,
  `OrderType`, `OrderItemType` fields to their real camelCase names. Update the response types
  to match.

Acceptance: `accountApi.getOverview()` returns data instead of 11 schema validation errors, so
My Account and My Orders render.

---

## Verification order

```
 1. backend pytest src/app/tests                     -> 226 still pass
 2. scripted browser re-run of the reproduction     -> no "Authentication required" with cookies only
 3. login  -> home -> products -> category -> detail -> cart -> my-account -> my-orders
                                                     -> still authenticated at every step
 4. direct URLs /products /cart /my-account /my-orders-> still authenticated
 5. browser refresh on each of the above             -> still authenticated
 6. force access-token expiry, then any request     -> silent refresh, session survives
 7. explicit logout                                 -> cookies cleared, refresh revoked,
                                                       My Account / My Orders unreachable
 8. anonymous visitor: home -> products -> detail -> add to cart -> cart -> checkout
 9. admin login -> dashboard -> admin pages -> refresh-> still authenticated
10. frontend npm test / lint / tsc --noEmit          -> no new failures
```

## Files

| File | Step |
|---|---|
| `backend/src/app/dependencies/auth.py` | 1 |
| `backend/src/app/public/dependencies.py` | 1 |
| `backend/src/app/api/auth.py` | 2 |
| `frontend/services/api/client.ts` | 3 |
| `frontend/app/providers.tsx` | 4 |
| `frontend/services/api/account.api.ts` | 5 |

## Out of scope

Cookie attributes, CORS, `authSlice`, `useAuth`, `hooks/useAuth.test.ts`, the route guards,
`auth.api.ts`, header/footer components, every admin page, all CSS, and the two pre-existing
chat test failures.
