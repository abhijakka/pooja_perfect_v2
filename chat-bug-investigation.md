# Chat Bug Investigation

**Status:** Investigation complete. Fix plan lives in `chat-bug-fix.md`.
**Date:** 2026-09-26
**Scope:** Public customer chat ↔ backend ↔ admin customer chat, end to end.

**Stack verified from code and from the installed environment (not assumed):**

| Layer | Actual technology |
|---|---|
| Backend framework | FastAPI `0.141.1` |
| Backend API | **GraphQL only** (Strawberry `0.327.7`). There is **no REST route for chat.** |
| Backend ORM | SQLAlchemy `2.0.52` declarative `Mapped[]` |
| Realtime | GraphQL subscriptions over `graphql-transport-ws` (Strawberry `GraphQLRouter`). No socket.io, no `graphql-ws` npm package. |
| Pub/sub | In-process `SimplePubSub` singleton (`public/api/graphql/subscriptions/pubsub.py:40`) |
| Frontend | Next.js `16.3.2` App Router (Turbopack), React `19.2.8`, Redux Toolkit `2.12`, `swr` (unused in chat) |
| Frontend HTTP | Native `fetch` via `services/api/client.ts`. No axios. |
| Frontend WS | **Hand-rolled** `graphql-transport-ws` client over native `WebSocket` (`services/websocket/chat.socket.ts`) |
| Auth | httpOnly cookies (`access_token`, `refresh_token`, `guest_token`) + PyJWT HS256. No token in JS storage. |
| Date library | **None.** No date-fns / dayjs / moment. All formatting is hand-rolled. |

---

## 0. Method and baseline

Every claim below was either read out of the repository or **measured**. Measurements used
`fastapi.testclient.TestClient` against the real `app.main:app` with a throwaway SQLite file DB
(`Base.metadata.create_all`), plus `node` for date parsing, `pytest`, `tsc`, `jest` and
`next build` for the frontend.

Baseline recorded **before** any change, so post-change numbers are comparable:

```
backend   .venv\Scripts\python.exe -m pytest src/app/tests/test_public_chat.py src/app/tests/test_admin_chat.py -q
          -> 17 passed

frontend  npx tsc --noEmit   -> 6 errors, ALL in chat files
frontend  npx jest           -> 3 failed suites / 144 passed / 147 total
                                 (SupportChat, chat/page, signup/page)
frontend  npx next build     -> "Compiled successfully" then "Failed to type check"
```

Important nuance on the `next build` result, because it is easy to get backwards:

* Turbopack/webpack **resolve `.tsx` before `.ts`**
  (`node_modules/next/dist/build/webpack-config.js:582-590` →
  `extensions: ['.js','.mjs','.tsx','.ts','.jsx','.json','.wasm']`).
  So the **real** `context/ChatContext/index.tsx` *is* what ships.
* `tsc` (`moduleResolution: "bundler"`) and `next/jest` resolve `.ts` **first**, so they pick up the
  dead stub `context/ChatContext/index.ts`.

Measured proof of the divergence:

```ts
// frontend/__resolution_probe.test.ts (temporary, since removed)
import * as ChatModule from "./context/ChatContext";
console.log(Object.keys(ChatModule));   // -> ["ChatContext"]   <-- the 32-byte stub
```

**Conclusion: the chat is not dead at runtime, but it cannot be type-checked, cannot be built for
production, and cannot be tested by Jest.** See root cause **C5**.

---

## Current Architecture

The real path, with the actual project implementation at every hop. Nothing here is invented.

```text
PUBLIC CHAT UI
  app/(public)/chat/page.tsx            -> components/chat/ChatApplication.tsx   (full page, /chat)
  components/chat/SupportChat.tsx       (floating widget, mounted in app/providers.tsx:130
                                         on EVERY route; self-hides on /admin and /chat
                                         via SupportChat.tsx:66-68)
      |  useChat()  (hooks/useChat.ts -> context/ChatContext/index.tsx:438)
      v
CHAT SERVICE / STATE
  context/ChatContext/index.tsx         the engine: identity steps, bootstrap, WS, polling
  store/slices/chatSlice.ts             messages[], conversationId, guestStep, unread(boolean)
  localStorage: pp-chat-conversation    conversation id mirror
               pp-chat-guest-name
               pp-chat-guest-email
      |
      +--> HTTP  services/api/chat.api.ts -> services/api/client.ts graphqlRequest()
      |
      +--> WS    services/websocket/chat.socket.ts (graphql-transport-ws, "graphql-transport-ws" subprotocol)
                |
                v
BACKEND
  main.py:37-42   GraphQLRouter(public_schema, context_getter=get_public_context)  prefix "/graphql"
      |
      v
AUTH / GUEST IDENTIFICATION
  public/context.py:29-42   get_public_context  (bearer -> access_token cookie -> guest_token cookie)
  public/context.py:52-80   require_user_or_guest
        authenticated -> ctx.user
        anonymous     -> guest_token cookie -> SHA-256 -> carts.guest_token_hash -> carts.user_id
                        -> users.id   (else CREATE a users row with is_guest=True)
      |
      v
CONVERSATION
  models/conversation.py            conversations
  models/conversation_participant.py conversation_participants  (uq: conversation_id+user_id)
  repositories/chat_repository.py:87-124  get_or_create_support_conversation / active_support_conversation
        lookup key = users.id, filtered subject=="support" AND status=="active"
      |
      v
MESSAGE
  models/chat_message.py            chat_messages  (sender_id, content, is_read, read_at, created_at)
      |
      v
DATABASE  (SQLite in dev/test, Postgres per config default)
      |
      v
ADMIN CHAT
  app/admin/chat/page.tsx -> app/admin/components/AdminChatPage.tsx  (447 lines, local state only)
  services/api/admin.api.ts:111-116 -> POST /admin/graphql
      |
      v
ADMIN REPLY
  admin/mutations/chat.py sendMessage -> admin/repositories/chat_repository.py:171-185
      |
      v
BACKEND -> pubsub.publish("chat:{id}")  -> (subscription)  -> PUBLIC CHAT
```

