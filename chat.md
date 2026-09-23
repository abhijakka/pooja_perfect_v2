# Customer Chat Implementation

## Frontend Audit

Stack: Next.js 16 (App Router) + React 19 + TypeScript + Redux Toolkit + SWR. Public and admin apps live under `frontend/app`. Global client providers in `app/providers.tsx` mount `<SupportChat />`. Rails:
- `services/api/*.api.ts` — thin GraphQL/REST callers (`client.ts` has `graphqlClient` → `/graphql` and `adminGraphqlClient` → `/admin/graphql`, `credentials: include`).
- `store/slices/*` — Redux state. `authSlice` holds `user`, `isAuthenticated`, `isReady`.
- `hooks/useChat.ts` — currently a mock (static Redux messages + local `replyFor`).
- `components/chat/SupportChat.tsx` — floating chat widget (mock data).
- `app/(public)/chat/page.tsx` — `/chat` page (just opens the widget).
- `app/admin/components/AdminChatPage.tsx` — fully static mock admin chat UI (hard-coded `customers`, `messages`).
- `services/websocket/` — stubs only.
- Loader: `components/layout/PoojaPointLoader.tsx`; admin pages use their own `loading` boolean + error state + toast (`notify`).

## Backend Audit

Stack: FastAPI + Strawberry GraphQL (`backend/src/app`). Two GraphQL routers in `app/main.py`:
- Public customer API: `POST /graphql` (`public_schema`), optional bearer auth.
- Admin API: `/admin/graphql` (`admin_schema`), gated by `require_admin` in `app/admin/context.py` → `app/dependencies/auth.py` (`get_current_user` → `get_current_active_user` → `require_admin`, role `UserRole.ADMIN`).
- REST auth at `/auth/*` sets httpOnly `access_token`/`refresh_token` cookies.
- DB: SQLite `backend/poojapoint.db` (from `backend/.env` `DATABASE_URL`); SQLAlchemy 2.0 models `app/models/*`, Alembic migrations in `backend/alembic/versions/`. Tests use in-memory SQLite (`app/tests/conftest.py`).
- App errors: `app/core/exceptions.py` (`AppError` → status code + detail; `PermissionDeniedError` 403, `NotFoundError` 404, `ValidationError` 422, `DuplicateResourceError` 409).
- Tests: pytest under `app/tests/`, run with `.venv\Scripts\python.exe -m pytest`.

## Existing Chat System

Models (`app/models/`):
- `conversation.py` — `Conversation` (id, `subject`, created/updated). **No status column.**
- `conversation_participant.py` — `ConversationParticipant` (conversation_id, user_id, `participant_role`) unique (conversation, user).
- `chat_message.py` — `ChatMessage` (conversation_id, sender_id → users.id, `message_type`, `content`, `is_read`, `read_at`, timestamps).
- `enums.py` — `MessageType` (text/image/file).

Public side (`app/public/`):
- `api/graphql/types/chat.py` — `ChatMessageType`, `ConversationType` (no status).
- `api/graphql/queries/chat.py` — `conversations`, `conversation`, `messages` (all `require_user`).
- `api/graphql/mutations/chat.py` — `sendChatMessage` (`require_user`), publishes `chat:{conversation_id}`.
- `api/graphql/subscriptions/chat.py` — `chatMessage` subscription (`require_user`, participant check).
- `api/graphql/subscriptions/pubsub.py` — in-memory `SimplePubSub`; topics `chat:{id}`, `notifications:{user_id}`.
- `services/chat_service.py` — `conversations`, `get_conversation`, `messages`, `send_message`, `send_first_message`, `get_or_create_support`.
- `repositories/chat_repository.py` — list by user, participant checks, create conversation/add participant, `get_or_create_support_conversation` (subject `"support"`), messages (desc), send_message. Ownership/participant checks present for public reads.

Admin side (`app/admin/`):
- `api/graphql/queries/chat.py` — `conversations`, `conversation`, `messages` (admin-gated via context).
- `api/graphql/mutations/chat.py` — `sendMessage`, `mark_read`.
- `api/graphql/types/chat.py` — `ChatMessageType`, `ConversationType` **references** `customer_id`, `customer_name`, `customer_email`, `status`, `last_message`, `unread_count` — but the repository `conversations()` does NOT populate them (solvers read via `getattr`, so they are `None`).
- `services/chat_service.py` / `repositories/chat_repository.py` — basic list/get/messages/send/mark_read.
- Admin `sendMessage` does NOT publish to the shared pubsub, and the admin schema has **no subscription**, so customer and admin never see messages in realtime.

