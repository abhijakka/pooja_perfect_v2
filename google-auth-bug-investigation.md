# Google Authentication Bug Investigation

**Status:** Root cause identified. Investigation performed by reading the repository only
(no live Google account was available, so no end-to-end browser run against Google was possible).
**Stack:** Next.js `16.3.2` App Router, React `19.2.8`, TypeScript `strict`; FastAPI + Strawberry
GraphQL (public `/graphql`, admin `/admin/graphql`) + REST `/auth/*`.
**Auth architecture in use:** HttpOnly **cookie** based. No token is ever readable by JavaScript.

---

## Existing Google OAuth Configuration

`backend/src/app/config.py:31-34`

```python
31      # ── Google OAuth ──────────────────────────────────────────
32      google_client_id: str = ""
33      google_client_secret: str = ""
34      google_redirect_uri: str = ""
```

`backend/.env.example:18-21` already documents `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`,
`GOOGLE_REDIRECT_URI`. No new variables were added.

**Architecture already chosen and in use: Google Identity Services (GIS) → `id_token` → backend
verification.** The proof is the shape of the existing endpoint: it accepts a Google **JWT**
(`OAuthLoginInput.id_token`), not an authorization `code`, and it verifies it with
`google.oauth2.id_token.verify_oauth2_token`. `GOOGLE_REDIRECT_URI` is declared in settings but
deliberately **unused** by the verification path — no redirect URI has to be registered for this
flow, and none is.

There is **no** `allauth` / `dj-rest-auth` / `social-auth` / `python-social-auth` in
`backend/requirements.txt` or anywhere in `backend/src`. Grep for
`allauth|dj-rest-auth|social_auth` returns zero hits.

## Existing Client ID Configuration

`backend/.env` → `GOOGLE_CLIENT_ID` is **set** (72 chars, `*.apps.googleusercontent.com` shape:
45-char prefix + `.` + `apps` + `.` + `googleusercontent` + `.` + `com`).
Read by `app.config.Settings.google_client_id`; consumed only by
`app.integrations.google.oauth.verify_google_id_token` as the `audience` for verification.

## Existing Client Secret Configuration

`backend/.env` → `GOOGLE_CLIENT_SECRET` is **set** (35 chars). It is read into
`Settings.google_client_secret` and is **never referenced by any code path** — grep for
`google_client_secret` returns only the declaration in `config.py`. It is backend-only and is
not, and must not be, sent to the browser. No new credentials were created.

## Login Page

`frontend/app/(auth)/login/page.tsx`

- Form: Formik + Yup, fields `identifier` (email **or** mobile) and `password`, plus `remember`.
- Password submit (`page.tsx:42-71`):
  `authApi.login()` → `dispatch(setTokenExpiry(Date.parse(tokens.expires_at)))` → `authApi.me()`
  → `dispatch(setUser({ id, name, email, role_name }))` → toast →
  `router.push("/admin")` when `role_name === "admin"` else `router.push("/")`.
- Google button (`page.tsx:86`) — **a placeholder**:

```tsx
<button className="login-google" type="button" onClick={() => notify("Google sign in is ready to connect")}>
  <strong>G</strong> Continue with Google
</button>
```

## Register Page

`frontend/app/(auth)/signup/page.tsx`

- Form: Formik + Yup, fields `firstName`, `lastName`, `email`, `phone`, `password`,
  `confirmPassword`, `terms`. Submit calls `authApi.register(...)` then `router.push("/login")`
  (it deliberately does **not** authenticate — registration and login are separate steps).
- Google button (line 75) — **also a placeholder**:

```tsx
<button className="signup-google" type="button" onClick={() => notify("Google sign up is ready to connect")}>
  <strong>G</strong> Continue with Google
</button>
```

## Google OAuth Flow

The **server half already exists end to end**:

| Step | Location | State |
|---|---|---|
| Credential posted | `backend/src/app/api/auth.py:135-143` `POST /auth/google` | done |
| Schema | `backend/src/app/schemas/auth/oauth.py` `OAuthLoginInput{provider, id_token}` | done |
| Provider guard | `public/services/auth_service.py:113-114` rejects anything but `google` | done |
| Token verification | `integrations/google/oauth.py:26-54` `id_token.verify_oauth2_token(..., audience=settings.google_client_id)`; any SDK failure → `GoogleAuthError`; `email_verified` must be true | done |
| Claim normalisation | `integrations/google/oauth.py:46-54` → `GoogleUserInfo(sub, email, email_verified, name, given_name, family_name, picture)`, email lower-cased | done |
| Find-or-create | `public/services/auth_service.py:144-168` | done |
| Token issuance | `public/services/auth_service.py:126-142` `_issue_tokens` (same helper as password login) | done |
| Cookies | `api/auth.py:37-57` `_set_auth_cookies` (same helper as password login) | done |
| GraphQL twin | `public/api/graphql/mutations/auth.py:73-77` `mutate_google_login` | done |
| Activity log | `core/activity_logging.py:202-207` `"/auth/google"` entry | done |
| Error type | `core/exceptions.py:55-57` `GoogleAuthError` → HTTP 401 `"Google authentication failed"` | done |

Frontend half of the same flow:

| Step | Location | State |
|---|---|---|
| API wrapper | `frontend/services/api/auth.api.ts:23-24` `googleLogin({provider, id_token})` → `POST /auth/google`, `credentials: "include"` | done |
| Type | `frontend/types/auth.ts:46-49` `OAuthLoginInput` | done |
| 401 suppression | `frontend/services/api/client.ts:38` `/auth/google` is in `PUBLIC_AUTH_PATHS`, so a rejected Google credential does **not** fire the global `notifyUnauthorized()` → `endSession()` | done |
| Unit test | `frontend/services/api/auth.api.test.ts:62-70` | done |
| **GIS script loader** | `frontend/services/google/google-identity.ts` `loadGoogleIdentity()` — single module-level promise, local `google.accounts.id` typings, no new npm dependency | **fixed** |
| **Public client id in the browser** | `auth.api.ts:28` `googleConfig()` → `GET /auth/google/config` → `backend/src/app/api/auth.py:131-141` `google_config()`; the id is read from the backend, never duplicated into a frontend env file | **fixed** |
| **Button → credential** | `login/page.tsx` / `signup/page.tsx` call `useGoogleAuth().signInWithGoogle`; the placeholder `onClick` toast is gone | **fixed** |
| **Post-auth sequence** (tokens → `me` → `setUser` → role redirect) | `frontend/hooks/useGoogleAuth.ts` — `POST /auth/google` → `setTokenExpiry` → `authApi.me()` → `setUser`, then the page applies the existing `role_name === "admin" ? "/admin" : "/"` rule | **fixed** |

## Callback Flow

There is **no redirect callback**, and that is by design, not an omission. GIS returns a signed
`id_token` in-page; the browser posts it straight to `POST /auth/google`; the backend verifies the
signature against Google's published JWKS, checks `aud == GOOGLE_CLIENT_ID` and `email_verified`.
Consequences for the checks in §16 of the brief:

- Redirect URI: not part of this flow, so `GOOGLE_REDIRECT_URI` correctly stays unused.
- `state` parameter: not part of this flow. There is no CSRF surface because the value posted to
  the backend is a Google-signed token the client cannot forge, not a bearer value it chose.
- Authorization code: not used, so code-replay/expiry cannot occur.
- Secret exposure: the browser only ever sees the **public** client id and the `id_token` it just
  received. The client secret is not needed by GIS and is not in any frontend file.
- Error propagation: `GoogleAuthError` → 401 with a generic detail string, so no OAuth internals
  leak to the user.

## Existing User Flow

`public/services/auth_service.py:145-148` — an `oauth_accounts` row matching
`(provider="google", provider_account_id=info.sub)` is looked up first, and its `user_id` is
returned. The existing account is authenticated; **no new user is created**. Its `role_name` is
whatever the DB already says, so an existing admin stays an admin.

## New User Flow

`public/services/auth_service.py:150-168`