### Transport facts

* **All chat traffic is GraphQL.** Public → `POST /graphql`. Admin → `POST /admin/graphql`.
* Subscriptions are `chatMessage(conversationId: UUID!)` on both schemas.
* Topic / "room" is `chat:{conversation_id}` (`pubsub.py:43-44`). One topic per conversation.
  There is **no admin-wide "all conversations" topic**, so an admin only receives live messages
  for the conversation they currently have open.
* The frontend runs **two independent mechanisms at once**: a WS subscription *and* an 8 s poll
  (`ChatContext/index.tsx:274-282` and `:284-301`). The admin runs a WS subscription *and* a 10 s
  poll of the conversation list (`AdminChatPage.tsx:127-148`). This dual mechanism is intentional
  in the code ("realtime remains primary") and is why duplicate suppression matters (§Duplicate
  Message Investigation).

---

## Public Guest Flow

Measured, not inferred.

1. `POST /graphql startConversation(name, email)` → `public/api/graphql/mutations/chat.py:38-62`.
2. No auth is required. `require_user_or_guest` (`public/context.py:52`) never rejects an
   anonymous caller; it mints a real `users` row with `is_guest=True`,
   `email = guest-<24hex>@guest.local` (`context.py:63-79`).
3. `set_guest_identity` (`public/services/chat_service.py:51-85`) overwrites that row's
   `first_name`, `last_name`, `email` with what the guest typed. Validation is regex only
   (`chat_service.py:19`, `:148-149`).
4. `get_or_create_support_conversation` reuses the caller's existing `active` support
   conversation, or creates one and adds a `customer` participant row.

Measured result — no duplicate conversations on repeated open:

```
startConversation x3, same cookie jar ->
  ['db3ed992-…', 'db3ed992-…', 'db3ed992-…']   unique: 1   OK
```

Measured guest → admin → guest round trip over HTTP:

```
startConversation(name:"Ravi", email:"ravi@p.com") -> 200 status=active
sendChatMessage "Msg 1"                            -> 200 mine=true
admin conversations                                -> customerName="Ravi Ravi" unreadCount=1
admin sendMessage "Hello, how can I help?"         -> 200
guest messages                                     -> mine=false, content="Hello, how can I help?"
```

## Authenticated Customer Flow

* Auth is `require_user(ctx)` / `ctx.user` populated by `get_optional_current_user`
  (`public/dependencies.py:28-49`), which reads `Authorization: Bearer` then falls back to the
  `access_token` cookie (`dependencies/auth.py:35-42`).
* `mutate_start_conversation` **ignores** any `name`/`email` an authenticated user passes,
  because the identity branch is guarded by `if user.is_guest and (name or email)`
  (`mutations/chat.py:49`). An authenticated customer is therefore never treated as a guest for
  identity purposes. That part is correct.
* The frontend also skips the guest step machine for logged-in users:
  `sessionIdentity()` returns `undefined` when `isAuthenticated` (`ChatContext/index.tsx:122-128`),
  and logging in wipes all three localStorage keys (`ChatContext/index.tsx:246-248`).

The problems are in §Root Causes (C4 takeover, and §Authentication for the logout/transition gaps).

## Admin Flow

`app/admin/layout.tsx:11-14` is the only frontend guard (redirects non-admins to `/`). Real
authorization is server side: `main.py:47` → `admin/context.py:28-36` → `require_admin`
(`dependencies/auth.py:72-78`). Measured:

```
POST /admin/graphql  no token       -> 401 {"detail":"Invalid or malformed token"}
POST /admin/graphql  customer token -> 403 {"detail":"You do not have permission to perform this action"}
POST /admin/graphql  admin token    -> 200 data
```

Admins are **never** inserted as participants (`admin/repositories/chat_repository.py:171-185`
only inserts a `ChatMessage`). Ownership is derived solely from `conversation_participants`, so
`is_participant` is never true for an admin and an admin cannot see their own replies through the
public API.

## Conversation Creation

Creation is **lazy**, not on widget open. Chain in `establishConversation`
(`ChatContext/index.tsx:161-234`):

```text
not authenticated + no stored identity -> setGuestStep("name")   (NO conversation created)
forceNew=true                          -> startConversation(..., forceNew=true)  (ends old, creates new)
localStorage has pp-chat-conversation  -> conversation(id)        (reuse)
else                                   -> activeConversation()    (reuse)
else                                   -> startConversation(...)  (create)
```

Backend side, `get_or_create_support_conversation`
(`public/repositories/chat_repository.py:87-111`) means **opening/closing the chat does not create
duplicates** — measured, see §Public Guest Flow. `forceNew=true` *ends* the previous conversation
(line 108) rather than deleting it, so the transcript is preserved.

## Message Flow

```text
Customer send:
  ChatContext.send (:310-333) -> chatApi.sendMessage -> POST /graphql sendChatMessage
    -> mutations/chat.py:74-91 -> chat_service.send_message (:118-126)
    -> guards: participant, status==active, content non-blank
    -> repo.send_message (INSERT) -> commit -> db.refresh
    -> pubsub.publish(chat:{id}, message)   (mutations/chat.py:88-90)
    -> returns ChatMessageType with `mine=true`

Admin reply:
  AdminChatPage.sendMessage (:172-198) [optimistic local row first]
    -> adminApi.sendChatMessage -> POST /admin/graphql sendMessage
    -> admin/mutations/chat.py:42-58 -> admin repo.send_message (INSERT, sender_id = admin.id)
    -> commit -> refresh -> pubsub.publish(chat:{id}, message)
    -> returns ChatMessageType (no `mine` field on the admin type)
```

