# Google OAuth Fix — Implementation Plan

Companion to `google-auth-bug-investigation.md`. Same architecture, minimum changes.

## Summary

The backend Google OAuth flow was already essentially complete. What was missing is the browser
half: the "Continue with Google" buttons on `/login` and `/signup` were placeholders that showed a
toast instead of starting an authentication attempt, and the frontend had no access to the public
client id. Writing the tests then exposed three real backend defects in the same path — a case-
sensitive email lookup, a non-idempotent `add_oauth_account`, and a 500 on a dangling
`oauth_accounts` row — which are fixed here too.

**Rule followed throughout: reuse what exists. Add no second OAuth system, no second login
endpoint, no second user model, no second JWT system, no second auth provider, no second
credential.**

## Non-negotiables checked before starting

| Rule | How it is honoured |
|---|---|
| No new Google client id/secret | `backend/.env` untouched. The public id is **read from the backend**, so it is never written a second time. |
| Secret stays backend-only | `Settings.google_client_secret` is read but referenced by **no** code path. `GET /auth/google/config` returns the public id only. No `NEXT_PUBLIC_GOOGLE_SECRET` exists or is created. |
| No duplicate auth | Reuses `POST /auth/google`, `_issue_tokens`, `_set_auth_cookies`, `authSlice`, `AuthBootstrap`. |
| No duplicate users | Backend matches `oauth_accounts` → `users.email` → create. Both existing stores are honoured. |
| No hard-coded Google data | Every field comes from a server-verified `id_token` claim. The frontend never reads the Google profile. |
| No unverified profile trust | The frontend posts only the `id_token`; the backend re-verifies signature, `aud`, `exp` and `email_verified`. |
| No CSS change | `frontend/styles/**` untouched. The existing `login-google` / `signup-google` buttons and their markup are kept as-is. |
| Do not break login / register / cart / admin | Password paths untouched. Full suites run before and after. |

## Why the client id comes from the backend

`backend/.env` already owns `GOOGLE_CLIENT_ID`, and the verification path uses that same value as
the expected `aud`. Duplicating it into `frontend/.env.local` would create a second copy that can
silently drift — a Google sign-in failing with an opaque 401 after someone rotates the client.

`GET /auth/google/config` is a read-only, unauthenticated, non-secret read. It makes the backend
the single source of truth, adds no credential, and cannot leak anything sensitive. It degrades to
`{"client_id": ""}`, which the frontend turns into a disabled button and a clear message rather
than a crash.

`GOOGLE_REDIRECT_URI` is intentionally left unused: this flow uses a Google-signed `id_token`
delivered in-page, not an authorization code, so no redirect URI is involved.

## Changes, in order

### 1. Backend — public client id (read-only)

- `backend/src/app/schemas/auth/oauth.py` — add `OAuthProviderConfigResponse` (`client_id: str`).
- `backend/src/app/schemas/auth/__init__.py` — export it.
- `backend/src/app/api/auth.py` — `GET /auth/google/config` → `{"client_id": settings.google_client_id}`.
  Declared **before** `POST /auth/google` so the router table reads config-then-exchange.

### 2. Backend — link consistency (no behaviour change for existing links)

Found while writing the tests, not visible in the static read:

- `public/repositories/user_repository.py` — `get_by_email` now normalises with
  `email.lower().strip()`. Register and the email OTP verifier already lower-cased, so a stored
  address and a login lookup could disagree on case; Google delivers addresses folded too, and
  `users.email` is unique, so an un-normalised lookup silently created a second account instead of
  reusing the existing one.
- `public/repositories/user_repository.py` — `add_oauth_account` is now **idempotent**. It used to
  unconditionally `add()` a fresh `OAuthAccount`, which violated the
  `(provider, provider_account_id)` unique constraint whenever a link already existed (re-linking a
  previously-linked email raised `IntegrityError` → 500). It now fetches-or-creates, and repairs a
  row whose `user_id` points at a different account.
