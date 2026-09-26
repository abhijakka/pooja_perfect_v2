import { environment } from "../../config/environment";
import type { AdminChatMessage, ChatMessage } from "../../types/chat";

type JsonObject = { [key: string]: JsonValue };
type JsonValue = string | number | boolean | null | JsonValue[] | JsonObject;

type SocketMessage = {
	id?: string;
	type: string;
	payload?: { data?: { chatMessage?: ChatMessage } };
};
type SocketHandler = (message: SocketMessage) => void;
type Cleanup = () => void;

const RECONNECT_DELAY_MS = 2500;
const MAX_RECONNECTS = 4;
const KEEP_ALIVE_MS = 30000;

const SUBSCRIPTION_QUERY = `
	subscription ChatMessage($conversationId: UUID!) {
		chatMessage(conversationId: $conversationId) {
			id conversationId senderId messageType content isRead mine createdAt
		}
	}
`;

const ADMIN_SUBSCRIPTION_QUERY = `
	subscription ChatMessage($conversationId: UUID!) {
		chatMessage(conversationId: $conversationId) {
			id conversationId senderId messageType content isRead createdAt
		}
	}
`;

function wsUrl(endpoint: string): string {
	const apiUrl = environment.apiUrl.replace(/\/+$/, "");
	return apiUrl.replace(/^http/, "ws") + endpoint;
}

/** Minimal `graphql-transport-ws` client shared by all chat subscriptions. */
class ChatSocketClient {
	private readonly endpoint: string;
	private socket: WebSocket | null = null;
	private connectionReady = false;
	private nextId = 1;
	private subscriptions = new Map<string, { handler: SocketHandler; query: string; variables: Record<string, unknown> }>();
	private pingTimer: number | null = null;
	private reconnectAttempts = 0;
	private shouldReconnect = true;

	constructor(endpoint: string) {
		this.endpoint = endpoint;
	}

	init(): void {
		if (this.socket) return;
		this.shouldReconnect = true;
		this.reconnectAttempts = 0;
		this.open();
	}

	private open(): void {
		let socket: WebSocket;
		try {
			socket = new WebSocket(wsUrl(this.endpoint), "graphql-transport-ws");
		} catch {
			this.scheduleReconnect();
			return;
		}
		this.socket = socket;

		socket.addEventListener("open", () => {
			socket.send(JSON.stringify({ type: "connection_init", payload: {} }));
		});

		socket.addEventListener("message", (event) => {
			let message: SocketMessage;
			try {
				message = JSON.parse(String(event.data)) as SocketMessage;
			} catch {
				return;
			}
			if (message.type === "connection_ack") {
				this.connectionReady = true;
				this.reconnectAttempts = 0;
				this.resubscribeAll();
				this.startKeepAlive(socket);
				return;
			}
			if (message.type === "ping") {
				socket.send(JSON.stringify({ type: "pong" }));
				return;
			}
			if (message.type === "pong") return;
			if (message.id && this.subscriptions.has(message.id)) {
				this.subscriptions.get(message.id)?.handler(message);
			}
		});

		socket.addEventListener("close", () => {
			this.connectionReady = false;
			this.socket = null;
			this.stopKeepAlive();
			if (this.shouldReconnect) this.scheduleReconnect();
		});

		socket.addEventListener("error", () => {
			socket.close();
		});
	}

	private scheduleReconnect(): void {
		if (!this.shouldReconnect) return;
		if (this.reconnectAttempts >= MAX_RECONNECTS) return;
		this.reconnectAttempts += 1;
		window.setTimeout(() => this.open(), RECONNECT_DELAY_MS * this.reconnectAttempts);
	}

	private resubscribeAll(): void {
		if (!this.socket || this.socket.readyState !== WebSocket.OPEN || !this.connectionReady) return;
		this.subscriptions.forEach((subscription, subscriptionId) => {
			this.socket?.send(
				JSON.stringify({
					id: subscriptionId,
					type: "subscribe",
					payload: { query: subscription.query, variables: subscription.variables },
				}),
			);
		});
	}