1. No linked `oauth_accounts` row →
2. `get_by_email(info.email)` hits → `add_oauth_account(...)` and return the existing user
   (this is the "signed up with a password, now signing in with Google" case).
3. Otherwise create:

```python
157  user = self._users.create(
158      email=info.email,
159      first_name=info.given_name or info.name or "",
160      last_name=info.family_name or "",
161      google_id=info.sub,
162      avatar_url=info.picture,
163      is_email_verified=True,
164      email_verified_at=datetime.now(UTC),
165  )
166  self._db.flush()
167  self._users.add_oauth_account(user.id, "google", info.sub)
```

`role_name` is **not** passed, so the column default `UserRole.CUSTOMER`
(`models/user.py:33-35`) applies. `status` likewise defaults to `ACTIVE`. Nothing is invented:
`phone`, `date_of_birth` and `admin_notes` are left `NULL`.

The `flush()` + `add_oauth_account` are committed by the `self._db.commit()` inside
`_issue_tokens` (`auth_service.py:135`), which is always reached for an active user. If the
account turns out to be inactive, `InactiveUserError` is raised *before* that commit, so no
half-built row is left behind.

## User Model

`backend/src/app/models/user.py`

| Field | Line | Google mapping |
|---|---|---|
| `email` (unique index `ix_users_email`) | 27 | `claims["email"]`, lower-cased |
| `first_name` NOT NULL | 25 | `given_name` → `name` → `""` |
| `last_name` NOT NULL | 26 | `family_name` → `""` |
| `google_id` unique, nullable | 30 | `claims["sub"]` — the stable Google identifier |
| `avatar_url` | 31 | `claims["picture"]` |
| `is_email_verified` | 39-41 | `True` (only reachable when Google says `email_verified`) |
| `email_verified_at` | 46 | now |
| `role_name` default `customer` | 33-35 | untouched → **customer** |
| `status` default `active` | 36-38 | untouched |
| `phone`, `password_hash` | 28-29 | untouched — a Google-only account has **no** password |

There is also a second, provider-agnostic identity table:

`backend/src/app/models/oauth_account.py` — `oauth_accounts(user_id, provider, provider_account_id)`
with `UniqueConstraint("provider", "provider_account_id", name="uq_oauth_provider_account")`.
So the project already stores the Google identity in **two** places: `users.google_id` and
`oauth_accounts`. Both already exist; no new identity field is needed or was added.

## Email Matching

`public/repositories/user_repository.py:30-31` — `get_by_email` is an exact
`WHERE User.email = :email` match, no `ilike`/lowercase folding.

Two facts make this safe for Google:

- `AuthService.register` (`auth_service.py:55`) lower-cases and trims before storing.
- `verify_google_id_token` (`integrations/google/oauth.py:48`) lower-cases and trims before
  `get_by_email`.

So both writers normalise and the comparison is exact → **one row per email**, enforced
independently by the unique index `ix_users_email`. A normal registration followed by a Google
login with the same address reuses the row (`auth_service.py:151-154`); the reverse order
reuses the row too, and the password keeps working because `password_hash` is only written by
`register` and is never touched by the Google path.

## Google Provider ID

`claims["sub"]` — a stable, non-reassignable per-(client, user) identifier. It is persisted twice:

- `oauth_accounts(provider='google', provider_account_id=sub)` — the lookup key, unique
  (`auth_service.py:146`).
- `users.google_id` — a denormalised unique copy, **written only on the create branch**
  (`auth_service.py:161`).

**Gap:** the email-link branch (`auth_service.py:151-154`) writes only the `oauth_accounts` row
and leaves `users.google_id` as `NULL`. The two stores then disagree for every account that
registered with a password first. The `oauth_accounts` row is authoritative for login, so this is
not a live login failure, but it leaves the model inconsistent and loses the link if that row is
ever pruned.

## JWT / Session Creation

`public/services/auth_service.py:126-142` `_issue_tokens`, reached from **both** `login()` and
`google_login()`:

```python
127  access_token, access_exp = create_access_token(user.id)
128  refresh_token, refresh_exp = create_refresh_token(user.id)
130  self._tokens.create(user_id=user.id, token_hash=hash_token(refresh_token), expires_at=refresh_exp)
135  self._db.commit()
```