- `public/repositories/user_repository.py` — add `get_by_google_id` (needed to guard the unique
  column when backfilling).
- `public/services/auth_service.py` `_find_or_create_google_user`:
  - dangling `oauth_accounts` row (user deleted) currently returns `None` and then
    `AttributeError` → 500. Fall through to the email branch instead.
  - `email` is normalised before creating the new user, so it matches the unique index.
- `public/services/auth_service.py` `_link_google_identity` (new) — shared by the existing-email
  branch, always calls the idempotent `add_oauth_account`, and backfills `users.google_id` only
  when the column is free and no other user holds that `sub`. It never overwrites existing profile
  fields, so a Google sign-in cannot rename an account the customer already filled in.

### 3. Frontend — GIS loader (new)

`frontend/services/google/google-identity.ts`

- `loadGoogleIdentity(): Promise<GoogleIdentity>` — injects
  `https://accounts.google.com/gsi/client` once; module-level promise de-duplicates concurrent and
  repeated calls; rejects on `script.onerror` so the page can show a real error.
- Minimal local typings for `google.accounts.id` (`initialize`, `prompt`, `cancel`, the
  `CredentialResponse` and the `PromptMomentNotification` reasons). **No new npm dependency** —
  `@types/google.accounts.id` is not installed and `frontend/package.json` is left alone.

### 4. Frontend — shared sign-in hook (new)

`frontend/hooks/useGoogleAuth.ts`

One implementation, used by both pages, mirroring the password path in
`login/page.tsx:45-59` step for step:

```
read public client id (GET /auth/google/config)
  → loadGoogleIdentity()
  → google.accounts.id.initialize({ client_id, callback, ux_mode: "popup", use_fedcm_for_prompt: true })
  → google.accounts.id.prompt()
  → credential.credential  (a Google-signed id_token)
  → authApi.googleLogin({ provider: "google", id_token })
  → dispatch(setTokenExpiry(Date.parse(tokens.expires_at)))
  → authApi.me()
  → dispatch(setUser({ id, name, email, role_name }))
  → return the UserResponse so the page can toast and redirect by role
```

Details that matter:

- `credential` is the **only** value read from Google's response. No `name`/`email` from the
  browser is trusted or forwarded; the backend derives everything from verified claims.
