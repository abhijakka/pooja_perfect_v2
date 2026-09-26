# Chat Bug Fix Plan

**Companion to:** `chat-bug-investigation.md` (all evidence, measurements and file:line references live there).
**Status:** Phase 1 and Phase 3 **implemented and verified** on 2026-09-26. Phases 2 and 4–6 are
still plan-only. See [Implementation log](#implementation-log) for exactly what changed.
**Date:** 2026-09-26

## Ground rules

1. **Backend is the source of truth.** Every fix that decides *what* the user sees (identity,
   ownership, ordering, timestamps, unread) is made on the backend. Frontend changes are rendering
   and delivery concerns only.
2. **Keep the existing architecture.** GraphQL stays GraphQL. The hand-rolled
   `graphql-transport-ws` client stays. The in-process `SimplePubSub` stays. Nothing is replaced by
   polling, nothing is rewritten in a second style.
3. **No CSS changes.** `app/globals.css` and `app/admin/styles/admin_style.css` are untouched.
   Where a fix needs a new piece of chrome (e.g. a "load older" control) the existing classes are
   reused.
4. **Do not touch concurrent work.** `bug-authentication.md` and `bug-view-product.md` are in
   flight in the same working tree. `api/auth.py`, `dependencies/auth.py`,
   `public/dependencies.py`, `providers.tsx`, all cart/product/navbar files are **out of scope**
   except where C1 unavoidably requires a change, which is called out explicitly in F1.
5. **Verify, never assert.** Every fix ships with the command that proves it, run before and after.

## Baseline to beat

```
backend   pytest src/app/tests/test_public_chat.py src/app/tests/test_admin_chat.py -q   -> 17 passed
frontend  npx tsc --noEmit   -> 6 errors, all chat
frontend  npx jest           -> 3 failed / 144 passed / 147 total
frontend  npx next build     -> Compiled successfully, then Failed to type check
```

Target after all fixes:

```
backend   pytest (chat)                                    -> 17 passed + new tests, 0 failed
frontend  npx tsc --noEmit                                 -> 0 chat errors
frontend  npx jest                                         -> 0 chat failures (non-chat pre-existing failures unchanged)
frontend  npx next build                                   -> type check passes
```

### Achieved after Phase 1 + Phase 3 (2026-09-26)

```
backend   pytest (chat)                                    -> 20 passed, 0 failed  (17 baseline + 3 new)
backend   pytest src/app/tests (full suite)                -> 268 passed, 0 failed
frontend  npx tsc --noEmit                                 -> 0 errors (whole repo, not just chat)
frontend  npx jest                                         -> 77 suites / 172 tests, 0 failed
frontend  npx next build                                   -> Compiled successfully, 42/42 pages, type check passes
```

The non-chat failures that were open at baseline (`signup`, product/cart) were resolved by the
concurrent auth/product work in the same tree, so the whole-repo numbers are green as well.

---

## Phase 1 — Unblock the build and the test harness

Nothing else can be verified until the chat type-checks and Jest can load the real chat context.

### F1 (C5) — delete the dead stub that shadows the real chat context  ·  ✅ **DONE**

`context/ChatContext/index.ts` is 32 bytes: `export const ChatContext = {};`. It sits beside the
real 446-line `context/ChatContext/index.tsx` and shadows it for `tsc` and for `next/jest`.

**Action:** delete `frontend/context/ChatContext/index.ts`. Nothing imports it — the only importer,
`app/providers.tsx:16` and `hooks/useChat.ts:1`, both want `ChatProvider` / `useChat`, which live in
`index.tsx`.

**Verify:** `npx tsc --noEmit` → the two `TS2305` errors are gone. Then a new test that imports the
real context (not a mock) can resolve `ChatProvider` and `useChat`.

**Risk:** low. If any code genuinely imported the stub, `tsc` would already have failed differently.

### F2 (C5) — clear the remaining four chat type errors  ·  ✅ **DONE**

* `app/admin/components/AdminChatPage.tsx:133` — the WS `onMessage` payload is typed `ChatMessage`
  (`createdAt: string | null`) but pushed into `AdminChatMessage[]` (`createdAt: string`). Fix by
  mapping explicitly at the boundary rather than widening the type:
  `incoming as AdminChatMessage` is **not** acceptable — narrow `createdAt` with a real guard.
* `components/chat/SupportChat.tsx:145` and `components/chat/ChatApplication.tsx:124` — implicit
  `any` on the `messages.map` callback. Type the callback parameter.
* `services/websocket/chat.socket.ts:134` — `pingTimer` typed `Timeout`, assigned
  `window.setTimeout`'s `number`. Use `ReturnType<typeof window.setTimeout> | null`, and clear it
  with `window.clearInterval` (already what the code does) — or switch the field to `number | null`.

**Verify:** `npx tsc --noEmit` reports **0 errors in chat files**.

### F3 (L3, L4) — repair the two out-of-sync chat test suites  ·  ✅ **DONE**

* `SupportChat.test.tsx:75` queries `getByLabelText("Your name")`; the component's `aria-label` is
  `"Enter your name"` (`SupportChat.tsx:191`). Align the test to the component.
* `app/(public)/chat/page.test.tsx` fails on `bodyRef.current?.scrollTo is not a function`
  (`ChatApplication.tsx:40`). Add the same `Element.prototype.scrollTo` stub that
  `SupportChat.test.tsx` already installs in `beforeAll`. Cleaner: put the stub once in
  `jest.setup.ts` so both suites get it.

**Verify:** `npx jest` → chat suites green.

**Note:** `app/(auth)/signup/page.test.tsx` also fails, but it is `bug-authentication.md` work.
Leave it; record it as pre-existing.

---

## Phase 2 — Make realtime delivery actually work (C1, C2)

This is the highest-value fix in the whole task: it turns 6 failing scenarios green.

### F4 (C1) — make the auth dependencies ASGI-scope-agnostic

The failure is `HTTPBearer.__call__() missing 1 required positional argument: 'request'`, because
FastAPI only injects the `request` argument for HTTP scopes
(`fastapi/dependencies/utils.py:711-714`) while Strawberry resolves the context getter during the
WebSocket upgrade (`strawberry/fastapi/router.py:248-254`).

`HTTPBearer` is unusable in any dependency that must also run in a WS scope. Replace it with a
hand-written scheme that accepts both scopes.

**Action** — `backend/src/app/dependencies/auth.py`:

```python
# Replace:
bearer_scheme = HTTPBearer(auto_error=False)

# With a scope-agnostic extractor. Accept the ASGI object as either
# Request or WebSocket; both expose .headers and .cookies.
```

Then change every `credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)]`
to take the ASGI object directly and pull the scheme/credentials out of `scope["headers"]` (or
`obj.headers.get("authorization")`). Apply in **both** `dependencies/auth.py` and
`public/dependencies.py`.

`resolve_access_token(request, credentials)` already falls back to the `access_token` cookie, so the
WS path (which carries cookies on the handshake) keeps working with no extra work.

**Acceptance:**
```
TestClient(app).websocket_connect("/graphql", subprotocols=["graphql-transport-ws"])
  -> connects, receives connection_ack
```
and the same for `/admin/graphql` **with an admin token**, plus 401 without one.

**Regression guard:** `POST /admin/graphql` must still return 401 with no token and 403 with a
customer token (currently correct — do not regress it).

**Scope note:** this file is currently being edited by the concurrent `bug-authentication.md` work.
Re-read it immediately before editing and keep the change surgical.

### F5 (C2) — make the public context WebSocket-safe

`public/context.py:33` takes `response: Response` and line 41 calls `response.set_cookie(...)`.
There is no `Response` in a WS scope, so F4 alone converts the `TypeError` into an `AttributeError`.

**Action:** make the `Response` dependency optional and skip the cookie write when it is absent:

* Accept the ASGI object as `Request | WebSocket`.
* Only call `set_cookie` when a real `Response` is available.
* In a WS scope, resolve `guest_token` from the request cookies only. If the handshake carried no
  `guest_token`, the guest falls back to `require_user_or_guest` creating a fresh anonymous user —
  acceptable, because **a browser always has the cookie by the time it opens a socket** (it was set
  on the first HTTP `/graphql` call that the widget makes before subscribing).

**Acceptance:** an unauthenticated browser can open `WS /graphql` and receive `connection_ack`.

### F6 — verify the full realtime round trip

Once F4 + F5 land, prove the whole path with an async test, not a manual click:

1. Guest opens `WS /graphql`, subscribes `chatMessage(conversationId)`.
2. `sendChatMessage` over HTTP.
3. Assert the frame arrives on the socket **with `mine: true`**.
4. Admin opens `WS /admin/graphql` for the same conversation, replies over HTTP.
5. Assert the guest's socket receives it **with `mine: false`**.
6. Assert **no duplicates** across socket + the 8 s poll.

Requires enabling `pytest-asyncio` (`asyncio_mode`) — currently installed and configured nowhere,
and there is zero subscription test coverage today.

**Also fix while here:** `chat.socket.ts` give-up is silent. After `MAX_RECONNECTS` the client stops
trying and nothing tells the user. At minimum log it; ideally surface a "reconnecting" state so the
polling fallback is visible rather than mysterious. `disposeChatSocket()` / `disposeAdminChatSocket()`
are exported and never called (`chat.socket.ts:249-255`) — wire them into a provider teardown.

---

## Phase 3 — Correctness of identity, ownership and authorization (C4, L1, L2, L11)

### F7 (C4) — close the guest identity-takeover hole  ← **security, do this carefully**  ·  ✅ **DONE**

Current behaviour (`public/services/chat_service.py:65-78` + `public/api/graphql/mutations/chat.py:53-61`):
if the guest's typed email already belongs to a registered user, the server adds that registered
user as a participant on the visitor's conversation **and** hands the visitor a conversation owned
by the registered account.

The safe behaviour, and the one the data model already supports: **an anonymous caller must never
gain access to, or ownership of, an account identified only by an unverified email string.**

**Action in `set_guest_identity` (`public/services/chat_service.py`):**
* Stop returning `existing_user`. It must always return the *caller's own* user.
* Stop adding `existing_user` as a participant of the caller's conversation.

**Action in `mutate_start_conversation` (`public/api/graphql/mutations/chat.py`):**
* Remove the `if user.id != original_user.id` block entirely (lines 58-61). With F7's first change
  `user.id` is always `original_user.id`, so the block is dead — delete it rather than leave it.
* Do **not** set `force_new = True` based on an email match.

**What replaces it** — and this is where the brief's §7 ("follow the existing backend data model")
and §20 ("do not invent behaviour") matter. The data model already distinguishes these two cases
cleanly, and the correct, minimal, non-inventive rule is:

| Caller | Email typed | Correct behaviour | Why |
|---|---|---|---|
| guest | new / unused | Update **the guest's own row** with that name + email. Conversation stays with the guest. | The visitor identified themselves; no proof needed to rename yourself. |
| guest | belongs to a registered user | Keep the conversation with the **guest's own row**. Leave the registered user's account completely untouched. Do not merge, do not link, do not transfer. | There is no verification, so the only safe reading is "this is still the anonymous visitor". |
| authenticated | anything | Ignore `name`/`email` entirely (already the case, `mutations/chat.py:49`). | Identity comes from the session. |

This is **not** a merge and **not** a link — it is the explicit decision *not* to merge, which is
what §20 asks to be documented. The consequence to accept and document: a guest who later registers
(or logs in) starts a **separate** conversation, because the guest row and the registered row are
different users and nothing links them. That is the pre-existing model, and inventing a merge would
require email verification, which does not exist in this project.

**Acceptance (re-run the C4 repro, inverted):**
```
1. attacker startConversation(name:"Attacker", email:"victim_…@registered.com") -> 200, conversation C
2. victim authenticates and lists conversations
   -> must NOT contain C
3. attacker can still read and post in C using their own cookie
4. guests table: no new participant row for the victim on C
```

### F8 (L1, L2) — identity hygiene for guests  ·  ◐ **PARTIAL** (`last_name` done, `is_guest` not done)

* `chat_service.py:81` — `user.last_name = name` produces `"Ravi Ravi"` in the admin UI
  (measured). Set `first_name = name` and leave `last_name` empty, or store the whole string in
  `first_name` and let the admin view render `first_name` when `last_name` is blank. Preferred:
  keep `first_name = name`, set `last_name = ""`. The admin view already does
  `.strip()` on the join (`admin/repositories/chat_repository.py:122`), so `"Ravi"` renders
  correctly.
* `chat_service.py:80-83` — set `is_guest = False` once the guest supplies a name + email, so a
  self-identified lead is not permanently classified as anonymous.

### F9 (L11) — do not mint a guest user on every call for a cookieless client  ·  ✅ **DONE** (implemented via `optional_user_or_guest`)

`context.py:63-79` creates a `users` row per request when no `guest_token` exists. Measured: two
consecutive `activeConversation` calls from a cookieless client each minted a fresh guest.

**Action:** if there is no `guest_token` cookie, do not fabricate a persisted user for
*read-only* operations. Return "no conversation" instead. Keep fabrication for the mutations that
genuinely need a user (`startConversation`, `sendChatMessage`), where the cookie will have been set
by the same response.

---

## Phase 4 — Timestamps and ordering (C3, H1, H2, M1)

### F10 (C3) — emit unambiguous, high-resolution UTC timestamps  ← **fixes every visible time**

**Backend, `models/base.py:18-27`:** replace the DB-side `server_default=func.now()` for
`chat_messages.created_at` with a **Python-side default of `datetime.now(UTC)`**. This single change
fixes three defects at once:

1. **Timezone** — a tz-aware UTC datetime serializes with an explicit offset
   (`2026-09-25T19:07:06+00:00`), so the browser can no longer misread it as local time.
2. **Resolution** — microseconds instead of 1 second.
3. **Ordering ties** — see F11.

Existing rows are already stored as naive UTC, so they keep rendering correctly under the new
parse rule. **No migration is required** for correctness; add one only if you want the column
default itself changed for non-Python writers. Verify the Alembic chain
(`9a1b2c3d4e5f` is current) before deciding.

**Frontend, single shared parser.** `ChatContext/index.tsx:63-72` (`formatTime`) and
`AdminChatPage.tsx:21-39` (`clockTime`, `timeAgo`) each hand-roll their own. Replace all three with
one helper in `lib/utils/date.ts` (the file already exists and is currently unused by chat) that:

* Parses the value, **forcing UTC when the string carries no offset** — this is the actual bug
  today, and it must be fixed for the 32 pre-existing rows too, not only for new ones.
* Formats in the **viewer's local** timezone via `Intl`/`toLocaleTimeString` (no `timeZone` option),
  which is what a user expects.
* Handles null / unparseable values by returning `""`, as both current implementations do.

Keep the existing display format — the brief says follow the current UI. `toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'})`
already produces `10:31 PM` in en-US and `10:31 pm` in en-IN; that is acceptable, do not force a
locale.

**Acceptance:** with the machine at IST, a message inserted at `00:37 IST` displays as `12:07 AM`,
for both guest and admin, and the two agree with each other.

### F11 (H1) — make message ordering deterministic

Two layers, both required.

**Backend:** every `ORDER BY ChatMessage.created_at` gets an explicit tie-breaker.
F10's microsecond precision makes ties vanishingly unlikely, but "unlikely" is not a guarantee, and
`OFFSET` pagination over a non-unique sort key can duplicate or drop rows across pages.

Preferred: order by `(created_at, id)`. Note `id` is `uuid4` (`models/base.py:15`) so it is stable
but **not** chronological — it guarantees *determinism* (no dup/drop across pages), which is the
correctness requirement, while microsecond timestamps supply the ordering. If true monotonic
ordering is wanted, the honest fix is an autoincrement `seq` column via a new Alembic migration;
raise that as a follow-up rather than pretending `id` is a sequence.

Apply in:
* `public/repositories/chat_repository.py:162` (`messages`)
* `admin/repositories/chat_repository.py:165` (`messages`)
* `admin/repositories/chat_repository.py:95` (`_build_views` last-message scan)
* `public/repositories/chat_repository.py:136` (`latest_message`)

**Frontend (H2):** stop relying on arrival order.
* `store/slices/chatSlice.ts:83-88` — after the id-dedupe, insert at the correct chronological
  position instead of `push`. The UI message type (`types/chat.ts`) must carry the sort key; today
  `toUiMessage` (`ChatContext/index.tsx:74-81`) discards `createdAt` and keeps only a formatted
  `time` string, so **add `createdAt` (and `id`) to `UiChatMessage`** and sort on it.
* `AdminChatPage.tsx:133-137` — same.

Do not remove the id-dedupe; it is what stops the socket and the poll double-delivering.

### F12 (M1) — advance `conversations.updated_at` when a message is sent

Measured: `updatedAt` is unchanged after 3 sends, so the admin list (`ORDER BY updated_at DESC`,
`admin/repositories/chat_repository.py:54`) does not surface new activity.

**Action:** in both `send_message` implementations, touch the parent conversation
(`conversation.updated_at = datetime.now(UTC)` or `conversation.last_message_at = ...`).
Cheapest correct form: `UPDATE conversations SET updated_at = :now WHERE id = :id` in the same
transaction as the message INSERT.

### F13 (M5) — stop truncating history silently

* **Admin:** `AdminChatPage.tsx:89` fetches page 1 × 100 with no pagination. Add a "load older"
  control that walks `page` forward and prepends, reusing the existing reverse-per-page logic.
* **Public:** `ChatContext/index.tsx:134-149` hard-caps at 5 × 50 = 250. Replace the magic `5` with
  a constant and, when `hasNext` is still true after the last page, show the existing empty-state
  styling with "load earlier messages". **No new CSS.**
* Report the true total from the API (already available: `pagination.total`) so the UI can say so.

---

## Phase 5 — Unread / read state (H4, M2, L5)

The brief says: *"Do not implement read/unread behavior if the existing application does not support
it unless explicitly required."* The application **does** support it, but only for admins, and the
customer side is measurably broken (after an admin reply `unreadCount` stays `0` and the customer
gets nothing). So this is a **gap in existing behaviour**, not a new feature — but it needs a
storage decision, and that decision is not mine to make silently.

### F14 (H4) — decide the read model, then implement it once

`is_read` is a single global boolean per message (`models/chat_message.py:37`), so "read by the
admin" and "read by the customer" cannot coexist. The dead helper at
`public/repositories/chat_repository.py:140-147` shows per-reader counting was already intended.

**Recommended (matches the existing schema shape, smallest honest change):**
add a `conversation_reads` table `(conversation_id, user_id, last_read_at)`, PK
`(conversation_id, user_id)`. Then:
* `unread_count` = messages in the conversation with `created_at > last_read_at` and
  `sender_id != reader_id`. Works identically for admin and customer.
* Public `markRead(conversationId)` mutation.
* Keep `is_read`/`read_at` in place for one release so nothing else breaks, then drop them.

**Alternative (cheaper, partial):** keep the boolean, add a public `markRead` that only ever marks
*admin-sent* messages, and accept that it collides with the admin's own marking. **This is
inferior and I do not recommend it** — it produces exactly the bug being reported.

**Decision needed from the product owner:** which of the two. F14 should not start until that is
answered, because the storage choice is a one-way door.

### F15 (H3) — decouple delivery from panel visibility

`ChatContext/index.tsx:275` and `:285` both bail on `!chat.open`. Consequences, both measured:
* Nothing is fetched while the widget is closed, so admin replies are not noticed.
* `appendMessage` only sets `unread` when `!state.open` (`chatSlice.ts:87`) — a state that can
  never be reached, so the unread badge is **unreachable dead code**.

**Action:** drop `!chat.open` from both guards. Subscribe and poll whenever there is a
`conversationId` and it is not ended. Then `unread` becomes reachable, and:
* Replace the hard-coded `1` (`SupportChat.tsx:98`) with a real count from the backend.
* `openChat` already clears `unread` (`chatSlice.ts:40-43`).

Cost: a poll per open conversation for every visitor. Keep the 8 s interval but only for
conversations with a `conversationId`, and let the (now working) socket be the primary path.

### F16 (L5) — clear the admin unread chip immediately

`selectConversation` (`AdminChatPage.tsx:166-170`) fires `markChatRead` and ignores the result, so
the header total (`:164`) is stale until the next 10 s poll. Zero the selected conversation's
`unreadCount` in local state on selection, then reconcile with the server response.

---

## Phase 6 — Input validation and error handling (M3, M4, M5)

### F17 (M3) — enforce a message length cap where it is reachable

`schemas/chat/message.py:12` declares `max_length=10000` but `app.schemas.chat` is imported
nowhere, so it is dead code. Measured: 20 000 characters accepted.

**Action:** validate in `public/services/chat_service.py:send_message` and
`admin/services/chat_service.py` alongside the existing blank check (`:125-126`). Delete the dead
`schemas/chat/` package or wire it in — do not leave a second, unreachable validation lying around.

### F18 (M4) — make public GraphQL errors match admin errors

`admin/api/graphql/schema.py:331-355` registers `_AppErrorExtension`; the public schema
(`public/api/graphql/schema.py:224-228`) does not. Result: public business errors log a full Python
traceback and ship raw text to the client.

**Action:** register the same extension on the public schema. Then convert the raw
`pydantic.ValidationError` from `PaginationInput` into a clean `ValidationError` in the public and
admin chat resolvers, so `page: 0` returns a message instead of
`"1 validation error for PaginationInput\npage\n  Input should be greater than or equal to 1"`.

### F19 — error handling in the UI

Both surfaces currently swallow the real cause:
* `ChatContext:150-156` — `loadMessages` discards the error, shows a generic string, **and clears
  the stored conversation id**, so one transient network blip silently discards the customer's
  session pointer.
* `AdminChatPage` — every call is `.catch(() => notify("Could not load …"))`; a 401 is
  indistinguishable from a 500, while the global handler silently redirects to `/`.

**Action:** surface the real message; do **not** clear `pp-chat-conversation` on a network error
(only on a genuine 403/404 "not found / not a participant"). Add a distinct 401 path.

### F20 (L10) — validate `Origin` on the WebSocket upgrade

CORS does not govern WebSockets and the server does not check `Origin`. Once F4 lands, add the
check in the WS path against the same three origins already listed in `main.py:21-25`.

---

## Execution order

```
Phase 1  F1  F2  F3      unblock build + jest          (no behaviour change)
Phase 2  F4  F5  F6      realtime delivery works        (C1, C2)
Phase 3  F7  F8  F9      identity + authorization       (C4, L1, L2, L11)
Phase 4  F10 F11 F12 F13 timestamps + ordering + history (C3, H1, H2, M1, M5)
Phase 5  F14 (blocked on decision) F15 F16             (H4, H3, L5)
Phase 6  F17 F18 F19 F20 validation + errors           (M3, M4, L10)
```

Phase 3 (F7) is a **security** fix and should not wait for the rest.
Phase 5 (F14) is gated on a product decision about the read model.

Each phase ends with its own verification run before the next begins.

## Regression suite to add

Backend (`src/app/tests/`), all currently missing:

| Test | Proves |
|---|---|
| `websocket public connect + subscription` | F4/F5 — WS connects, `connection_ack` received |
| `websocket admin requires admin token` | F4 — 401 without, works with |
| `realtime customer -> admin` | F6 — frame arrives without refresh |
| `realtime admin -> customer` | F6 — frame arrives without refresh |
| `no duplicate frames across socket + poll` | F6, F11 |
| `guest cannot claim registered email` | F7 — the C4 repro, inverted |
| `guest email is stored on the guest's own row` | F7 |
| `authenticated user ignores name/email args` | F7 |
| `ordering deterministic for same-second messages` | F11 — send 5 in one second, assert stable order across 2 pages |
| `timestamps carry UTC offset` | F10 |
| `conversations.updated_at advances on send` | F12 |
| `message length cap enforced` | F17 |
| `public errors carry extensions.code` | F18 |
| `pagination errors are clean messages` | F18 |
| `customer markRead` (after F14) | F14 |

Frontend:

| Test | Proves |
|---|---|
| real `ChatContext` resolves without a mock | F1 — the C5 guard |
| `appendMessage` inserts chronologically, not at tail | F11 |
| timestamps render in local time from a zoneless UTC string | F10 |
| unread badge reflects a real count | F15 |
| socket is torn down on unmount | F6 |

`pytest-asyncio` is installed and configured nowhere; F6 and the subscription tests need
`asyncio_mode` configured. There is currently **zero** subscription coverage.

## Explicitly not doing

* No CSS edits — no redesign of chat bubbles, admin layout, loaders or navbar.
* No replacement of the WebSocket architecture with polling. The socket client is sound; the server
  is what is broken.
* No second communication mechanism. The existing socket + 8 s poll pairing stays, with the dedupe
  that makes it safe.
* No mock, static or fallback chat data. The backend stays the only source of truth.
* No changes to the concurrent `bug-authentication.md` / `bug-view-product.md` work, except the
  surgical change F4 requires in `dependencies/auth.py` and `public/dependencies.py`.
* No email-verification, OTP or rate-limiting infrastructure for F7 — it does not exist in this
  project and inventing it is out of scope. F7's fix is to stop trusting the unverified email, not
  to verify it.
* No `Redis` fan-out for the pub/sub, despite `redis` being installed. The in-process
  `SimplePubSub` is correct for a single-instance deployment and its own docstring already flags
  the multi-instance case as a known follow-up.

---

## Implementation log

### F1 — done

Deleted `frontend/context/ChatContext/index.ts` (the 32-byte `export const ChatContext = {};` stub
that shadowed `index.tsx`). Jest and `tsc` now resolve the real provider. Cleared TS2307 and the two
TS7006 implicit-`any` errors that the stub was causing.

Side effect worth recording: a stale `tsconfig.tsbuildinfo` still referenced the deleted path and made
`tsc` report `TS6053: File .../context/ChatContext/index.ts not found`. The file is a gitignored
build artifact (`frontend/.gitignore:40 *.tsbuildinfo`); deleting it cleared the error. Anyone who
deletes a source file in this repo should re-run `tsc` after clearing that cache.

### F2 — done

* `frontend/services/websocket/chat.socket.ts` — added the missing `AdminChatMessage` type import,
  typed the ping timer as `number | null`, and added `AdminSubscriptionOptions` for the admin
  subscription callback map.
* `chat.socket.ts` `subscribeToAdminChat` now drops any frame whose `createdAt` is not a string
  before using it, so one malformed payload can no longer crash the admin socket handler.

Both remaining chat type errors cleared. Note the chat type errors were the *only* errors in the repo
at this point; `tsc --noEmit` is now completely clean.

### F3 — done

* `frontend/components/chat/SupportChat.test.tsx` — the test queried `getByLabelText("Your name")`
  but the component's input is `aria-label="Enter your name"` (`SupportChat.tsx:191`). The component
  was right and the test was stale, so the test was corrected, not the markup.
* Moved the `Element.prototype.scrollTo` stub from that one suite into `frontend/jest.setup.ts`, so
  every suite that renders a chat panel gets it. jsdom does not implement `scrollTo` at all.
* Added a guest-email-step test to `SupportChat.test.tsx`; the existing "walks a guest through name
  and email" case only ever exercised the name step, so the email step had no coverage at all.

Chat suites: 2 files / 9 tests green. Full frontend suite is 77 files / 172 tests green.

### F7 — done, and this is the one that mattered

The hole: `set_guest_identity` looked up the submitted email, and on a hit it added the *registered
user* as a participant of the *anonymous caller's* conversation and then **returned the registered
user**. `mutate_start_conversation` compounded it by forcing `force_new = True` and re-adding the
original guest as a second participant. So typing someone else's email handed you their identity
and injected you into their thread. No password, no email verification, nothing.

The fix, in `backend/src/app/public/services/chat_service.py`:

* `set_guest_identity` now **always returns the caller's own row**. It never returns, joins, or
  rewrites a registered account.
* When the self-declared email collides with a real account, the guest keeps their own generated
  `guest-<hex>@guest.local` address. `users.email` is unique, so this also keeps the write legal
  instead of raising an integrity error.
* The participant-transfer block and the `existing_user` lookup result are gone.
* `mutate_start_conversation` dropped the `force_new` escalation and the "re-add the original guest"
  block. It no longer compares user ids at all, because the service no longer changes identity.

The registered account is left **completely** untouched: not a participant of the impostor's
conversation, not merged, not renamed, and its own history stays intact and readable.

Verified in `test_public_chat.py`:

* `test_existing_email_creates_new_conversation` — rewritten. The old version only asserted "new
  conversation id differs" and "0 messages", which the vulnerable code also satisfied; it never
  checked the thing that actually mattered. It now asserts the guest conversation has exactly one
  participant and that it is not the victim, the victim conversation still has exactly the victim,
  the impostor can neither read nor post into the victim's conversation, and the victim can still
  read their own conversation with 0 messages.
* `test_guest_claiming_registered_email_never_writes_that_email` — new. Snapshots the victim's user
  row before and after and asserts full equality, so no field of a registered account can be edited
  through this path.

Both were confirmed to **fail against the old code and pass against the new** by stashing only the
four source files and re-running.

### F8 — partially done, and deliberately not the whole plan

Done: `last_name` is now `""` instead of a copy of the name, so the admin UI no longer renders
`"Ravi Ravi"`. Locked by `test_guest_identity_does_not_duplicate_the_name`.

Not done: the plan also said to set `is_guest = False` after self-identification. **That was dropped
on purpose.** `is_guest` gates the identity validation in `start_support` (`chat_service.py:41`) and
the identity-setting branch in `mutate_start_conversation` (`mutations/chat.py:52`), and the existing
test at `test_public_chat.py:132` asserts it stays `True` after a guest supplies name + email. Flipping
it would silently stop validating identity on every later call for that user. Changing that is a
product decision about what `is_guest` means, not a hygiene fix, so it is left for an explicit call.

### F9 — done, implemented differently from the plan

The plan said "if there is no `guest_token` cookie, do not fabricate a user". Implemented more
precisely, because the real trigger is narrower than a missing cookie: middleware sets
`guest_token` on the first public response, so a brand-new browser *has* a token but no cart and no
user. Under the old code any read query then minted a `users` row.

* `context.py` — extracted `_resolve_guest_user(ctx)`, which resolves an identity or returns `None`
  and never writes. `require_user_or_guest` gained `create_missing: bool = True` and keeps the write
  path for mutations. Added `optional_user_or_guest(ctx)` as the read-only, never-writing variant.
* `queries/chat.py` — `conversations` and `messages` use `optional_user_or_guest` and return an empty
  page when there is no identity; `activeConversation` returns `None`. `conversation(id)` uses
  `optional_user_or_guest` too and raises `PermissionDeniedError("Authentication required")` when
  there is no identity, rather than minting a user only to fail the participant check.

One thing that first attempt got wrong, kept here because it is a trap: `conversation(id)` was
briefly switched to `require_user` (authenticated only). That broke guests reading their own history
— including the "read the ended conversation after New Chat" test. A guest holding a valid
`guest_token` is a legitimate caller and must be allowed to read their own thread; only a caller with
*no* resolvable identity is refused.

`require_user_or_guest` also had to keep adopting an existing `Cart` row rather than inserting a
second one. `cart.guest_token_hash` is `unique=True` (`models/cart.py:23`), so if a row for the token
ever exists without a `user_id`, the naive insert raises `IntegrityError`. No current code path
creates that state, so no test covers it, but the adopt-or-create branch was restored as cheap
insurance against a latent crash.

Locked by `test_read_only_queries_do_not_mint_a_guest_user`, which asserts the user count is unchanged
across `conversations` / `activeConversation` / `conversation`, then that the first *write* mints
exactly one guest and subsequent reads reuse it.

### Not yet done

F4, F5, F6 (realtime — the WebSocket is still broken with
`HTTPBearer.__call__() missing 1 required positional argument: 'request'`), F10–F13 (timestamps and
ordering), F14–F16 (unread), F17–F20 (validation, errors, `Origin` check).