## Existing Authentication

- REST `/auth/login|register|refresh|logout|me`; httpOnly cookie `access_token`. Public GraphQL context (`app/public/context.py`) uses `get_optional_current_user` (bearer header only). `require_user(ctx)` forces auth; `require_user_or_guest(ctx)` fabricates a guest `User` keyed by a persistent `guest_token` cookie (mapped via `Cart.guest_token_hash`). Guest users are created as `first_name="Guest"`, `last_name="Customer"`, `email="guest-<hex>@guest.local"`. Frontend `useAuth()`/`authSlice` restore the session from `/auth/me`.

## Existing AdminCustomerChat

`frontend/app/admin/chat/page.tsx` → `AdminChatPage.tsx`. Fully **static mock**: hard-coded `customers[]` and `initialMessages[]`, local-array reply/send. No API calls. Admin layout (`app/admin/layout.tsx`) enforces frontend role guard. Backend admin queries exist but return incomplete data (see above).

## Existing Public ChatApplication

`components/chat/SupportChat.tsx` (floating widget) + `app/(public)/chat/page.tsx`. Uses `useChat` → `store/slices/chatSlice.ts` with **static** `initialMessages` and a mock local `replyFor()` reply bot. `services/api/chat.api.ts` and `services/websocket/chat.socket.ts` are empty stubs; `context/ChatContext` and `types/chat.ts` are placeholder/partial.

## Existing Realtime System

Strawberry GraphQL subscriptions over WebSocket. Public subscription `chatMessage(conversationId)` backed by an in-memory `SimplePubSub` (`chat:{conversation_id}`). Admin schema: none. Frontend: no WS client yet (`services/websocket/*` are stubs). Subprotocol for Strawberry is `graphql-transport-ws`.

## Existing Database Models

- `Conversation` (subject only, no status), `ConversationParticipant`, `ChatMessage` (FK conversation/users, `sender_id` NOT NULL → every message requires a real `User.id`; guest chat therefore requires the guest-`User` row created by `require_user_or_guest`). Duplicate chat tables do not exist — reuse these.

## Files To Modify

Backend:
- `backend/src/app/models/conversation.py` — add `status` (`active`/`ended`).
- `backend/src/app/models/user.py` — add `is_guest` flag.
- `backend/alembic/versions/*` — new migration for the above columns.
- `backend/src/app/public/context.py` — mark guest users `is_guest=True`.
- `backend/src/app/public/repositories/chat_repository.py` — status-aware support conversation lookup, end, new-conversation, last message/unread helpers.
- `backend/src/app/public/services/chat_service.py` — start/resume, force-new, end, ended-block.
- `backend/src/app/public/api/graphql/types/chat.py` — expose `status`.
- `backend/src/app/public/api/graphql/queries/chat.py` — guest support + `activeConversation` query.
- `backend/src/app/public/api/graphql/mutations/chat.py` — `startConversation`, `endConversation`; guest send.
- `backend/src/app/public/api/graphql/subscriptions/chat.py` — guest support.
- `backend/src/app/public/api/graphql/schema.py` — register new query/mutations.
- `backend/src/app/admin/repositories/chat_repository.py` — conversations joined with customer + last message + unread + status.
- `backend/src/app/admin/services/chat_service.py` — populate conversation details, end conversation.
- `backend/src/app/admin/api/graphql/queries/chat.py` — map actual detail fields.
- `backend/src/app/admin/api/graphql/mutations/chat.py` — publish to pubsub + `endConversation`.
- `backend/src/app/admin/api/graphql/subscriptions/chat.py` — **new** admin realtime subscription.
- `backend/src/app/admin/api/graphql/schema.py` — register subscription/mutation.
- `backend/src/app/tests/test_public_chat.py`, `test_admin_chat.py` — expand coverage.

Frontend:
- `frontend/types/chat.ts` — real conversation/message types.
- `frontend/services/api/chat.api.ts` — public chat GraphQL client.
- `frontend/services/api/admin.api.ts` — admin chat operations.
- `frontend/services/websocket/chat.socket.ts` — `graphql-transport-ws` subscription client (+ polling fallback).
- `frontend/store/slices/chatSlice.ts` — remove mock data; backend-driven state.
- `frontend/hooks/useChat.ts` — full flow (guest/auth/session/realtime).
- `frontend/components/chat/SupportChat.tsx` — wire to backend; End/New Chat; guest form.
- `frontend/app/(public)/chat/page.tsx` — full-page ChatApplication.
- `frontend/app/(public)/chat/page.test.tsx` — update test.
- `frontend/components/chat/SupportChat.test.tsx`, `frontend/store/slices/chatSlice.test.ts` — update tests.
- `frontend/app/admin/components/AdminChatPage.tsx` — real backend data.