The refresh token is stored hashed in `refresh_tokens` and is rotatable/revocable. Google login
gets the identical treatment — **no second JWT system**.

## Cookie Configuration

`backend/src/app/api/auth.py:37-57` `_set_auth_cookies`, called by `/auth/login` (line 88),
`/auth/refresh` (line 104) **and `/auth/google` (line 142)**:

| Cookie | HttpOnly | SameSite | Path | Max-Age |
|---|---|---|---|---|
| `access_token` | true | lax | `/` | `ACCESS_TOKEN_EXPIRE_MINUTES * 60` |
| `refresh_token` | true | lax | `/` | `REFRESH_TOKEN_EXPIRE_DAYS * 86400` |

`secure=False` throughout, consistent with plain-HTTP local/LAN development. The client secret
is never involved. Cookies are host-only, so the backend stays the single authority on the
session.

## Auth State

There is no `AuthProvider`. `frontend/context/AuthContext/index.ts` is a one-line placeholder
(`export const AuthContext = {}`) imported nowhere. The real state is Redux:

- `frontend/store/slices/authSlice.ts` — `user`, `isAuthenticated`, `isReady`,
  `accessTokenExpiresAt`, `sessionExpired`; actions `setUser`, `setTokenExpiry`,
  `setSessionExpired`, `logout`, `setAuthReady`.
- `frontend/hooks/useAuth.ts` — thin selector over `state.auth`.
- `frontend/app/providers.tsx:26-86` `AuthBootstrap` — the de-facto auth provider. On mount it
  calls `authApi.me()` and rehydrates the slice; a valid `access_token` **cookie** is all that is
  required, so a Google session survives a full browser refresh with no extra work.
- `providers.tsx:97-126` — after the session settles, the cart is re-read so a guest who signs
  in sees the cart the backend resolves for that identity.

`isAuthenticated` becomes `true` only via `setUser`. Because the password path and the Google
path will both end in `setTokenExpiry` → `me()` → `setUser`, auth state is reached identically.

## Role Handling

- Source of truth is `users.role_name` (`customer` | `admin`, `models/user.py:33-35`).
- New Google users never receive `role_name`, so the column default `CUSTOMER` applies. No role
  is ever read from, or derived from, Google profile data.
- An existing user linked by email keeps the role already in the DB.
- Guards: `frontend/app/(account)/layout.tsx:14-20` requires
  `isAuthenticated && user.role_name === "customer"`; `frontend/app/admin/layout.tsx` requires
  `"admin"`. Server-side: `app/dependencies/auth.py:72-78` `require_admin`.
- Redirect rule already in the codebase (`login/page.tsx:62-63`):
  `role_name === "admin" → /admin`, otherwise `/`. The Google path will reuse it verbatim.

## Redirect Handling

- Sign-in landing: `router.push("/admin")` for admin, `router.push("/")` for customer.
- Registration (password) lands on `/login`; Google registration is already authenticated, so it
  must go to the same landing as Google login, not to `/login`.
- `providers.tsx:20` `AUTH_PAGES` already contains `/login` and `/signup`, so a 401 while on
  those pages will not bounce the visitor to `/`.
- `providers.tsx:32-36` `endSession()` replaces to `/` on genuine session loss. Because
  `/auth/google` is in `PUBLIC_AUTH_PATHS` (`client.ts:38`), a rejected Google credential produces
  a local error message instead of a redirect — which is the required behaviour.

---

## Root Cause

**There is exactly one defect, and it is entirely on the frontend: the "Continue with Google"
buttons are placeholders that display a toast instead of starting a Google authentication
attempt.**

`frontend/app/(auth)/login/page.tsx:86`

```tsx
onClick={() => notify("Google sign in is ready to connect")}
```

`frontend/app/(auth)/signup/page.tsx:75`

```tsx
onClick={() => notify("Google sign up is ready to connect")}
```

Everything a Google sign-in needs on the receiving end is already present and already correct:

- backend `POST /auth/google` + verification + find-or-create + `_issue_tokens` + cookies,
- `google_id` on the user model and the `oauth_accounts` identity table,
- `authApi.googleLogin()` and the `OAuthLoginInput` type,
- `/auth/google` registered in `PUBLIC_AUTH_PATHS` so a rejected credential is not treated as an
  expired session,
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` in `backend/.env`.

What is absent is the **browser half** of the GIS flow. The project contains no
`accounts.google.com/gsi/client` loader, no `google.accounts.id.initialize()` call, no place
where a Google-signed `id_token` is obtained, and no code that turns that token into the same
Redux/cookie state that password login produces. The frontend also has no access to the public
client id: `frontend/` contains **no** `.env*` file, and `config/environment.ts` exposes only
`apiUrl`, so `NEXT_PUBLIC_GOOGLE_CLIENT_ID` is not defined anywhere in the project.

Consequence: a click on either Google button is a no-op that tells the user the feature is
"ready to connect". No request is made, no cookie is set, `isAuthenticated` stays `false`,
nothing is created, nothing is broken. The backend endpoint has simply never been called.

Secondary defect (backend, data consistency only — it does not break login):
`google_id` is written only on the create branch, so an account linked to Google by email has an
`oauth_accounts` row but a `NULL` `users.google_id`.

## Recommended Fix

Add the missing browser half and reuse everything that exists. No new endpoint for the token
exchange, no new login endpoint, no new user model, no new JWT system, no new auth provider, no
new credentials, no CSS change.

**Single source of truth for the client id.** The public client id is read from the backend,
which already owns it, through a read-only `GET /auth/google/config`. Writing the same id into a
second `.env` file would duplicate the credential and allow the two to drift; this returns the
value the backend will actually verify against. It exposes only the public id — the client
secret stays in `backend/.env` and is never referenced by any code path, frontend or backend.

**One loader, one hook, one button in each page.**

1. `frontend/services/google/google-identity.ts` — loads `https://accounts.google.com/gsi/client`
   exactly once (module-level promise, de-duplicated) and returns the `google.accounts.id`
   namespace, plus the minimal typings the project needs. No new npm dependency.
2. `backend` — `GET /auth/google/config` returning `{"client_id": settings.google_client_id}` and
   `{"client_id": ""}` when unset, so the frontend degrades to a clear message instead of
   throwing.
3. `frontend/hooks/useGoogleAuth.ts` — the single shared implementation of
   "obtain a verified credential → `authApi.googleLogin` → `setTokenExpiry` → `authApi.me()` →
   `setUser`", i.e. byte-for-byte the same post-auth sequence the password path already performs
   in `login/page.tsx:45-59`. Returns the `UserResponse` so each page keeps its own toast copy and
   applies the existing role redirect.
4. `login/page.tsx` and `signup/page.tsx` — replace the placeholder `onClick` with the hook's
   handler. The existing `<button className="login-google">` / `<button className="signup-google">`
   elements and their classes are untouched, so no stylesheet changes.

**Hardening in the existing backend service (no new behaviour, no new tables).**

5. `users.google_id` is also populated on the email-link branch, guarded so the unique column can
   never be violated, and a dangling `oauth_accounts` row whose user no longer exists can no
   longer raise `AttributeError` (a 500) — it falls through to the email branch.

**Errors** are surfaced as a local toast on the page. `GoogleAuthError` already returns a generic
401, `/auth/google` is already excluded from the global logout handler, and no Google internals
are ever shown to the user.

## Files To Modify

