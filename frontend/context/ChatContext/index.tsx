"use client";

import {
	createContext,
	useCallback,
	useContext,
	useEffect,
	useMemo,
	useRef,
} from "react";
import type { ReactNode } from "react";
import { chatApi } from "../../services/api/chat.api";
import { subscribeToChat } from "../../services/websocket/chat.socket";
import { useAppDispatch, useAppSelector } from "../../store/hooks";
import {
	appendMessage,
	closeChat,
	openChat,
	setBooting,
	setChatError,
	setConversation,
	setGuestEmail,
	setGuestName,
	setGuestStep,
	setLoadingMessages,
	setSending,
	replaceMessages,
	resetChat,
} from "../../store/slices/chatSlice";
import type { ChatConversation, ChatMessage, UiChatMessage } from "../../types/chat";

const GUEST_NAME_KEY = "pp-chat-guest-name";
const GUEST_EMAIL_KEY = "pp-chat-guest-email";
const CONVERSATION_KEY = "pp-chat-conversation";

const EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;

function loadStoredString(key: string): string | null {
	if (typeof window === "undefined") return null;
	try {
		return window.localStorage.getItem(key);
	} catch {
		return null;
	}
}

function storeString(key: string, value: string): void {
	try {
		window.localStorage.setItem(key, value);
	} catch {
		// storage unavailable — guest identity is still sent per request
	}
}

function clearStoredString(key: string): void {
	try {
		window.localStorage.removeItem(key);
	} catch {
		// ignore
	}
}

function formatTime(value: string | null): string {
	if (!value) return "";
	try {
		const date = new Date(value);
		if (Number.isNaN(date.getTime())) return "";
		return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
	} catch {
		return "";
	}
}

export function toUiMessage(message: ChatMessage): UiChatMessage {
	return {
		id: message.id,
		author: message.mine ? "customer" : "admin",
		text: message.content,
		time: formatTime(message.createdAt),
	};
}

function errorMessage(error: unknown): string {
	if (error instanceof Error) return error.message;
	return "Something went wrong. Please try again.";
}

type ChatContextValue = {
	open: boolean;
	booting: boolean;
	loadingMessages: boolean;
	sending: boolean;
	error: string | null;
	conversationId: string | null;
	guestName: string;
	guestEmail: string;
	guestStep: "none" | "name" | "email" | "done";
	ended: boolean;
	messages: UiChatMessage[];
	unread: boolean;
	openChat: () => void;
	closeChat: () => void;
	send: (text: string) => void;
	endChat: () => void;
	newChat: () => void;
	submitGuestName: (name: string) => void;
	submitGuestEmail: (email: string) => void;
	clearError: () => void;
};

const ChatContext = createContext<ChatContextValue | null>(null);