## Files To Create

- `backend/src/app/admin/api/graphql/subscriptions/chat.py`
- `backend/alembic/versions/<rev>_add_conversation_status_and_user_is_guest.py`
- Realtime subscription support in the admin schema (new file above).

## API Contract

Public `/graphql` (existing naming, camelCase):
- `startConversation(name: String, email: String, forceNew: Boolean = false) -> Conversation` — resume the active support conversation for the caller, or create a new one; guest name/email validated + stored on the guest user.
- `endConversation(conversationId: UUID!) -> Conversation` — mark ended (owner only).
- `sendChatMessage(conversationId: UUID!, content: String!, messageType: String = "text") -> ChatMessage` (existing; now guest-capable, blocked when ended).
- `activeConversation -> Conversation | null` — resume on refresh.
- `conversations`, `conversation(id)`, `messages(conversationId)` (existing; now guest-capable, ownership-checked).
- Subscription `chatMessage(conversationId: UUID!)` (existing; guest-capable, participant-checked).

Admin `/admin/graphql` (admin-only via context):
- `conversations(page, pageSize)`, `conversation(id)`, `messages(conversationId, page, pageSize)` (existing) — now return `customerId`, `customerName`, `customerEmail`, `status`, `lastMessage`, `unreadCount`, `createdAt`, `updatedAt`.
- `sendMessage(conversationId, content, messageType)` (existing; now publishes to the public `chat:{id}` topic).
- `markRead(conversationId)` (existing).
- `endConversation(conversationId: UUID!)` (new).
- Subscription `chatMessage(conversationId: UUID!)` (new; admin sees customer messages realtime).

Conversation status values: `active` (open) / `ended` (closed). Support conversations use `subject = "support"`.

## Authenticated User Flow

Open chat → `startConversation()` (no args) → resumes active support conversation or creates one → subscribe `chatMessage` → load messages → chat. Name/email come from the account; never re-asked.

## Guest User Flow

Guest (no auth) opens chat → backend creates/marks the `guest_token`→`User` → frontend shows greeting flow: "Hi" → ask name → ask email → validate on frontend + backend → `startConversation(name, email)` → conversation (owner = guest user) → subscribe → chat. Guest name/email cached in `localStorage` to avoid re-asking; refresh restores the same conversation via `activeConversation`.

## Chat Session Lifecycle

`Conversation.status`: creates as `active`; `endConversation` sets `ended`. Messages cannot be sent to `ended` conversations (backend enforced). `startConversation(forceNew: true)` (New Chat) ends any existing active support conversation and creates a fresh one — the previous conversation is preserved.

## End Chat

`endConversation(conversationId)` → status `ended` → frontend disables input, shows "Chat ended. You can start a new chat whenever you need help."

## New Chat

`startConversation(forceNew: true)` → new conversation (new id), messages cleared, new subscription. Authenticated: no extra identity questions. Guest: reuses cached name/email from the guest session.

## Admin Chat Flow

Conversation list (real data) → select → fetch messages + `markRead` → reply via `sendMessage` (persisted, published realtime to customer) → optional `endConversation`.

## Authorization

- Admin API: every resolver gated by `AdminContext` (`require_admin` → active + `role_name == "admin"`).
- Public chat: participant/ownership enforced in the repository/service (`is_participant`), never trusting `conversation_id`/`user_id` from the payload.
- Guests only reach their own conversations (guest identity derived from the signed `guest_token` cookie server-side).
- Frontend admin route guard exists but backend enforcement is authoritative.

## Conversation Ownership

`get_conversation`, `messages`, `send_message`, `end_conversation`, and the `chatMessage` subscription all re-verify that the caller is a participant of the conversation. Admin can access any conversation (admin role).

## Testing Plan

- Backend pytest: guest start/resume/new/end/send-validations, ownership isolation (guest A ↔ guest B, customer ↔ other customer), admin reply persistence, admin list detail fields, authorization (customer/guest → admin API → forbidden), ended-block, status transitions.
- Frontend: `npm test` (update chatSlice/SupportChat/page tests), `npm run lint`, `tsc` via `next build`.
- Build: `npm run build`.
- Realtime: WS connect/disconnect/reconnect/message/reply/session-end/new-chat manual + code paths.

## Implementation Status

Audit complete. Implementation of the plan above is in progress. Results appended below at the end.