Both directions work **over HTTP**. Both are broken over WebSocket (§WebSocket / API Flow).

## WebSocket / API Flow

**This is the single most damaging finding in the whole subsystem.**

Measured directly against the real app:

```python
TestClient(app).websocket_connect("/graphql",       subprotocols=["graphql-transport-ws"])
  -> TypeError: HTTPBearer.__call__() missing 1 required positional argument: 'request'
TestClient(app).websocket_connect("/admin/graphql", subprotocols=["graphql-transport-ws"])
  -> TypeError: HTTPBearer.__call__() missing 1 required positional argument: 'request'
```

**Both WebSocket endpoints fail 100% of the time, for every user, always.** Realtime delivery does
not exist in this application. The frontend never knows: `chat.socket.ts` retries 4 times with
linear backoff (`RECONNECT_DELAY_MS=2500`, `MAX_RECONNECTS=4`), gives up silently, and the only
thing the user ever sees is the 8 s poll.

Root cause chain:

1. `dependencies/auth.py:30` and `public/dependencies.py:25` both declare
   `bearer_scheme = HTTPBearer(auto_error=False)`.
2. That scheme is injected with `Depends(bearer_scheme)` into
   `get_optional_current_user` / `get_current_user`.
3. FastAPI classifies `HTTPBearer.__call__(self, request: Request)`'s `request` as
   `dependant.request_param_name`
   (`fastapi/dependencies/utils.py:353-355`).
4. At solve time FastAPI injects it **only for HTTP scopes**:
   ```python
   if dependant.request_param_name and isinstance(request, Request):
       values[dependant.request_param_name] = request
   elif dependant.websocket_param_name and isinstance(request, WebSocket):
       values[dependant.websocket_param_name] = request
   ```
   (`fastapi/dependencies/utils.py:711-714`). In a WebSocket scope the object is a `WebSocket`,
   so `request` is never supplied → `TypeError`.
5. `strawberry/fastapi/router.py:248-254` resolves the context getter with
   `@self.websocket(path)` + `Depends(self.context_getter)`, so the whole auth chain runs during
   the WS upgrade and raises.

A **second, latent** blocker sits behind the first and will surface the moment the first is fixed:
`get_public_context` declares `response: Response` (`public/context.py:33`) and calls
`response.set_cookie(...)` at line 41. FastAPI supplies no `Response` object in a WebSocket scope,
so that line would raise `AttributeError` on `None`. A guest also has no way to obtain a
`guest_token` over WS at all, because the cookie is the only place it is delivered.

Also relevant: there is **no `Origin` validation** on the WS upgrade.

The frontend WS client itself is well built and does not need replacing — it implements
`connection_init`/`connection_ack`, `subscribe`/`next`/`complete`, `ping`/`pong` keep-alive at
30 s, `resubscribeAll()` on reconnect, exponential-ish backoff, and per-subscription
last-id dedupe (`chat.socket.ts:55-213`). The architecture should be kept and repaired, **not**
replaced with polling.

## Authentication

| Concern | Reality |
|---|---|
| Token location | httpOnly cookie only. `services/api/client.ts:122-131` sends `credentials: "include"`. The `token` argument of `graphqlRequest` exists but **no chat call passes it**. |
| Session restore | `app/providers.tsx:43-73` calls `GET /auth/me` on every load. |
| Expiry | `app/providers.tsx:75-83` polls `accessTokenExpiresAt` every 1 s and ends the session. |
| 401 handling | `client.ts:32-54` `notifyUnauthorized()` → `providers.tsx:27-40` `endSession()` → `logout()` + redirect to `/`. |
| Admin guard | `app/admin/layout.tsx:11-14`, role from `/auth/me`. |
| Anonymous identity | `guest_token` cookie → `carts.guest_token_hash` → `carts.user_id` → `users.id`. |

Guest identity is keyed off the **cart** table, which is the only `guest_token_hash` store in the
schema. Measured: a cookieless client gets `activeConversation: null` **and a brand new guest user
row minted on every single call** (`context.py:63-79`). Any non-browser consumer of the API
therefore fragments identity per request.

## Authorization

* Access decisions always use the **server-derived** `user.id`. The client never supplies a user id.
  Verified: an authenticated customer cannot read or write another customer's conversation.
* `is_participant` guards `conversation(id)`, `messages`, `sendChatMessage`, `endConversation` and
  the public subscription (`public/services/chat_service.py:87-126`,
  `public/api/graphql/subscriptions/chat.py:36-37`).