export function ChatProvider({ children }: { children: ReactNode }) {
	const dispatch = useAppDispatch();
	const chat = useAppSelector((state) => state.chat);
	const auth = useAppSelector((state) => state.auth);
	const bootRequested = useRef(false);

	const isAuthenticated = auth.isAuthenticated;
	const authReady = auth.isReady;

	const sessionIdentity = useCallback(() => {
		if (isAuthenticated) return undefined;
		const name = loadStoredString(GUEST_NAME_KEY);
		const email = loadStoredString(GUEST_EMAIL_KEY);
		if (name && email) return { name, email };
		return null;
	}, [isAuthenticated]);

	const loadMessages = useCallback(
		async (conversationId: string) => {
			dispatch(setLoadingMessages(true));
			try {
				const collected: UiChatMessage[] = [];
				let page = 1;
				let hasNext = true;
				while (hasNext && page <= 5) {
					const result = await chatApi.messages(conversationId, page, 50);
					const items = result.messages.items
						.slice()
						.reverse()
						.map(toUiMessage);
					for (let i = items.length - 1; i >= 0; i -= 1) {
						collected.unshift(items[i]);
					}
					hasNext = result.messages.pagination.hasNext;
					page += 1;
				}
				dispatch(replaceMessages(collected));
			} catch {
				// Clear stored conversation ID so next attempt starts fresh
				clearStoredString(CONVERSATION_KEY);
				dispatch(setChatError("Could not load your chat history. Please try again."));
			} finally {
				dispatch(setLoadingMessages(false));
			}
		},
		[dispatch],
	);

	const establishConversation = useCallback(
		async (forceNew: boolean) => {
			dispatch(setBooting(true));
			dispatch(setChatError(null));
			try {
				if (!isAuthenticated) {
					const identity = sessionIdentity();
					if (!identity) {
						dispatch(setGuestStep("name"));
						dispatch(setBooting(false));
						return;
					}
					if (forceNew) {
						const result = await chatApi.startConversation(identity.name, identity.email, true);
						const conversation = result.startConversation;
						storeString(CONVERSATION_KEY, conversation.id);
						dispatch(setConversation({ id: conversation.id, ended: conversation.status === "ended" }));
						await loadMessages(conversation.id);
						dispatch(setBooting(false));
						return;
					}
				} else if (forceNew) {
					const result = await chatApi.startConversation(undefined, undefined, true);
					const conversation = result.startConversation;
					storeString(CONVERSATION_KEY, conversation.id);
					dispatch(setConversation({ id: conversation.id, ended: conversation.status === "ended" }));
					await loadMessages(conversation.id);
					dispatch(setBooting(false));
					return;
				}

				let conversation: ChatConversation | null = null;
				const storedId = loadStoredString(CONVERSATION_KEY);
				if (storedId) {
					try {
						const result = await chatApi.conversation(storedId);
						if (result.conversation) conversation = result.conversation;
					} catch {
						// Clear stale/inaccessible conversation ID
						clearStoredString(CONVERSATION_KEY);
					}
				}
				if (!conversation) {
					const active = await chatApi.activeConversation();
					conversation = active.activeConversation;
				}
				if (!conversation) {
					const identity = sessionIdentity();
					const result = await chatApi.startConversation(
						identity?.name,
						identity?.email,
						false,
					);
					conversation = result.startConversation;
				}
				storeString(CONVERSATION_KEY, conversation.id);
				dispatch(setGuestStep("done"));
				dispatch(
					setConversation({
						id: conversation.id,
						ended: conversation.status === "ended",
					}),
				);
				if (conversation.status !== "ended") {
					await loadMessages(conversation.id);
				}
			} catch (error) {
				dispatch(setChatError(errorMessage(error)));
			} finally {
				dispatch(setBooting(false));
			}
		},
		[dispatch, isAuthenticated, sessionIdentity, loadMessages],
	);

	useEffect(() => {
		if (!authReady || bootRequested.current) return;
		bootRequested.current = true;
		establishConversation(false);
	}, [authReady, establishConversation]);

	useEffect(() => {
		if (!authReady || !isAuthenticated) return;
		// Authenticated session: drop any guest identity and resume the
		// customer's own conversation.
		clearStoredString(GUEST_NAME_KEY);
		clearStoredString(GUEST_EMAIL_KEY);
		clearStoredString(CONVERSATION_KEY);
		bootRequested.current = true;
		establishConversation(false);
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [authReady, isAuthenticated]);

	useEffect(() => {
		if (
			!authReady ||
			isAuthenticated ||
			chat.open ||
			chat.conversationId ||
			chat.guestStep !== "none"
		) {
			return;
		}
		// Returning guest: restore saved identity and resume the saved session.
		const identity = loadStoredString(GUEST_NAME_KEY);
		if (identity) {
			dispatch(setGuestStep("done"));
			establishConversation(false);
		} else {
			dispatch(setGuestStep("name"));
		}
	}, [authReady, isAuthenticated, chat.open, chat.conversationId, chat.guestStep, dispatch, establishConversation]);

	useEffect(() => {
		if (!chat.conversationId || chat.ended || !chat.open) return;
		const conversationId = chat.conversationId;
		const cleanup = subscribeToChat({
			conversationId,
			onMessage: (message) => dispatch(appendMessage(toUiMessage(message))),
		});
		return cleanup;
	}, [chat.conversationId, chat.ended, chat.open, dispatch]);

	useEffect(() => {
		if (!chat.conversationId || chat.ended || !chat.open) return;
		const conversationId = chat.conversationId;
		const timer = window.setInterval(() => {
			chatApi
				.messages(conversationId, 1, 50)
				.then((result) => {
					const items = result.messages.items.slice().reverse();
					for (const message of items) {
						dispatch(appendMessage(toUiMessage(message)));
					}
				})
				.catch(() => {
					// polling is best-effort, realtime remains primary
				});
		}, 8000);
		return () => window.clearInterval(timer);
	}, [chat.conversationId, chat.ended, chat.open, dispatch]);

	const openChatHandler = useCallback(() => {
		dispatch(openChat());
		if (!chat.conversationId && authReady) establishConversation(false);
	}, [authReady, chat.conversationId, dispatch, establishConversation]);

	const closeChatHandler = useCallback(() => dispatch(closeChat()), [dispatch]);

	const send = useCallback(
		(text: string) => {
			const clean = text.trim();
			if (
				!clean ||
				!chat.conversationId ||
				chat.ended ||
				chat.sending ||
				chat.booting
			) {
				return;
			}
			dispatch(setSending(true));
			dispatch(setChatError(null));
			chatApi
				.sendMessage(chat.conversationId, clean)
				.then((result) => {
					dispatch(appendMessage(toUiMessage(result.sendChatMessage)));
				})
				.catch((error) => dispatch(setChatError(errorMessage(error))))
				.finally(() => dispatch(setSending(false)));
		},
		[chat.conversationId, chat.ended, chat.sending, chat.booting, dispatch],
	);

	const endChat = useCallback(() => {
		if (!chat.conversationId || chat.ended) return;
		dispatch(setSending(false));
		dispatch(setChatError(null));
		chatApi
			.endConversation(chat.conversationId)
			.then((result) => {
				dispatch(
					setConversation({
						id: result.endConversation.id,
						ended: result.endConversation.status === "ended",
					}),
				);
			})
			.catch((error) => dispatch(setChatError(errorMessage(error))));
	}, [chat.conversationId, chat.ended, dispatch]);

	const newChat = useCallback(() => {
		dispatch(resetChat());
		establishConversation(true);
	}, [dispatch, establishConversation]);

	const submitGuestName = useCallback(
		(name: string) => {
			const clean = name.trim();
			if (!clean) {
				dispatch(setChatError("Please tell us your name to start chatting."));
				return;
			}
			dispatch(setGuestName(clean));
			storeString(GUEST_NAME_KEY, clean);
			dispatch(setGuestStep("email"));
		},
		[dispatch],
	);

	const submitGuestEmail = useCallback(
		(email: string) => {
			const clean = email.trim();
			if (!EMAIL_RE.test(clean)) {
				dispatch(setChatError("Please enter a valid email address."));
				return;
			}
			dispatch(setGuestEmail(clean));
			storeString(GUEST_EMAIL_KEY, clean);
			dispatch(setGuestStep("done"));
			establishConversation(false);
		},
		[dispatch, establishConversation],
	);

	const clearError = useCallback(() => dispatch(setChatError(null)), [dispatch]);

	const value = useMemo<ChatContextValue>(
		() => ({
			open: chat.open,
			booting: chat.booting,
			loadingMessages: chat.loadingMessages,
			sending: chat.sending,
			error: chat.error,
			conversationId: chat.conversationId,
			guestName: chat.guestName,
			guestEmail: chat.guestEmail,
			guestStep: chat.guestStep,
			ended: chat.ended,
			messages: chat.messages,
			unread: chat.unread,
			openChat: openChatHandler,
			closeChat: closeChatHandler,
			send,
			endChat,
			newChat,
			submitGuestName,
			submitGuestEmail,
			clearError,
		}),
		[
			chat.open,
			chat.booting,
			chat.loadingMessages,
			chat.sending,
			chat.error,
			chat.conversationId,
			chat.guestName,
			chat.guestEmail,
			chat.guestStep,
			chat.ended,
			chat.messages,
			chat.unread,
			openChatHandler,
			closeChatHandler,
			send,
			endChat,
			newChat,
			submitGuestName,
			submitGuestEmail,
			clearError,
		],
	);

	return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
}

export function useChat(): ChatContextValue {
	const context = useContext(ChatContext);
	if (context === null) {
		throw new Error("useChat must be used within a ChatProvider");
	}
	return context;
}

export { clearStoredString };