- `prompt` moment notifications are handled so the spinner always clears:
  `isNotDisplayed` / `isSkippedMoment` → one silent retry (Google's documented behaviour) then a
  local error; `isDisabled` / `isDismissedMoment` → local error. The user is never left spinning
  and is never redirected on failure.
- The `id_token` is discarded after the request, exactly like the password path discards its
  tokens — the session lives in HttpOnly cookies the backend set.
- Returns the user instead of redirecting, so each page keeps its own toast copy and applies the
  existing rule `role_name === "admin" ? "/admin" : "/"`.

### 5. Frontend — wire the two buttons

`frontend/app/(auth)/login/page.tsx`, `frontend/app/(auth)/signup/page.tsx`

- Replace the placeholder `onClick` with the hook's handler.
- Keep `<button className="login-google">` / `<button className="signup-google">` and their
  children exactly as they are → **no CSS change**.
- Disable the Google button while a request is in flight, and while the password form is
  submitting, so two sessions cannot be created at once.
- Reuse each page's existing `notify()` for success and failure, so the UI language and the
  `2500ms` toast behaviour are unchanged.
- On success apply the existing role redirect; `/signup` also lands on `/admin` or `/` rather than
  back on `/login`, because a Google registration is already authenticated.

### 6. Tests

Added:

- `backend/src/app/tests/test_auth.py` — new-user creation, existing-`sub` reuse, existing-email
  link (incl. `google_id` backfill and password still working), reverse order, inactive user,
  tampered/wrong-audience token, `email_verified=false`, unknown provider, no duplicate rows,
  case-insensitive email reuse, `google_id` not taken over from another user, dangling
  `oauth_accounts` row recovery, config endpoint returns the id and **never** the secret, and
  cookies from `/auth/google` matching `/auth/login` including refresh rotation and logout.
- `frontend/services/api/auth.api.test.ts` — `googleConfig()` request shape.
- `frontend/hooks/useGoogleAuth.test.ts` (new) — success sets `isAuthenticated` + expiry; admin vs
  customer is surfaced through the returned user; backend rejection leaves Redux untouched and
  resolves with `null`; empty client id refuses without touching the network; a `null` credential,
  a GIS load failure and a rejected `POST /auth/google` all clear the spinner and resolve `null`.
- `frontend/app/(auth)/login/page.test.tsx`, `signup/page.test.tsx` — the buttons start a Google
  attempt instead of showing the placeholder toast, and land on `/admin` vs `/` by role.

Existing password login / registration tests were left untouched and stayed green.

One expectation was **corrected** rather than added: signing up with a password using the email of a
Google-only account is rejected with `409` by the existing duplicate-email rule. The test now pins
that existing behaviour (one account, no `409` → `201` regression) instead of inventing a
"set a password" path, which this project does not have.

## Verification

```
backend : cd backend;  .\.venv\Scripts\python.exe -m pytest src/app/tests/test_auth.py -q
backend : cd backend;  .\.venv\Scripts\python.exe -m pytest src/app/tests -q
frontend: cd frontend; npm test
frontend: cd frontend; npm run lint
frontend: cd frontend; npx tsc --noEmit
```

Use `.\.venv\Scripts\python.exe`, not `uv run`: `uv run` fails before collection with
`Failed to build backend` / `Expected a Python module at: src\backend\__init__.py`, an existing
packaging mismatch between `pyproject.toml` and the flat `src/app` layout.

Results:

| Check | Result |
|---|---|
| `pytest src/app/tests/test_auth.py -q` | **41 passed** |
| `pytest src/app/tests -q` (full backend) | **268 passed** |
| `npm test` (full frontend) | **77 suites, 172 tests passed** |
| `npx tsc --noEmit` | **0 errors** |
| `npx eslint` on the nine changed/added frontend files | **0 errors, 0 warnings** |
| `ruff check` on the changed backend files | **clean** |
| `mypy` on the changed backend files | **clean** |

`npm run lint` over the whole project still reports 3 pre-existing `react-hooks` errors in
`app/admin/components/AdminChatPage.tsx`, which belongs to unrelated chat work and is not touched by
this change.

Manual end-to-end against `accounts.google.com` (needs a real Google session) — not performed in
this environment, tracked in `google-auth-bug-investigation.md` § Testing Results rows 19-20.

## Order of work

Automated rows are done; rows 25-26 need a real Google session in a browser and were not run here.

1. ✅ Inspect project
2. ✅ Find existing Google credentials/configuration
3. ✅ Inspect Login page
4. ✅ Inspect Register page
5. ✅ Inspect backend OAuth implementation
6. ✅ Inspect User model
7. ✅ Inspect JWT/session implementation
8. ✅ Inspect cookies
9. ✅ Inspect auth provider
10. ✅ Inspect role routing
11. ✅ `google-auth-bug-investigation.md`
12. ✅ Document actual bugs
13. ✅ This plan
14. ✅ Implement minimum required changes
15. ✅ Test new Google user
16. ✅ Test existing Google user
17. ✅ Test existing email account
18. ✅ Test login persistence
19. ✅ Test refresh
20. ✅ Test direct URLs (backend `require_user_or_guest` / admin 401-403 assertions)
21. ✅ Test logout
22. ✅ Test customer role
23. ✅ Test admin protection
24. ✅ Test cart (guest cart survives; no cart code touched — no `frontend/hooks/useCart.ts` or `store/slices/cartSlice.ts` change from this work)
25. ⬜ Final end-to-end regression against live Google
26. ⬜ Manual matrix: new user, returning user, popup cancel, browser refresh of a protected URL
