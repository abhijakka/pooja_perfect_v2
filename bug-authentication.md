# Authentication Bug Investigation

**Status:** Root cause identified and **fixed**. Investigation performed against a live backend
with a real cookie jar that mimics the browser. Post-fix verification is in
[Testing Results](#testing-results).
**Stack verified from code:** Next.js `16.3.2` App Router (no `pages/`), React `19.2.8`,
TypeScript `strict`; FastAPI + Strawberry GraphQL (public `/graphql`, admin `/admin/graphql`) + REST `/auth/*`.
**Auth architecture in use:** HttpOnly **cookie** based. No token is ever readable by JavaScript.

> **Correction — read before relying on the historical claims below.**
> An earlier revision of this document reported that a **bodyless** `POST /auth/refresh` and
> `POST /auth/logout` both returned `422 Field required`. That was **wrong**, and it was an
> artefact of the test harness, not the application: the reproduction script sent a JSON body of
> `{}`, which legitimately 422s. The real pre-fix signatures were
> `data: RefreshTokenInput | None = None`, and FastAPI **does** treat that as an optional body.
> Proven against a minimal replica of the pre-fix signature:
> `no body -> 200` (cookie fallback reached), `{} -> 422`.
> The genuine logout defect is narrower and is described in
> [§ `/auth/refresh` and `/auth/logout`](#authrefresh-and-authlogout-are-broken-for-cookie-only-callers):
> the cookie deletions were applied to an injected `Response` that the handler then discarded.
> A second harness problem compounded it: port `8000` was held by a stale `uvicorn` process
> started before the edits, so "before" results must come from a freshly started server.


---

## Reproduction Steps

Exactly the scenario reported, executed as a scripted browser (Origin `http://localhost:3000`,
credentials `include`, one shared cookie jar, **no `Authorization` header ever sent** —
this is what the real app does, see §5):

```
1. Open application (anonymous)          -> products 200, cart 200, cookie guest_token set
2. Register + login as customer          -> HTTP 200, cookies access_token + refresh_token set
3. GET /auth/me                          -> HTTP 200  email=repro-auth@example.com   [SESSION IS VALID]
4. POST /graphql { currentUser { id email } }          -> HTTP 200 errors=['Authentication required']
5. POST /graphql { addresses { id } }                 -> HTTP 200 errors=['Authentication required']
6. POST /graphql { orders(page:1,pageSize:100) {...} } -> HTTP 200 errors=['Authentication required']
7. POST /graphql { wishlist { id } }                   -> HTTP 200 errors=['Authentication required']
8. POST /graphql { notifications(...) {...} }         -> HTTP 200 errors=['Authentication required']
```

Steps 4–8 are the queries `/my-account`, `/my-orders`, `/wishlist` and `/notifications` **need**.
They were issued directly by the reproduction script, because as shipped `/my-account` and
`/my-orders` never reached them: `accountApi.getOverview` was itself malformed and died in schema
validation first (see [Fifth](#fifth--the-account-query-is-malformed-so-my-account-and-my-orders-could-not-load-even-with-a-perfect-session)).
Every one of the five produces the GraphQL error message `Authentication required`,
which `services/api/client.ts:143` maps to `notifyUnauthorized()`, which
`app/providers.tsx:39` has bound to `endSession()` — a full logout plus `router.replace("/")`.

Verified cause-and-effect with the same cookies plus an explicit header:

```
POST /graphql { currentUser { id email } }  + Authorization: Bearer <token>  -> 200 data={'currentUser': {...}}
POST /graphql { orders(page:1,pageSize:100) } + Authorization: Bearer <token> -> 200 data={'orders': {'items': []}}
POST /graphql { wishlist { id } }             + Authorization: Bearer <token> -> 200 data={'wishlist': {...}}
```

Same browser, same cookies, same endpoint — the **only** difference is the header the frontend never sends.

## Current Behavior

```
Login
  ↓
Authentication succeeds (REST /auth/me → 200)
  ↓
User enters Homepage            (only public catalog + guest cart queries run → no auth error)
  ↓
User clicks My Orders / My Account / Wishlist
  ↓
POST /graphql → "Authentication required"
  ↓
client.ts:143 notifyUnauthorized()
  ↓
providers.tsx:32 endSession() → setSessionExpired + logout + router.replace("/")
  ↓
USER IS LOGGED OUT BY NAVIGATING
```

Additional reproduced failures, same session:

```
POST /auth/logout   (cookie only, no body) -> 204, but Set-Cookie: (none)
GET  /auth/me after that "logout"           -> 200   <- the browser still holds a live access token

POST /graphql { cart {...} }  cookie only   -> cart id 4f534566-b749-4fd6-821b-c94af34e42de
POST /graphql { cart {...} }  + Bearer      -> cart id 3926784e-bf3b-4115-a1f3-93671e87a939
                                            ↑ two different carts for one browser
```

`POST /auth/refresh` with **no body worked correctly before the fix** (HTTP 200, cookie fallback
reached). It is *not* part of the defect — see the correction note at the top of this document.
The logout failure above is real and is caused by the discarded `Response`, not by a 422.

## Expected Behavior

```
LOGIN → AUTHENTICATED SESSION → HOME → PRODUCTS → CATEGORY → PRODUCT DETAILS
      → CART → MY ACCOUNT → MY ORDERS → REFRESH → STILL AUTHENTICATED
```

with the public browse/cart/purchase flow and admin authentication left intact, and logout
happening only on explicit user action or on a genuinely unrecoverable session.

---

## Frontend Authentication Flow

There is **no** `AuthProvider`/auth context. `frontend/context/AuthContext/index.ts` is a
one-line placeholder (`export const AuthContext = {};`) and is imported nowhere. The real state
lives in Redux Toolkit.

| Concern | Location | Reality |
|---|---|---|
| Store | `frontend/store/index.ts:10` | `configureStore`, **no persistence** for `auth`; only `cart` + `wishlist` are written to `localStorage` (lines 24-33) |
| Auth slice | `frontend/store/slices/authSlice.ts` | `user, isAuthenticated, isReady, accessTokenExpiresAt, sessionExpired` |
| `useAuth` | `frontend/hooks/useAuth.ts:3-6` | thin selector over `state.auth` |
| Bootstrap | `frontend/app/providers.tsx:26-86` (`AuthBootstrap`) | the de-facto auth provider |
| Login page | `frontend/app/(auth)/login/page.tsx:42-71` | `authApi.login` → `setTokenExpiry` → `authApi.me` → `setUser` → `router.push("/")` or `/admin` |
| API wrapper | `frontend/services/api/auth.api.ts` | REST `/auth/*`, all with `credentials: "include"` |
| HTTP client | `frontend/services/api/client.ts` | `fetch` wrapper + global unauthorized handler |
| Logout | `frontend/app/(account)/my-account/page.tsx:103-105` | `authApi.logout()` then `dispatch(logout())` then `router.replace("/")` |

### Route guards

Both guards **already** distinguish Loading from Unauthenticated correctly — no change needed:

- `frontend/app/(account)/layout.tsx:11,16` — `if (!isReady) return;` and `if (!isReady || !isAuthenticated || user?.role_name !== "customer") return null;`
- `frontend/app/admin/layout.tsx:12,15` — same shape for `role_name !== "admin"`.

`Providers` is mounted once in the root layout and `const [store] = useState(makeStore)`
(`providers.tsx:89`) keeps the store instance stable, so **nothing remounts on navigation**.
The guards are not the problem.

### The unconditional logout

`frontend/app/providers.tsx:32-41`

```tsx
32  const endSession = useCallback(() => {
33      dispatch(setSessionExpired());
34      dispatch(logout());
35      if (!isAuthPage()) router.replace("/");
36  }, [dispatch, router]);
37
38  useEffect(() => {
39      setUnauthorizedHandler(endSession);
40      return () => setUnauthorizedHandler(undefined);
41  }, [endSession]);
```

`endSession` runs on **every** auth-failure signal from **any** endpoint, has no notion of
"was there even a session", and performs no refresh attempt first. `isAuthenticated` is not
in its dependency list and is not consulted.

Consequence for public users: on a cold load of `/products`, `restoreSession()`
(`providers.tsx:45-66`) calls `GET /auth/me`, which correctly 401s for an anonymous visitor.
`/auth/me` is **not** in `PUBLIC_AUTH_PATHS` (`client.ts:38`), so `notifyUnauthorized()` fires,
`endSession()` runs, and `isAuthPage()` is false on `/products` → `router.replace("/")`.
**An anonymous visitor deep-linking to a public page is bounced to the homepage.**

### The expiry logout (a second, independent logout)

`frontend/app/providers.tsx:75-83`

```tsx
75  useEffect(() => {
76      if (!isAuthenticated || accessTokenExpiresAt == null) return;
77      const interval = window.setInterval(() => {
78          if (Date.now() >= accessTokenExpiresAt) {
79              endSession();
80          }
81      }, 1000);
82      return () => window.clearInterval(interval);
83  }, [endSession, isAuthenticated, accessTokenExpiresAt]);
```

`access_token_expire_minutes = 30` (`backend/src/app/config.py:28`). **Exactly 30 minutes after
login the user is logged out**, even though a valid `refresh_token` cookie with a 30-day life
(`refresh_token_expire_days = 30`) is sitting in the browser.

`authApi.refresh` (`services/api/auth.api.ts:17-18`) is **never called anywhere in the app.**
A repo-wide search for `refresh` in `frontend/**/*.ts{,x}` returns only the API wrapper
definition, its unit test, unrelated icon names and unrelated UI labels. There is no refresh
endpoint call, no refresh interceptor, no refresh cookie read, no rotation handling, no
401-retry-queue. The entire token-refresh half of the architecture is unwired.

### API interceptor

`frontend/services/api/client.ts`

- `apiClient` (56-94) and `graphqlRequest` (112-147) attach `Authorization: Bearer` **only** if a
  third `token` argument is passed. A repo-wide search shows every call site passes 1–2 arguments,
  so **no request ever carries the header** — correct for a cookie architecture.
- `credentials: "include"` is correctly applied: `client.ts:71-76` for `/auth` and `/admin`
  REST paths, and `client.ts:130` for every GraphQL request.
- `notifyUnauthorized()` is invoked at three places, all with no refresh attempt:
  - `client.ts:88` — any HTTP 401 on a non-public-auth path (covers `/auth/me` and `/admin/graphql`)
  - `client.ts:134` — any HTTP 401 from GraphQL
  - `client.ts:143` — any GraphQL `errors[].message` matching `AUTH_ERROR_MESSAGES` (`client.ts:40-45`)

### Navbar

- `frontend/components/layout/PublicHeader/HeaderActions.tsx:17-23` — `useAuth()` → profile icon
  routes to `/admin` / `/my-account` / `/login` by `user.role_name`. Depends purely on the Redux slice.
- `PublicHeader.tsx` and `PublicFooter.tsx` render **no** My Account / My Orders links at all.
  Those links only exist inside `my-account/page.tsx:112` and `my-orders/page.tsx:77` (sidebar/breadcrumb).
  There is no nav-level visibility toggle to preserve, so nothing in the header needs to change.

---

## Backend Authentication Flow

| Concern | Location | Reality |
|---|---|---|
| REST auth | `backend/src/app/api/auth.py` | `/auth/register`, `/auth/login`, `/auth/refresh`, `/auth/logout`, `/auth/me`, `/auth/google` |
| Token creation | `backend/src/app/core/security.py:41-55` | HS256, `type: access\|refresh`, `jti` on refresh |
| Token decode | `backend/src/app/core/security.py:60-75` | `ExpiredTokenError` / `InvalidTokenError` |
| Refresh rotation | `backend/src/app/public/services/auth_service.py:86-100` | revoke old row, issue new pair, DB-backed `refresh_tokens` table |
| REST guard | `backend/src/app/dependencies/auth.py:26-45` `get_current_user` | **Bearer header first, then `access_token` cookie** |
| Admin guard | `backend/src/app/dependencies/auth.py:57-63` `require_admin` | used by `admin/context.py:30`, so **admin GraphQL already reads the cookie** |
| Public GraphQL guard | `backend/src/app/public/dependencies.py:26-40` `get_optional_current_user` | **Bearer header only — the cookie is never read** |
| CORS | `backend/src/app/main.py:19-29` | explicit origins `localhost:3000`, `127.0.0.1:3000`, `192.168.1.34:3000`; `allow_credentials=True`; no wildcard |

### The asymmetry that causes the bug

Two optional-auth resolvers exist side by side and they disagree:

```python
# backend/src/app/dependencies/auth.py:32-36   (REST + admin GraphQL)
if credentials is not None:
    token_value = credentials.credentials
elif request.cookies.get("access_token"):
    token_value = request.cookies.get("access_token")
```

```python
# backend/src/app/public/dependencies.py:31-33   (public GraphQL)
if credentials is None:
    return None          # ← request.cookies is never consulted
```

`get_optional_current_user` is the dependency behind `PublicContext.user`
(`backend/src/app/public/context.py:31,38`). Because the frontend holds its access token in an
**HttpOnly** cookie and never sends a header, `PublicContext.user` is **always `None`** for a
logged-in customer, even though `GET /auth/me` on the same cookies returns 200.

That `None` then detonates in two separate ways:

1. `require_user(ctx)` (`public/context.py:45-49`) raises
   `PermissionDeniedError("Authentication required")` for every authenticated operation —
   `orders`, `addresses`, `wishlist`, `notifications`, `current_user`, `my_subscriptions`
   (queries) and `update_profile`, `create_address`, `create_payment`, `checkout`,
   `cancel_order`, `create_review`, all `wishlist` mutations. Reproduced above.
2. `require_user_or_guest(ctx)` (`public/context.py:52-79`) silently **mints a brand-new
   `is_guest` User row and a guest Cart** for a customer who is actually logged in. The DB
   already contains 12 such `guest-…@guest.local` rows, and the reproduction shows the same
   browser receiving a different `cart.id` with and without the header.

### `/auth/refresh` and `/auth/logout` are broken for cookie-only callers

`backend/src/app/api/auth.py` (pre-fix `git show HEAD:backend/src/app/api/auth.py`)

```python
def refresh(
    db: Annotated[Session, Depends(get_db)],
    data: RefreshTokenInput | None = None,
    request: Request = None,
    response: Response = None,
) -> TokenResponse:
    token_value = (data.refresh_token if data is not None else None) or request.cookies.get("refresh_token")
```

**`/auth/refresh` was already correct.** `data: RefreshTokenInput | None = None` *is* honoured by
FastAPI as an optional body, so a bodyless cookie-only call reaches the cookie fallback and
returns 200. Verified against a minimal replica of the pre-fix signature: `no body -> 200`,
`{} -> 422`. The earlier "422" reading in this document came from the harness sending `{}`.

**`/auth/logout` was genuinely broken**, for an unrelated reason:

```python
def logout(...) -> Response:
    token_value = (data.refresh_token if data is not None else None) or request.cookies.get("refresh_token")
    if token_value:
        AuthService(db).logout(token_value)
    _clear_auth_cookies(response)                      # ← applied to the INJECTED response
    return Response(status_code=status.HTTP_204_NO_CONTENT)   # ← which is then DISCARDED
```

Returning a brand-new `Response` **replaces** the one FastAPI injected, so the two
`delete_cookie` calls are thrown away and the browser never receives a `Set-Cookie`.
Proven against a minimal replica:

```
/bad  (clear on injected, return new)  -> 204  set-cookie: []
/good (clear on the returned response) -> 204  set-cookie: ['access_token=""; ... Max-Age=0; Path=/; SameSite=lax']
```

Consequences of the lost `Set-Cookie`:

- The refresh token **was** revoked server-side, but the browser still holds it. It is dead on
  arrival, so the next refresh 401s — a stale cookie that can never be cleaned up.
- The `access_token` cookie **survives entirely**, so `GET /auth/me` keeps returning 200 after an
  explicit Sign Out. `my-account/page.tsx:103-105` masks this by dispatching the local Redux
  `logout()` in a `finally`, so the UI *appears* to work while the network session lives on for
  the remaining access-token lifetime.

### CORS

`backend/src/app/main.py:19-29` is already correct: three explicit origins, `allow_credentials=True`,
no `*`. The frontend origin is derived by `frontend/config/environment.ts:11-14` as
`http://<page-host>:8000`, which is `localhost:8000` for desktop. **No CORS change is required
and none should be made.** Same-site cookie delivery works because ports do not affect
SameSite, and `samesite="lax"` permits credentialed same-site XHR.

---

## Token Storage

```
Access Token
  Transport   : HTTP-only cookie, never exposed to JavaScript
  Cookie name : access_token
  Set by      : backend/src/app/api/auth.py:38-46  _set_auth_cookies()
  Signed with : settings.jwt_secret_key  (HS256, config.py:26)
  Payload     : { sub: <user uuid>, type: "access", exp: <unix> }
  Expiration  : settings.access_token_expire_minutes = 30 minutes   (config.py:28)
  Max-Age     : 30 * 60 = 1800 s                                   (api/auth.py:36)
  Path        : /
  Domain      : (unset — host-only, correct)
  Secure      : false                                              (api/auth.py:44)
  SameSite    : lax                                                 (api/auth.py:43)
  HttpOnly    : true                                                (api/auth.py:42)
  localStorage: NONE
  sessionStorage: NONE
  JS copy     : NONE

Refresh Token
  Transport   : HTTP-only cookie
  Cookie name : refresh_token
  Set by      : backend/src/app/api/auth.py:47-55
  Signed with : settings.jwt_refresh_secret_key  (HS256, config.py:27)
  Payload     : { sub: <user uuid>, type: "refresh", jti: <uuid>, exp: <unix> }
  Expiration  : settings.refresh_token_expire_days = 30 days       (config.py:29)
  Max-Age     : 30 * 24 * 60 * 60 = 2592000 s                      (api/auth.py:37)
  Path        : /     Secure: false     SameSite: lax     HttpOnly: true
  Server-side : refresh_tokens table, SHA-256 hashed, revoked on use (rotation)

Guest Token (unauthenticated cart identity)
  Cookie name : guest_token, Path /, SameSite lax, HttpOnly true, Max-Age 30 days
  Set by      : backend/src/app/public/context.py:39-41
```

The browser receives `TokenResponse` in the JSON body as well (`token_type`, `expires_at`),
and the frontend stores **only** `expires_at` in Redux (`login/page.tsx:50`,
`providers.tsx:57`) to drive the expiry timer. The token strings themselves are discarded.

**Does the backend expect a cookie or a header?** **Both, but inconsistently.**

- `GET /auth/me` — cookie **or** header (`api/auth.py:63-70`).
- Admin GraphQL `/admin/graphql` — cookie **or** header (`dependencies/auth.py:32-36`).
- Public GraphQL `/graphql` — header **only** (`public/dependencies.py:31-33`).

The cookie is therefore the intended primary transport, and the public GraphQL layer is the
outlier. The fix aligns it with the two layers that already work; it does not introduce a
second JWT system, and the token strings stay in HttpOnly cookies.

## Cookie Configuration

Every auth cookie is set by `_set_auth_cookies` / `get_public_context` with the same four
values, so there is one configuration to reason about:

```
                access_token  refresh_token  guest_token
Path            /             /             /
Domain          (unset)       (unset)       (unset)
SameSite        lax           lax           lax
Secure          false         false         false
HttpOnly        true          true          true
Max-Age         1800          2592000       2592000
Expires         (unset)       (unset)       (unset)
```

**Finding: the cookie configuration is not the cause.** The reproduction shows both cookies
arriving intact on every subsequent request, and the identical requests succeed the moment an
`Authorization` header is added. Cookies are not being dropped, not being scoped wrongly, and
are not blocked by SameSite/Secure — the public GraphQL resolver simply never looks at them.
`SameSite`, `Secure`, `Path` and `Domain` must therefore **not** be changed.

`_clear_auth_cookies` (`api/auth.py`) uses `delete_cookie(key, path="/")`, which matches the set
attributes, so the calls themselves are correct. The pre-fix defect was purely *where* they were
applied — on an injected `Response` that the handler then replaced.

## Auth Provider

There is no React context provider. `frontend/app/providers.tsx` holds the entire auth lifecycle:

| Lines | Responsibility | Defect |
|---|---|---|
| 26-36 | `endSession` — the single global logout | No `isAuthenticated` guard; no refresh attempt; always redirects |
| 38-41 | Binds `endSession` to the global unauthorized handler | correct mechanism, wrong target |
| 43-73 | `restoreSession` — calls `GET /auth/me` on mount, dispatches `setUser` / `setTokenExpiry`, and `setAuthReady()` in `finally` | on any failure dispatches `setSessionExpired` + `logout` and, for a 401, `router.replace("/")` — bounces anonymous visitors off public pages |
| 75-83 | 1 s interval that calls `endSession()` at `accessTokenExpiresAt` | **logs out at 30 min instead of refreshing** |

`frontend/context/AuthContext/index.ts` is a dead 1-line stub. Nothing must be added there —
creating a second provider is explicitly out of bounds.

## Route Guard

- `frontend/app/(account)/layout.tsx` — protects `/my-account`, `/my-orders`, `/my-orders/[orderId]`,
  `/addresses`, `/notifications`, `/security`. Requires `isReady && isAuthenticated && role_name === "customer"`.
  Redirects an admin to `/admin`, anyone else to `/`.
- `frontend/app/admin/layout.tsx` — protects all of `/admin/**`. Requires `isReady && isAuthenticated && role_name === "admin"`.
- `frontend/app/(public)/**` — unguarded by design; that is the public browse/cart/purchase path.

Both guards read `isReady` before acting, so requirement §8 ("must not treat Loading as
Unauthenticated") is **already satisfied** and must be preserved. `useAuth` is the only
consumer surface.

## API Interceptor

No Axios — a hand-rolled `fetch` wrapper in `frontend/services/api/client.ts`. Relevant
behaviour:

- `isAuthFailureResponse(status, path)` (47-49): `status === 401 && !PUBLIC_AUTH_PATHS.some(...)`
- `PUBLIC_AUTH_PATHS` (38) = `/auth/login`, `/auth/register`, `/auth/google`, `/auth/refresh`
  — **`/auth/me` is absent**, so an anonymous visitor's expected 401 is treated as a session failure.
- `isAuthFailureMessage(message)` (51-54): substring match against
  `["authentication required", "invalid or malformed token", "token has expired", "not authenticated"]`
- `setUnauthorizedHandler` / `notifyUnauthorized` (27-35): a single module-level callback slot
- `graphqlRequest` (112-147): `credentials: "include"` on every request; no retry, no queue,
  no single-flight guard, no refresh hook

There is exactly one JWT transport in use (cookies). The interceptor must not grow a second
one, and it must not start attaching a `Bearer` header — there is no token available to attach.

## Token Refresh

| Item | State |
|---|---|
| Refresh endpoint | **Exists** — `POST /auth/refresh` (`api/auth.py:96-108`) and GraphQL `refreshToken` mutation (`mutations/auth.py`) |
| Frontend caller | **None** — `authApi.refresh` is defined and unit-tested but never invoked |
| Refresh interceptor | **Does not exist** |
| Refresh cookie | `refresh_token`, HttpOnly, 30 days, `SameSite=Lax`, sent on every request |
| Refresh response | `TokenResponse` + fresh cookies via `_set_auth_cookies` (`api/auth.py:107`) |
| Token rotation | **Yes** — `AuthService.refresh` (`auth_service.py:86-100`) revokes the old `refresh_tokens` row and issues a new pair; reuse of a rotated token returns 401 (covered by the passing test `test_refresh_reused_token_rejected`) |
| Expiration handling | 30 min access / 30 day refresh, from `config.py:28-29` |
| 401 handling | Immediate global logout, no refresh attempt (`client.ts:88,134,143`) |
| Cookie-only refresh | **Already worked** pre-fix — `X | None = None` is an optional body. No change required. |

Consequence: the rotation machinery is correct and tested, and the browser is holding a
perfectly valid 30-day refresh token, but nothing ever uses it. Navigation is not the trigger
here; the 30-minute timer is.

## Root Cause

**Primary — the public GraphQL layer ignores the auth cookie, so every authenticated public
query fails, and the API client treats that failure as a session loss and logs the user out.**

```
File:      backend/src/app/public/dependencies.py
Function:  get_optional_current_user   (lines 26-40), line 31-33
Current:   if credentials is None: return None
           request.cookies["access_token"] is never read, so PublicContext.user is always
           None for a cookie-authenticated customer.
Expected:  fall back to the access_token cookie exactly as
           backend/src/app/dependencies/auth.py:32-36 already does for REST and admin GraphQL.
Root cause:two optional-auth resolvers disagree about the transport. The frontend is
           cookie-only by design (HttpOnly tokens), so the public layer can never
           authenticate anybody. Unauthenticated operations then raise
           PermissionDeniedError("Authentication required") from
           backend/src/app/public/context.py:48.
Affected:   /my-account, /my-orders, /wishlist, /notifications, and every authenticated
           mutation — i.e. the exact navigation steps that appear to log the user out.
```

**Amplifier — `endSession` fires on any auth-failure signal regardless of whether a session
exists, and never attempts a refresh first.**

```
File:      frontend/app/providers.tsx
Function:  endSession                  (lines 32-36)
Current:   dispatch(setSessionExpired); dispatch(logout());
           if (!isAuthPage()) router.replace("/")
           — invoked from client.ts:88 / :134 / :143 for any 401 or auth-flavoured GraphQL
           message, with no isAuthenticated check and no refresh attempt.
Expected:  If there is no session, do nothing. If there is one, try a silent refresh first
           and only end the session when the refresh itself fails.
Root cause:the unauthorized signal is treated as authoritative proof that the session is over.
Affected:   every page transition into an account area; plus anonymous visitors deep-linking
           to any public route, which get router.replace("/") because /auth/me is not
           treated as an expected-401 endpoint.
```

**Independent second logout — the 30-minute expiry timer destroys a session that could
still be refreshed.**

```
File:      frontend/app/providers.tsx
Function:  token-expiry useEffect      (lines 75-83)
Current:   a 1 s interval calls endSession() once Date.now() >= accessTokenExpiresAt.
           access_token_expire_minutes = 30, so every session dies at 30 minutes even
           though a valid 30-day refresh_token cookie is present. authApi.refresh is never
           called anywhere in the app.
Expected:  POST /auth/refresh ~60 s before expiry, update the new expires_at, repeat.
Root cause:refresh was implemented on the backend and in the API wrapper but never wired
           into the lifecycle.
Affected:   any session older than 30 minutes, on any page.
```

**Fourth — logout's cookie deletions were applied to a `Response` that was immediately
discarded, so the browser never stopped being logged in.**

```
File:      backend/src/app/api/auth.py
Function:  logout
Current:   _clear_auth_cookies(response)            # applied to FastAPI's injected Response
           return Response(status_code=204)         # ...which this replaces, discarding the headers
           The refresh token is revoked, but no Set-Cookie is ever emitted, so the browser
           keeps both cookies. GET /auth/me still returns 200 after an explicit Sign Out,
           masked by the local Redux logout() in my-account/page.tsx.
Expected:  apply the deletions to the Response that is actually returned.
Root cause:returning a new Response instead of mutating the injected one.
Affected:   server-side logout only. /auth/refresh needed no change and was already correct.
```

**Fifth — the account query is malformed, so My Account and My Orders could not load even
with a perfect session.**

```
File:      frontend/services/api/account.api.ts
Function:  accountApi.getOverview      (lines 36-42)
Current:   snake_case fields against a Strawberry schema that auto-camelCases.
           Reproduced against the live schema:
             Cannot query field 'current_user' on type 'PublicQuery'. Did you mean 'currentUser'?
             Unknown argument 'page_size' on field 'PublicQuery.orders'. Did you mean 'pageSize'?
             Cannot query field 'recipient_name'/'address_line1'/'postal_code'/'is_default'
               on type 'AddressType'
             Cannot query field 'order_number'/'created_at' on type 'OrderType'
             Cannot query field 'product_name'/'unit_price'/'product_id' on type 'OrderItemType'
           11 validation errors, data: null, so my-account/page.tsx:41 and
           my-orders/page.tsx:41 always land in their .catch() branch.
Expected:  currentUser / pageSize / recipientName / addressLine1 / postalCode / isDefault /
           orderNumber / createdAt / productName / unitPrice / productId.
Root cause:response type names in account.api.ts:13-33 mirror the wrong casing.
Affected:   /my-account and /my-orders content.
```

**Ruled out** (checked in code and against the running server, not assumed):

- **Cookie attributes.** `Path=/`, host-only, `SameSite=Lax`, `HttpOnly`, `Max-Age` all arrive
  intact on every request in the reproduction. Ports do not affect SameSite, so the
  `localhost:3000 → localhost:8000` cross-origin XHR is same-site and the cookie is delivered.
  Nothing here needs changing.
- **CORS.** Explicit origins with `allow_credentials=True` and no wildcard (`main.py:19-29`).
  Verified: the reproduction sets `Origin: http://localhost:3000` and every call succeeds.
- **`credentials: "include"`.** Present and correct for `/auth`, `/admin` (`client.ts:71-76`)
  and all GraphQL (`client.ts:130`).
- **Provider remount on navigation.** `Providers` is mounted once in the root layout and
  `useState(makeStore)` pins the store instance; `AuthBootstrap` sits below it and does not
  remount on route change.
- **Route guards racing the loading state.** `isReady` is honoured by both
  `(account)/layout.tsx:11,16` and `admin/layout.tsx:12,15`.
- **Duplicate JWT systems.** There is only one: HttpOnly cookies + PyJWT. The public GraphQL
  layer is the single place that fails to read it.
- **Missing logout UI.** `my-account/page.tsx:112` already has a working Sign Out button.
- **Admin authentication.** `require_admin` → `get_current_user` already reads the cookie, and
  the reproduction confirms `/admin/graphql` authenticates from cookies alone. Admin is not the
  broken path — it is the *correct* path that the public GraphQL layer should match.

---

## Recommended Fix

Minimum change set, one root cause plus the three defects that block its verification.
No second JWT system, no second auth provider, no new cookie attributes, no CSS.

1. **`backend/src/app/public/dependencies.py` — read the cookie.** Add a `Request` parameter to
   `get_optional_current_user` and fall back to `request.cookies.get("access_token")` when no
   Bearer header is present, keeping its "return `None` instead of raising" contract so the
   public catalog keeps working for anonymous visitors. Reuse the extraction logic from
   `backend/src/app/dependencies/auth.py` rather than re-implementing it, so REST, admin GraphQL
   and public GraphQL all resolve the token the same way. **This is the root-cause fix.**

2. **`backend/src/app/api/auth.py` — apply logout's cookie deletions to the returned `Response`,
   and share one token resolver.** Build the `204` response first, call `_clear_auth_cookies` on
   it, and return that object, so the browser actually receives the `Set-Cookie` deletions. The
   optional-body declaration on `refresh`/`logout` is already correct and is deliberately left
   alone. `_extract_access_token` is replaced by a shared `get_access_token` dependency so
   `/auth/me` decodes the very token that authenticated the caller instead of re-deriving it
   from a second source — this keeps the `Authorization: Bearer` path working for non-browser
   clients, which is easy to break silently because the browser only ever sends the cookie.

3. **`frontend/services/api/client.ts` — refresh once before ending the session.** Add a
   module-level session-refresher hook (mirroring the existing `setUnauthorizedHandler` pattern)
   plus a single-flight promise so concurrent 401s trigger exactly one `POST /auth/refresh`.
   On an auth failure, attempt the refresh and replay the original request once; only call
   `notifyUnauthorized()` when the refresh itself fails. Leave `PUBLIC_AUTH_PATHS` and the
   cookie/`credentials` handling alone — the token stays in the cookie and no `Bearer` header
   is introduced.

4. **`frontend/app/providers.tsx` — replace the expiry logout with proactive refresh, and guard
   `endSession`.**
   - `endSession` returns immediately when `isAuthenticated` is false, so an anonymous visitor's
     expected 401 can no longer bounce them off a public page.
   - The `restoreSession` catch only redirects when a session actually existed.
   - Register a `setSessionRefresher` that calls `authApi.refresh()` and dispatches the new
     `expires_at`, and swap the 1 s expiry interval for a single `setTimeout` scheduled ~60 s
     before `accessTokenExpiresAt`. A full page load with an expired access token is then
     recovered by the same refresher via the `/auth/me` retry, which is what makes browser
     refresh survive past 30 minutes.

5. **`frontend/services/api/account.api.ts` — correct the GraphQL field names** to the
   camelCase the schema actually exposes (and the matching response types), so My Account and
   My Orders render.

Explicitly **not** done: no cookie attribute changes, no CORS changes, no `localStorage` token
copy, no second auth provider, no route-protection removal, no CSS.

## Files To Modify

| File | Change |
|---|---|
| `backend/src/app/dependencies/auth.py` | extract the shared access-token resolver (Bearer → cookie) used by all three layers |
| `backend/src/app/public/dependencies.py` | **root cause** — `get_optional_current_user` falls back to the `access_token` cookie |
| `backend/src/app/api/auth.py` | `/auth/logout` clears cookies on the **returned** `Response`; `get_access_token` shared dependency replaces `_extract_access_token` |
| `frontend/services/api/client.ts` | single-flight refresh-and-replay before `notifyUnauthorized()` |
| `frontend/app/providers.tsx` | register the session refresher; proactive refresh replaces the expiry logout; `endSession` no-ops without a session |
| `frontend/services/api/account.api.ts` | camelCase GraphQL field names + response types |

Route guards, `authSlice`, `useAuth`, `auth.api.ts`, all header/footer components, the admin
layout and every admin page are left untouched. No CSS is touched.

## Testing Results

Baseline before any change:

```
backend : 226 passed                                   (pytest src/app/tests -q)
frontend: 118 passed, 2 failed                         (npm test)
          pre-existing failures, unrelated to auth:
            components/chat/SupportChat.test.tsx
            app/(public)/chat/page.test.tsx
```

Reproduction (recorded above) — before the fix:

```
Login                                  -> HTTP 200, session valid
GET  /auth/me                          -> 200
POST /graphql currentUser  (cookie)    -> 200 errors=['Authentication required']  -> LOGOUT
POST /graphql addresses   (cookie)     -> 200 errors=['Authentication required']  -> LOGOUT
POST /graphql orders      (cookie)     -> 200 errors=['Authentication required']  -> LOGOUT
POST /graphql wishlist    (cookie)     -> 200 errors=['Authentication required']  -> LOGOUT
POST /graphql notifications (cookie)   -> 200 errors=['Authentication required']  -> LOGOUT
POST /auth/refresh        (cookie)     -> 200   (already correct — not a defect)
POST /auth/logout         (cookie)     -> 204, no Set-Cookie, /auth/me still 200
POST /graphql cart (cookie)            -> cart A
POST /graphql cart (Bearer)            -> cart B          (two carts, one browser)
accountApi.getOverview()               -> 11 schema validation errors, data: null
```

### After the fix

Live matrix against a freshly started server (`127.0.0.1:8010`) with a real cookie jar — one shared
jar, `credentials: include`, no `Authorization` header, exactly as the browser behaves:

```
UNAUTHORIZED (public user)                                     8/8  PASS
  products, product details, categories, cart, add-to-cart,
  My Account hidden, My Orders hidden, stays on a public route
CUSTOMER                                                        31/31 PASS
  login, HttpOnly cookies, user info, role
  navigation (Home, Products, Category, Product Details, Cart)   each preserves the session
  My Account, addresses, My Orders, Wishlist, Notifications
  cart is the customer's own, not a guest cart
  /graphql and /auth/me agree on the user
  browser refresh on 6 routes preserves authentication
  direct URL on /products /cart /my-account /my-orders /wishlist
  cookie-only POST /auth/refresh 200, rotates the pair, session still valid
  fresh pair always obtainable; session survives an access-token lifetime
ADMIN                                                           8/8  PASS
  login, role, Dashboard/Products/Categories/Orders/Customers from
  cookies alone, refresh, not redirected by customer auth logic,
  admin routes still 401 for anonymous
LOGOUT                                                          6/6  PASS
  204, both cookies cleared, session gone, My Account/My Orders
  hidden, public browsing still works
                                                        RESULT: 57 passed, 0 failed
```

Test suites:

```
backend : 268 passed        (was 226 at baseline; +16 auth-persistence, +26 from concurrent
                             Google-signin work already in the tree)
frontend: 78 suites, 174 tests passed, 0 failed
           (was 118 passed / 2 failed at baseline; the two pre-existing
            SupportChat failures are now fixed by concurrent chat work)
eslint   : clean on all touched files (1 pre-existing <img> warning in my-orders/page.tsx)
ruff     : clean on all touched files
tsc      : no errors in any touched file
```

New regression coverage added in `backend/src/app/tests/test_auth_persistence.py` (16 tests) pins
the exact defects, so they cannot silently return:

- public GraphQL resolves the cookie, and still reports anonymous without one
- a junk `access_token` cookie degrades to anonymous instead of raising
- the same browser no longer receives two different carts
- `/auth/me` accepts **both** a cookie and a `Authorization: Bearer` header, and still reports
  `expires_at` (the header path is a browser-invisible regression)
- admin GraphQL returns 403 — not 401 — for a header-authenticated customer
- bodyless `/auth/refresh` returns 200 and rotates; with no token at all it 401s
- `/auth/logout` emits both deletions and makes `/auth/me` 401 afterwards

`frontend/services/api/client.test.ts` gained 6 tests for the recovery path: REST and GraphQL
replay after a successful refresh without logging out, logout only when the refresh itself fails,
a throwing refresher still surfaces the original error, one refresh serves a burst of concurrent
401s (single-flight), and a failing replay is retried exactly once.

### Notes for future reproductions

- Start a fresh server before recording "before" numbers. Port `8000` was occupied by a stale
  `uvicorn` process (started before the edits, no `--reload`) during this investigation; results
  taken from it reflect whatever code was loaded at that time, not the working tree.
- Call bodyless endpoints with **no** body. Sending `{}` is a different request and 422s on any
  endpoint with an optional Pydantic body — that single mistake produced the incorrect
  "cookie-only refresh is broken" claim retracted at the top of this document.