	private startKeepAlive(socket: WebSocket): void {
		if (this.pingTimer) return;
		this.pingTimer = window.setInterval(() => {
			if (socket.readyState === WebSocket.OPEN) {
				socket.send(JSON.stringify({ type: "ping" }));
			}
		}, KEEP_ALIVE_MS);
	}

	private stopKeepAlive(): void {
		if (this.pingTimer) {
			window.clearInterval(this.pingTimer);
			this.pingTimer = null;
		}
	}

	subscribe(subscriptionId: string, query: string, variables: Record<string, unknown>, handler: SocketHandler): void {
		this.subscriptions.set(subscriptionId, { handler, query, variables });
		if (this.socket && this.socket.readyState === WebSocket.OPEN && this.connectionReady) {
			this.socket.send(
				JSON.stringify({ id: subscriptionId, type: "subscribe", payload: { query, variables } }),
			);
		}
	}

	unsubscribe(subscriptionId: string): void {
		if (this.socket && this.socket.readyState === WebSocket.OPEN) {
			this.socket.send(JSON.stringify({ id: subscriptionId, type: "complete" }));
		}
		this.subscriptions.delete(subscriptionId);
	}

	dispose(): void {
		this.shouldReconnect = false;
		this.connectionReady = false;
		this.stopKeepAlive();
		this.subscriptions.clear();
		if (this.socket) {
			this.socket.close();
			this.socket = null;
		}
	}
}

type SubscriptionOptions = {
	conversationId: string;
	onMessage: (message: ChatMessage) => void;
	onNotFound?: () => void;
};

type AdminSubscriptionOptions = {
	conversationId: string;
	onMessage: (message: AdminChatMessage) => void;
	onNotFound?: () => void;
};

function createSubscription(
	socket: ChatSocketClient,
	query: string,
	subscriptionId: string,
	variables: Record<string, unknown>,
	onMessage: (message: ChatMessage) => void,
): Cleanup {
	let active = true;
	let lastSeenId: string | null = null;

	socket.init();
	socket.subscribe(
		subscriptionId,
		query,
		variables,
		(message) => {
			if (!active) return;
			const data = message.payload?.data;
			if (message.type === "next" && data?.chatMessage && message.id === subscriptionId) {
				const incoming = data.chatMessage;
				if (incoming.id === lastSeenId) return;
				lastSeenId = incoming.id;
				onMessage(incoming);
			}
		},
	);

	return () => {
		active = false;
		socket.unsubscribe(subscriptionId);
	};
}

const chatSocket = new ChatSocketClient("/graphql");
const adminChatSocket = new ChatSocketClient("/admin/graphql");

/**
 * Subscribe to realtime chat messages for a public conversation.
 * Safe to call multiple times for the same conversation — the socket is shared
 * and messages are de-duplicated per subscription by message id.
 */
export function subscribeToChat({ conversationId, onMessage, onNotFound }: SubscriptionOptions): Cleanup {
	return createSubscription(
		chatSocket,
		SUBSCRIPTION_QUERY,
		`chat-${conversationId}`,
		{ conversationId },
		onMessage,
	);
}

/**
 * Subscribe to realtime chat messages for an admin conversation view.
 *
 * The admin `ChatMessage` GraphQL type declares `createdAt: DateTime!` (non-null)
 * and has no `mine` field, so a frame whose `createdAt` is missing is malformed
 * and is dropped rather than rendered with an undefined time.
 */
export function subscribeToAdminChat({
	conversationId,
	onMessage,
}: AdminSubscriptionOptions): Cleanup {
	return createSubscription(
		adminChatSocket,
		ADMIN_SUBSCRIPTION_QUERY,
		`admin-chat-${conversationId}`,
		{ conversationId },
		(message) => {
			if (typeof message.createdAt !== "string") return;
			onMessage({ ...message, createdAt: message.createdAt });
		},
	);
}

export function disposeChatSocket(): void {
	chatSocket.dispose();
}

export function disposeAdminChatSocket(): void {
	adminChatSocket.dispose();
}