Measured isolation (guest B against guest A's conversation):

```
conversation(id=A)          -> "You are not part of this conversation"
sendChatMessage(A)          -> "You are not part of this conversation"
```

Admin endpoints require `require_admin` (401 no token / 403 non-admin, measured above).
`POST /graphql` requires nothing, by design — public chat is meant to work for guests.

**The authorization hole is not in conversation access, it is in identity claiming — see C4.**

## Customer Identification

Resolution order for "who is calling", all server-side
(`public/context.py:52-80` → `public/dependencies.py:28-49` → `dependencies/auth.py:35-42`):

```text
Authorization: Bearer <jwt>   -> decode -> users.id
access_token cookie            -> decode -> users.id
guest_token cookie             -> carts.guest_token_hash -> carts.user_id -> users.id
neither                       -> CREATE users(is_guest=True, email=guest-<hex>@guest.local)
```

On the admin side, `customerId` / `customerName` / `customerEmail` are resolved by taking the
**first** participant row with `participant_role == "customer"`
(`admin/repositories/chat_repository.py:78-88`, `setdefault`). Consequences:

* Measured: a guest named "Ravi" appears as **`"Ravi Ravi"`** in the admin UI, because
  `set_guest_identity` does `user.last_name = name` (`chat_service.py:81`) and the view formats
  `f"{first_name} {last_name}"` (`admin/repositories/chat_repository.py:122`).
* If a conversation ever has more than one `customer` participant (which C4 creates), the resolved
  identity is whichever row the database returns first — non-deterministic.
* `is_guest` is never reset to `False` after a guest supplies a real name/email, so a guest who
  later becomes a known lead is permanently flagged as a guest.

## Timestamp Handling

**Every timestamp in both UIs is wrong by the viewer's UTC offset. This is measured, not suspected.**

Generation — `models/base.py:18-27`:

```python
created_at = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
```

`func.now()` on SQLite becomes `DEFAULT CURRENT_TIMESTAMP`, which is **UTC with 1-second
resolution and no offset**. Strawberry serializes the naive `datetime` to plain ISO-8601.
Measured API output:

```json
"createdAt": "2026-09-25T19:07:06"      <-- UTC, but no "Z" and no "+00:00"
```

Consumption — `context/ChatContext/index.tsx:63-72` and `AdminChatPage.tsx:21-39` both do a bare
`new Date(value)`. Per ECMA-262, a date-time string **without** an offset is interpreted as
**local time**, not UTC. Measured on this machine (IST, UTC+05:30):

```text
new Date("2026-09-25T19:07:06")   -> Fri Sep 25 2026 19:07:06 GMT+0530   <-- WRONG, treated as local
new Date("2026-09-25T19:07:06Z")  -> Sat Sep 26 2026 00:37:06 GMT+0530   <-- CORRECT
```

So a message stored at **00:37 IST** is displayed to an IST user as **19:07 the previous day** —
a **5 h 30 min error, and often the wrong calendar day**. The same defect hits the admin UI
(`clockTime`) and the conversation list (`timeAgo`). `DateTime(timezone=True)` is declared on the
column but SQLite cannot honour it, which is exactly why the offset is lost.

There is a third, inconsistent time source: `read_at` is Python-generated with real tzinfo
(`admin/repositories/chat_repository.py:206`, `datetime.now(UTC)`), which is why live `read_at`
values carry microseconds while `created_at` carries only seconds. `read_at` is not exposed through
GraphQL at all.

## Timezone Handling

Summary of the six timezones the brief asks about, as they actually are:

| Layer | Actual state |
|---|---|
| Database | naive UTC, **1-second** resolution (`CURRENT_TIMESTAMP`) |
| Backend process | never sets `TZ`; only `read_at` uses `datetime.now(UTC)` |
| API format | ISO-8601 **without** offset: `"2026-09-25T19:07:06"` |
| Frontend parse | `new Date(str)` → **local time** (wrong) |
| Customer timezone | whatever the browser is |
| Admin timezone | whatever the browser is |

No `timeZone` option, no `timeZone: "UTC"`, no offset appending anywhere in the repo.

## Message Ordering

**No sort exists anywhere in the chat subsystem.** A repo-wide search for `.sort(` in `.ts`/`.tsx`
returns exactly one hit, in `products/ProductsPage.tsx`, unrelated to chat.

Backend ordering is the authoritative part and it is unsound:

```python
# public/repositories/chat_repository.py:162  and  admin/repositories/chat_repository.py:165
.order_by(ChatMessage.created_at.desc())
```

`created_at` has **1-second** resolution and there is **no tie-breaker**. Measured — three messages
sent back to back:

```
2026-09-25T19:11:04  Msg 3
2026-09-25T19:11:04  Msg 2
2026-09-25T19:11:04  Msg 1
```

All three tie. SQLite is free to return tied rows in any order; what you observe is an artefact of
storage layout, not a guarantee. Consequences:

* Intra-second ordering is **non-deterministic**.
* `OFFSET`/`LIMIT` pagination over a **non-unique** sort key can **duplicate or silently drop rows
  across page boundaries** — messages can vanish from history.
* `ChatMessage.id` is a random `uuid4` (`models/base.py:15`), so it cannot be used as a
  chronological tie-breaker.

Frontend ordering is purely positional, and appends are never re-sorted:

```ts
// store/slices/chatSlice.ts:83-88
appendMessage: (state, action) => {
  const incoming = action.payload;
  if (state.messages.some((m) => m.id === incoming.id)) return;   // dedupe by id
  state.messages.push(incoming);                                   // always tail
  if (!state.open) state.unread = true;
},
```

So a message that arrives late (poll, then WS, then a second poll) is appended **after** messages
that are newer, and stays mis-ordered forever. `AdminChatPage.tsx:133-137` has the identical shape.

## Read / Unread

Implemented, but **admin-only and global rather than per-recipient**.

* Storage: `chat_messages.is_read BOOLEAN NOT NULL default false`, `read_at DATETIME NULL`
  (`models/chat_message.py:37-38`).
* Only mutator: `mark_read` (`admin/repositories/chat_repository.py:195-210`), reachable solely from
  the admin `markRead` mutation.
* Unread count: `admin/repositories/chat_repository.py:101-113` — counts `is_read = false` rows whose
  `sender_id != reader_id`.
* **There is no public `markRead` mutation.** The public schema exposes only the read-only `isRead`
  field. `public/repositories/chat_repository.py:140-147` has an `unread_count` helper that **no
  resolver or service ever calls** — dead code.

Measured consequence:

```
markRead                -> 4
unreadCount after       -> 0
admin sends a reply
unreadCount after reply -> 0        <-- customer gets NO unread signal for the reply
```

`is_read` is a single boolean per message, so "read by the admin" and "read by the customer" are
indistinguishable. The customer has no unread concept at all.

## Reconnection

Client-side reconnect logic exists and is reasonable (`chat.socket.ts:112-174`: `MAX_RECONNECS=4`,
backoff `2500 * attempt`, `resubscribeAll()` on `connection_ack`, 30 s `ping` keep-alive,
`dispose()`). It cannot be exercised because the socket never opens in the first place.

Two further defects:

* `disposeChatSocket()` / `disposeAdminChatSocket()` (`chat.socket.ts:249-255`) are exported but
  **never called from application code**. `SocketManager` is only instantiated in its own test.
  The module-level singletons `chatSocket` / `adminChatSocket` live for the whole page lifetime.
* `reconnectAttempts` resets to `0` on `connection_ack` (`:88`). With a hard cap of 4 attempts, a
  server restart longer than ~25 s leaves the client permanently unsubscribed until a page reload.
  There is no give-up notification, so the UI silently degrades to polling.

## Navigation Persistence

* `ChatProvider` lives in `app/providers.tsx:125-132`, above the router, so it survives client-side
  navigation. `<SupportChat />` is mounted there too, and self-hides on `/chat` and `/admin/*`
  (`SupportChat.tsx:66-68`).
* Conversation id is mirrored in `localStorage["pp-chat-conversation"]` and in Redux
  (`ChatContext:176,185,216`; `chatSlice.ts:12`). Redux persistence in `store/index.ts:24-33`
  writes **only** wishlist and cart, so chat relies on localStorage plus the `guest_token` cookie.
* Returning-guest restore is handled at `ChatContext:254-272`.
* The store persistence write in `store/index.ts` and the `cartToken`/guest token are the only
  cross-route carriers; there is no `middleware.ts`.

Measured risk: on navigation, `establishConversation` re-runs and re-validates the stored id via
`chatApi.conversation(storedId)`. If that call fails the id is cleared and the flow falls back to
`activeConversation()`, which is server-authoritative — so history survives. The 5-page × 50 = 250
message cap (§Message Ordering / M5) is the real history-loss ceiling.

## Duplicate Message Investigation

Enumerated every listener registration in the chat surface:

| File:line | Kind |
|---|---|
| `ChatContext:236-240` | `useEffect` — boot |
| `ChatContext:242-252` | `useEffect` — authenticated session |
| `ChatContext:254-272` | `useEffect` — returning-guest restore |
| `ChatContext:274-282` | `useEffect` — **WS subscribe** |
| `ChatContext:284-301` | `useEffect` — **8 s `setInterval` poll** |
| `SupportChat:44-50` | `useEffect` + `window.addEventListener("keydown")`, removed in cleanup |
| `ChatApplication:35-45` | three `useEffect` (open, scroll, focus) |
| `AdminChatPage:100-119` | `useEffect` — initial list fetch |
| `AdminChatPage:121-125` | `useEffect` — load messages + markRead |
| `AdminChatPage:127-148` | `useEffect` — **WS subscribe + 10 s `setInterval`** |
| `chat.socket.ts:72,76,100,107` | four `addEventListener` per physical socket, in `open()` |

Findings:

* Every effect returns a correct cleanup. **No duplicate listeners accumulate across route changes.**
* Dedupe is present in three places and works: `appendMessage` id check (`chatSlice.ts:85`),
  WS `lastSeenId` check (`chat.socket.ts:196-199`), admin `current.some(...)` check
  (`AdminChatPage.tsx:134`). Because the WS and the poll both deliver the same message, this dedupe
  is load-bearing — it is why there are no visible duplicates today.
* `ChatContext:254-272` has `chat.guestStep` in its own dependency array while also dispatching
  `setGuestStep`, i.e. a self-invalidating dep. It is guarded by the early-return at `:255-263`
  so it settles, but it is fragile.
* `AdminChatPage:127-148` depends on `refreshConversations`, whose own deps include `selectedId`
  (`AdminChatPage:83`). Every selection change therefore tears down and rebuilds the socket and the
  interval. Wasteful, not incorrect.
* The admin's 10 s poll refreshes only the **conversation list**, never messages — so an admin
  relies entirely on the (dead) socket to see a new message body.

**Verdict: no duplicate-message defect reproduced.** The risk is latent, not active.

## Duplicate Conversation Investigation

Measured directly (see §Public Guest Flow): three consecutive `startConversation` calls on the same
session return **one** id. `get_or_create_support_conversation` correctly reuses the active
conversation.

Two real caveats:

* `ChatContext:242-252` clears `pp-chat-conversation` whenever `isAuthenticated` flips, and
  `bootRequested.current` is a ref that is set in **two** effects (`:238` and `:249`). If the auth
  bootstrap and the conversation bootstrap interleave, a second `establishConversation` can run
  after the clear. It is currently saved by the server-side get-or-create, not by the client.
* `forceNew=true` ("New Chat") **ends** the old conversation and creates a new one
  (`chat_repository.py:108-110`). That is intended, but it means "New Chat" is destructive to the
  active transcript from the customer's point of view.

**Verdict: no duplicate-conversation defect reproduced on the server. The client bootstrap is
order-fragile but currently self-correcting.**

---

## Root Causes

Ordered by severity. Every entry is measured.

### C1 — CRITICAL: both WebSocket endpoints fail 100% of the time

`TypeError: HTTPBearer.__call__() missing 1 required positional argument: 'request'` on
`/graphql` **and** `/admin/graphql`. **There is no realtime delivery in this application at all.**
Root cause: `HTTPBearer` declared as a `Depends` in the GraphQL context chain
(`dependencies/auth.py:30`, `public/dependencies.py:25`); FastAPI only injects the `request`
argument for HTTP scopes (`fastapi/dependencies/utils.py:711-714`), and Strawberry resolves the
context getter during the WS upgrade (`strawberry/fastapi/router.py:248-254`).
Verified by direct `TestClient.websocket_connect` against `app.main:app`.

### C2 — CRITICAL (latent, behind C1): WS context also needs a `Response`

`public/context.py:33` takes `response: Response` and line 41 calls `response.set_cookie(...)`.
No `Response` exists in a WS scope. Fixing C1 alone converts the `TypeError` into an
`AttributeError`. A guest also cannot obtain a `guest_token` over WS at all, because the cookie is
the sole delivery channel for it.

### C3 — CRITICAL: every timestamp in both UIs is wrong by the viewer's UTC offset

Backend emits naive UTC with no offset (`"2026-09-25T19:07:06"`); both UIs call `new Date(str)`,
which per ECMA-262 treats a zoneless string as **local**. Measured: a 5 h 30 min error and the
wrong calendar day in IST. `models/base.py:19-21` + `ChatContext/index.tsx:63-72` +
`AdminChatPage.tsx:21-39`.

### C4 — CRITICAL SECURITY: an anonymous visitor can take over a registered account

Reproduced end to end. `set_guest_identity` (`public/services/chat_service.py:65-78`) looks the
typed email up with `UserRepository.get_by_email`, and if it exists it **adds the registered user
as a participant on the visitor's own conversation** (`:74-75`) and **returns the registered user**
so `mutate_start_conversation` sets `force_new=True` and creates a conversation **owned by the
registered account** (`mutations/chat.py:53-61`).

Measured:

```text
1. attacker (no cookie, no auth) startConversation(name:"Attacker", email:"victim_…@registered.com")
     -> 200, conversation e597f7a8-… created
2. the REAL registered customer authenticates and lists conversations
     -> {"items":[{"id":"e597f7a8-…","status":"active"}], "total":1}
```

The registered customer's account now owns and can read the anonymous visitor's conversation. There
is no email verification, no OTP, no rate limit, and no admin role requirement on this path.
`mutations/chat.py:58-61` compounds it by also adding the *original* guest as a participant, which
is what creates the multi-`customer` conversation that then makes admin identity resolution
non-deterministic.

### C5 — CRITICAL: the chat cannot be type-checked, built, or tested

`next build` → `Compiled successfully` then **`Failed to type check`**. Six of the errors are chat:

```
app/providers.tsx(16,10)            TS2305  Module '"../context/ChatContext"' has no exported member 'ChatProvider'
hooks/useChat.ts(1,10)              TS2305  Module '"../context/ChatContext"' has no exported member 'useChat'
app/admin/components/AdminChatPage.tsx(133,17) TS2345  ChatMessage | AdminChatMessage not assignable
components/chat/SupportChat.tsx(145,21)      TS7006  implicit any
components/chat/ChatApplication.tsx(124,20)  TS7006  implicit any
services/websocket/chat.socket.ts(134,3)    TS2322  number not assignable to Timeout
```

The first two are caused by a **32-byte dead stub** `context/ChatContext/index.ts`
(`export const ChatContext = {};`) sitting next to the real 446-line `index.tsx`. Next's bundler
resolves `.tsx` first so runtime is fine, but `tsc` (`moduleResolution: "bundler"`) and `next/jest`
resolve `.ts` first, so they load the stub. Measured: `Object.keys(await import("./context/ChatContext"))`
→ `["ChatContext"]`. Consequence: **Jest cannot test the real chat context at all** — `useChat()`
returns `undefined` unless a test mocks it, which is exactly why all three failing chat suites
have to mock `../../hooks/useChat`.

### H1 — HIGH: message ordering has no tie-breaker and the timestamp has 1-second resolution

`ORDER BY created_at DESC` with no secondary key (`public/repositories/chat_repository.py:162`,
`admin/repositories/chat_repository.py:165`) over a `CURRENT_TIMESTAMP` column. Measured: three
messages in the same second all tie. Intra-second order is non-deterministic, and `OFFSET`
pagination over a non-unique sort key can duplicate or drop rows across pages.
`ChatMessage.id` is `uuid4`, so it cannot break the tie.

### H2 — HIGH: frontend never re-sorts, so late arrivals stay mis-ordered

`chatSlice.ts:83-88` and `AdminChatPage.tsx:133-137` both append at the tail with id-dedupe only.
A message delivered by poll after a newer one was delivered by socket stays permanently in the
wrong position.

### H3 — HIGH: delivery is gated on the panel being open, which also kills the unread badge

`ChatContext:275` and `:285` both `if (!chat.conversationId || chat.ended || !chat.open) return;`.
While the widget is closed there is **no socket and no poll**, so nothing is fetched and
`appendMessage` never runs. But `appendMessage` only sets `unread` when `!state.open`
(`chatSlice.ts:87`) — a state that can never be reached. **The unread badge is unreachable
dead code.** The badge itself is additionally hard-coded to the literal `1`
(`SupportChat.tsx:98`).

### H4 — HIGH: the customer has no unread state at all

No public `markRead` mutation exists; `public/repositories/chat_repository.py:140-147` is dead code.
Measured: after an admin reply, `unreadCount` stays `0` and the customer has no signal that a reply
arrived. `is_read` is one global boolean (`models/chat_message.py:37`) so per-recipient read state
is not representable.

### M1 — MEDIUM: `conversations.updated_at` never advances when a message is sent

`send_message` only INSERTs into `chat_messages`; nothing UPDATEs `conversations`, and
`onupdate=func.now()` only fires on UPDATE (`models/base.py:22-26`). Measured:

```
updatedAt before 3 sends: 2026-09-25T19:11:04
updatedAt after  3 sends: 2026-09-25T19:11:04    <-- unchanged
```

Admin conversation list orders by `updated_at DESC` (`admin/repositories/chat_repository.py:54`),
so a conversation with brand-new activity does not bubble to the top.

### M2 — MEDIUM: `is_read` is global, not per participant

Consequence of H4's storage choice; `mark_read` excludes only `sender_id != reader_id`
(`admin/repositories/chat_repository.py:202`).

### M3 — MEDIUM: no message length cap

Measured: a 20,000-character message is accepted. `schemas/chat/message.py:12` declares
`max_length=10000` but that module is **dead code** — `app.schemas.chat` is imported nowhere.

### M4 — MEDIUM: public GraphQL leaks internal exception text, admin does not

`admin/api/graphql/schema.py:331-355` registers `_AppErrorExtension`, so admin errors carry
`extensions.code`. The public schema (`public/api/graphql/schema.py:224-228`) registers none, so
every expected business error escapes as a raw exception: the client receives the `detail` string
but the server logs a full Python traceback. Measured, HTTP 200 in both cases:

```text
admin: {"message":"This conversation has ended and cannot receive replies","extensions":{"code":422}}
public:{"message":"This conversation has ended — you can no longer send messages"}   (+ traceback logged)
```

Pagination inputs leak pydantic internals on both schemas:

```text
page: 0        -> "1 validation error for PaginationInput\npage\n  Input should be greater than or equal to 1 ..."
pageSize: 99999-> "... page_size Input should be less than or equal to 100 ..."
```

### M5 — MEDIUM: history is silently truncated

Public: hard cap of 5 pages × 50 = **250 messages**, then it stops
(`ChatContext:134-149`). Admin: **page 1 only, pageSize 100, no pagination at all**
(`AdminChatPage:89`). No "load older" affordance on either side.

### L1 — LOW: admin shows guests as `"Ravi Ravi"`

`chat_service.py:81` sets `last_name = name`; the view formats `f"{first_name} {last_name}"`
(`admin/repositories/chat_repository.py:122`). Measured: `customerName: "Ravi Ravi"`,
`customerName: "Priya Priya"`.

### L2 — LOW: `is_guest` is never cleared

After a guest supplies a real name/email the row keeps `is_guest=True`
(`chat_service.py:80-83`), so the guest is permanently classified as a guest.

### L3 — LOW: `SupportChat.test.tsx` is out of sync with the component

The test does `getByLabelText("Your name")` (`SupportChat.test.tsx:75`) but the component's
`aria-label` is `"Enter your name"` (`SupportChat.tsx:191`). Measured failure:
`TestingLibraryElementError: Unable to find a label with the text of: Your name`.

### L4 — LOW: `chat/page.test.tsx` fails on an unstubbed DOM API

`bodyRef.current?.scrollTo is not a function` (`ChatApplication.tsx:40`). `SupportChat.test.tsx`
stubs `Element.prototype.scrollTo` in `beforeAll`; this suite does not.

### L5 — LOW: admin `unreadCount` chip does not clear promptly

`selectConversation` calls `markChatRead` but does not update local state
(`AdminChatPage:166-170`); the header total (`:164`) only refreshes on the next 10 s poll or the
next socket message.

### L6 — LOW: hard-coded `"TODAY"` date divider

`SupportChat.tsx:144` and `ChatApplication.tsx:123` print the literal string `"TODAY"` whenever
`messages.length > 0`, regardless of the actual message date. There is no date grouping, so a
message from three days ago is still labelled today.

### L7 — LOW: `chat.socket.ts` timeout type

`window.setTimeout` returns `number` in the DOM but the field is typed `Timeout`
(`chat.socket.ts:134`). One of the six build-blocking type errors.

### L8 — LOW: admin `get_conversation` invents a reader id

`admin/repositories/chat_repository.py:69` passes `reader_id or uuid.uuid4()`, so a single
conversation read reports an `unreadCount` that counts unread messages from a sender who does not
exist.

### L9 — LOW: missing DB indexes on the hot chat paths

From the live schema: no index on `conversation_participants.user_id` (every
`active_support_conversation` subquery full-scans), none on `conversations.status` / `subject` /
`updated_at`, none on `chat_messages.is_read`.

### L10 — LOW: no `Origin` check on the WebSocket upgrade

CORS does not apply to WebSockets and the server does not validate `Origin`, so once C1 is fixed
the WS endpoint should be origin-checked.

### L11 — LOW: non-browser clients fragment guest identity

Measured: a client with no `guest_token` cookie gets `activeConversation: null` **and a new guest
`users` row created on every call** (`context.py:63-79`).

### Out of scope (not chat, but they break the build)

`app/(public)/products/[slug]/page.test.tsx`, `hooks/useCart.test.tsx`,
`services/api/cart.api.test.ts`, `services/api/products.api.test.ts`,
`hooks/useGoogleAuth.ts:73` (`authApi.googleConfig` does not exist) and
`app/(auth)/signup/page.test.tsx` are failing alongside the chat. They belong to the concurrent
`bug-authentication.md` / `bug-view-product.md` work in the working tree. Recorded so the chat
build result can be read correctly; **not touched by this task.**

---

## Recommended Fixes

Full detail, ordering and acceptance criteria are in **`chat-bug-fix.md`**. Summary:

| ID | Fix | Layer |
|---|---|---|
| C1 | Make the auth dependencies ASGI-scope-agnostic (accept `Request | WebSocket`, and read the bearer from headers directly instead of `HTTPBearer`) | backend |
| C2 | Give the public context a WS-safe path: no `Response` dependency, no `set_cookie` in a WS scope | backend |
| C3 | Emit tz-aware UTC timestamps (offset present) and/or normalize on parse; add microsecond precision | backend + frontend |
| C4 | Never transfer conversation ownership to an email that is not verified for the caller; stop adding a registered user as a participant of a stranger's conversation | backend |
| C5 | Delete the dead `context/ChatContext/index.ts` stub; fix the remaining 4 chat type errors | frontend |
| H1 | Deterministic ordering: microsecond `created_at` **and** an explicit tie-breaker in every `ORDER BY` | backend |
| H2 | Re-sort by authoritative key on insert in both UIs | frontend |
| H3 | Decouple delivery from panel visibility; make the unread badge real | frontend |
| H4 | Add a public `markRead` + a customer-visible unread signal (or document the admin-only design explicitly) | backend + frontend |
| M1 | Bump `conversations.updated_at` on every message insert | backend |
| M3 | Enforce the length cap in the service, where it is actually reachable | backend |
| M4 | Register the error extension on the public schema too; convert pydantic errors to clean messages | backend |
| M5 | Paginate admin history; surface the public 250-message cap | backend + frontend |
| L1-L11 | See `chat-bug-fix.md` | mixed |

## Files To Modify

**Backend**

```
src/app/dependencies/auth.py                 C1, C4
src/app/public/dependencies.py               C1
src/app/public/context.py                    C2, C4, L11
src/app/models/base.py                       C3
src/app/models/chat_message.py               C3
src/app/public/repositories/chat_repository.py   C3, H1, M1, M3
src/app/admin/repositories/chat_repository.py    C3, H1, M1
src/app/public/services/chat_service.py      C4, L1, L2, M3
src/app/public/api/graphql/mutations/chat.py C4, M4
src/app/public/api/graphql/schema.py         M4
src/app/public/api/graphql/queries/chat.py   C3, H4
src/app/public/api/graphql/mutations/chat.py C3, H4
src/app/admin/api/graphql/queries/chat.py    C3
src/app/admin/api/graphql/types/chat.py      C3
src/app/public/api/graphql/types/chat.py     C3
src/app/tests/test_public_chat.py            new coverage
src/app/tests/test_admin_chat.py             new coverage
```

**Frontend**

```
context/ChatContext/index.ts                 C3, H2, H3, M5
context/ChatContext/index.ts                 C5 (delete stub)
store/slices/chatSlice.ts                    H2, H3, H4
components/chat/SupportChat.tsx              C3, H3, L6
components/chat/ChatApplication.tsx          C3, L6
app/admin/components/AdminChatPage.tsx       C3, H2, M5, L5
services/api/chat.api.ts                     H4
services/api/admin.api.ts                    M5
types/chat.ts                                C3
lib/utils/date.ts                            C3
```

**Not touched:** any CSS file. `app/globals.css` (`support-chat-*`) and
`app/admin/styles/admin_style.css` (`admin-chat-*`) are explicitly out of scope per the brief.

## End-to-End Test Results

Status of the scenarios in §29-§33 **as measured, before any fix**. "Pass" means the complete
frontend → API → DB → admin → backend → frontend path was exercised.

| # | Scenario | Result | Evidence / blocking defect |
|---|---|---|---|
| 1 | Guest opens chat, submits name + email | **PASS** | `startConversation` 200, identity stored |
| 2 | Guest conversation created exactly once | **PASS** | 3 calls → 1 id |
| 3 | Guest message stored and admin sees it | **PASS** | admin list shows it, `unreadCount: 1` |
| 4 | Admin reply reaches the guest | **PARTIAL** | works over HTTP; **no realtime** (C1) |
| 5 | Admin reply delivered without refresh | **FAIL** | C1 — WS never connects |
| 6 | Customer message without refresh | **FAIL** | C1 |
| 7 | Timestamps correct for guest and admin | **FAIL** | C3 — 5 h 30 m error, measured |
| 8 | Message ordering 1,2,3 | **PARTIAL** | correct only because intra-second ties happen to fall out right; non-deterministic (H1) |
| 9 | Ordering survives pagination | **FAIL** | non-unique sort key + OFFSET (H1) |
| 10 | Refresh preserves conversation + history | **PASS (server)** | backend is the source of truth; UI path not browser-verified |
| 11 | Navigation preserves conversation | **PASS (server)** | get-or-create is server-authoritative |
| 12 | Customer A cannot read B's messages | **PASS** | measured, both directions blocked |
| 13 | Guest cannot access admin endpoints | **PASS** | 401/403 measured |
| 14 | Admin cannot be spoofed by a client id | **PASS** | identity always server-derived |
| 15 | Anonymous cannot claim a registered account | **FAIL — SECURITY** | C4, reproduced |
| 16 | Duplicate messages | **PASS** | id dedupe in 3 layers, no repro |
| 17 | Duplicate conversations on repeated open | **PASS** | measured |
| 18 | Admin sees unread, clears on open | **PARTIAL** | backend works; chip does not clear until next poll (L5) |
| 19 | Customer sees unread on admin reply | **FAIL** | H4 — no public read state |
| 20 | Empty message rejected | **PASS** | `"Message content cannot be empty"` |
| 21 | Invalid conversation id rejected | **PASS** | `"Conversation not found"` / not-a-participant |
| 22 | Ended conversation blocks sending, keeps history | **PASS** | measured, both |
| 23 | Reconnect after network drop | **UNVERIFIABLE** | C1 — no socket to drop |
| 24 | Guest → login transition | **PARTIAL** | client clears guest state (`ChatContext:246-248`); server has no merge/link rule — C4 governs |
| 25 | Logout does not leak customer data | **PASS (server)** | 401 after logout; backend derives identity from cookie/header only |
| 26 | Public build + type check | **FAIL** | C5 — `next build` fails |
| 27 | Chat testable by Jest | **FAIL** | C5 — Jest loads the dead stub |
| 28 | Message length bounded | **FAIL** | M3 — 20 000 chars accepted |
| 29 | No static/mock chat data | **PASS** | no fake replies, no hard-coded message arrays; only static UI copy and canned admin quick-replies |
| 30 | Public chat after logout | **PASS** | falls back to guest behaviour by design |

**Score: 17 pass · 6 partial · 7 fail · 1 unverifiable** (of 30). The two defects that block the
largest number of scenarios are **C1 (no realtime at all)** and **C3 (every timestamp wrong)**.