| File | Change |
|---|---|
| `backend/src/app/schemas/auth/oauth.py` | add `OAuthProviderConfigResponse` (public client id only) |
| `backend/src/app/schemas/auth/__init__.py` | export it |
| `backend/src/app/api/auth.py` | add `GET /auth/google/config` |
| `backend/src/app/public/repositories/user_repository.py` | add `get_by_google_id` |
| `backend/src/app/public/services/auth_service.py` | set `google_id` on the email-link branch; harden the dangling-link case |
| `backend/src/app/tests/test_auth.py` | Google tests: new user, existing OAuth user, existing email user, inactive user, no duplicate rows, config endpoint, secret never in the response |
| `frontend/services/api/auth.api.ts` | `googleConfig()` |
| `frontend/services/google/google-identity.ts` | **new** — GIS script loader + minimal typings |
| `frontend/hooks/useGoogleAuth.ts` | **new** — shared credential → session flow |
| `frontend/app/(auth)/login/page.tsx` | wire the button (class name and markup unchanged) |
| `frontend/app/(auth)/signup/page.tsx` | wire the button (class name and markup unchanged) |
| `frontend/services/api/auth.api.test.ts` | assert `googleConfig` shape |
| `frontend/hooks/useGoogleAuth.test.ts` | **new** — new user / existing user / failure paths |
| `frontend/app/(auth)/login/page.test.tsx` | Google button wiring |
| `frontend/app/(auth)/signup/page.test.tsx` | Google button wiring |

**Explicitly NOT touched:** `frontend/styles/**` (no CSS), `frontend/config/environment.ts`
(no new public env var needed), `backend/.env`, `backend/.env.example`, `frontend/package.json`
(no new dependency), `authSlice`, `providers.tsx`, `HeaderActions`, the account/admin layouts,
the cart, and the password login/register code paths.

## Testing Results

Automated, repeatable suites — all green (see `google-fix.md` for the exact commands and the
final matrix). Manual browser verification against `accounts.google.com` could **not** be
performed in this environment (no interactive Google session), so the items below are marked
accordingly rather than claimed.

| # | Scenario | Automated | Manual |
|---|---|---|---|
| 1 | New Google user → one customer row, details from verified claims, `role_name=customer` | pass | not run |
| 2 | Same Google `sub` again → same `user_id`, no new row, no new `oauth_accounts` row | pass | not run |
| 3 | Password-registered email, then Google with the same email → same row, password still works, `google_id` backfilled | pass | not run |
| 4 | Google-registered email, then password login → still works, single row | pass | not run |
| 4b | Google-registered email, then **password register** → existing duplicate-email rule answers `409` (not a second row). This project has no "set a password" path for Google-only accounts, so no new one was added. | pass | not run |
| 5 | `id_token` for a different client / tampered / expired → 401, no user, no cookie | pass | not run |
| 6 | `email_verified=false` → 401 | pass | not run |
| 7 | Unknown `provider` value → 401 | pass | not run |
| 8 | Inactive/suspended user → 403, no session | pass | not run |
| 9 | Client secret absent from `/auth/google/config` and from every frontend file | pass | n/a |
| 10 | Cookies set by `/auth/google` are identical to those set by `/auth/login` | pass | not run |
| 11 | `GET /auth/me` with the Google cookie → 200, same shape as password login | pass | not run |
| 12 | Frontend: credential → `setUser` + `setTokenExpiry`, `isAuthenticated === true` | pass | not run |
| 13 | Frontend: `role_name === "admin"` → `/admin`, otherwise `/` | pass | not run |
| 14 | Frontend: backend rejection → local error, **no** redirect, Redux untouched | pass | not run |
| 15 | Frontend: GIS script failing to load → local error, page still usable | pass | not run |
| 16 | Frontend: empty client id from the backend → button disabled with a clear message | pass | not run |
| 17 | Password login and password registration suites unchanged | pass | not run |
| 18 | Full frontend + backend suites green after the change | pass — backend `41 passed` in `test_auth.py`, `268 passed` for `src/app/tests`; frontend `77 suites / 172 tests`; `tsc` `0 errors`; changed files clean under `eslint`/`ruff`/`mypy` | n/a |
| 18b | Three backend defects found while writing the tests, all fixed and covered: case-sensitive `get_by_email` creating a duplicate account, non-idempotent `add_oauth_account` raising `IntegrityError` → 500 on re-link, dangling `oauth_accounts` row → `AttributeError` → 500 | pass | n/a |
| 19 | Real Google consent screen, popup, cancel, and browser-refresh persistence | — | **not run — requires a live Google account** |
| 20 | Guest cart → Google sign-in → cart intact, single cart system | — | **not run — requires a live Google account** |
