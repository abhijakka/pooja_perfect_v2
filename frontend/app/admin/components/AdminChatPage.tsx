"use client";

import { ChangeEvent, KeyboardEvent, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { AdminHeader } from "./AdminHeader";
import { AdminIcon, AdminIconSprite } from "./AdminIcon";
import { AdminSidebar } from "./AdminSidebar";
import { adminApi } from "../../../services/api/admin.api";
import type { AdminChatConversation, AdminChatMessage } from "../../../services/api/admin.api";
import { subscribeToAdminChat } from "../../../services/websocket/chat.socket";

type Status = "Online" | "Away" | "Ended";

function initialsOf(name: string): string {
	return name
		.split(/\s+/)
		.slice(0, 2)
		.map((part) => part.charAt(0).toUpperCase())
		.join("") || "?";
}

function timeAgo(value: string | null): string {
	if (!value) return "";
	const date = new Date(value);
	if (Number.isNaN(date.getTime())) return "";
	const seconds = Math.max(0, Math.round((Date.now() - date.getTime()) / 1000));
	if (seconds < 60) return "Now";
	if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
	if (seconds < 86400) return `${Math.floor(seconds / 3600)}h`;
	const days = Math.floor(seconds / 86400);
	if (days < 7) return `${days}d`;
	return date.toLocaleDateString([], { day: "numeric", month: "short" });
}

function clockTime(value: string | null): string {
	if (!value) return "";
	const date = new Date(value);
	if (Number.isNaN(date.getTime())) return "";
	return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function statusFor(conversation: AdminChatConversation): Status {
	return conversation.status === "ended" ? "Ended" : "Online";
}

function statusClass(status: Status): string {
	return status === "Online" ? "online" : "offline";
}

export function AdminChatPage() {
	const [sidebarOpen, setSidebarOpen] = useState(false);
	const [listOpen, setListOpen] = useState(false);
	const [query, setQuery] = useState("");
	const [toast, setToast] = useState("");
	const [conversations, setConversations] = useState<AdminChatConversation[]>([]);
	const [selectedId, setSelectedId] = useState<string | null>(null);
	const [messages, setMessages] = useState<AdminChatMessage[]>([]);
	const [loading, setLoading] = useState(true);
	const [sending, setSending] = useState(false);
	const [message, setMessage] = useState("");
	const [attachment, setAttachment] = useState("");
	const [showEmoji, setShowEmoji] = useState(false);

	const notify = useCallback((text: string) => {
		setToast(text);
		window.setTimeout(() => setToast(""), 2200);
	}, []);

	// An optimistic row is replaced by the server row once the send resolves, so its id only
	// has to be unique among rows still in flight. A ref counter keeps that guarantee without
	// reading a clock, which would make render impure.
	const pendingId = useRef(0);

	const refreshConversations = useCallback(
		async (keepSelection: string | null = selectedId) => {
			try {
				const result = await adminApi.listChatConversations(1, 50);
				setConversations(result.conversations.items);
				const stillExists =
					keepSelection && result.conversations.items.some((item) => item.id === keepSelection);
				if (!stillExists) {
					const next = result.conversations.items[0] ?? null;
					setSelectedId(next ? next.id : null);
				}
			} catch {
				notify("Could not load conversations");
			}
		},
		[selectedId, notify],
	);

	useEffect(() => {
		let isActive = true;
		adminApi
			.listChatConversations(1, 50)
			.then((result) => {
				if (!isActive) return;
				setConversations(result.conversations.items);
				setSelectedId(result.conversations.items[0]?.id ?? null);
			})
			.catch(() => {
				if (isActive) notify("Could not load conversations");
			})
			.finally(() => {
				if (isActive) setLoading(false);
			});
		return () => {
			isActive = false;
		};
	}, [notify]);

	// Fetching on selection is what an effect is for. The state updates live in the response
	// callbacks, and the cleanup drops a response that arrives after the selection moved on,
	// so a fast switch between conversations cannot show the previous one's messages.
	useEffect(() => {
		if (!selectedId) return;
		const conversationId = selectedId;
		let isActive = true;
		adminApi
			.getChatMessages(conversationId, 1, 100)
			.then((result) => {
				if (!isActive) return;
				setMessages([...result.messages.items].reverse());
			})
			.catch(() => {
				if (!isActive) return;
				setMessages([]);
				notify("Could not load this conversation");
			});
		adminApi.markChatRead(conversationId).catch(() => undefined);
		return () => {
			isActive = false;
		};
	}, [selectedId, notify]);

	useEffect(() => {
		if (!selectedId) return;
		const conversationId = selectedId;
		const cleanup = subscribeToAdminChat({
			conversationId,
			onMessage: (incoming) => {
				setMessages((current) =>
					current.some((item) => item.id === incoming.id)
						? current
						: [...current, incoming],
				);
				refreshConversations(conversationId);
			},
		});
		const timer = window.setInterval(() => {
			refreshConversations(conversationId);
		}, 10000);
		return () => {
			cleanup();
			window.clearInterval(timer);
		};
	}, [selectedId, refreshConversations]);

	const visibleConversations = useMemo(
		() =>
			conversations.filter((conversation) => {
				const needle = query.trim().toLowerCase();
				if (!needle) return true;
				return `${conversation.customerName ?? ""} ${conversation.customerEmail ?? ""} ${conversation.lastMessage ?? ""}`
					.toLowerCase()
					.includes(needle);
			}),
		[conversations, query],
	);

	const selected = conversations.find((conversation) => conversation.id === selectedId) ?? null;
	const hasSelected = selected !== null;
	const totalUnread = conversations.reduce((total, item) => total + item.unreadCount, 0);

	const selectConversation = (conversation: AdminChatConversation) => {
		setSelectedId(conversation.id);
		setListOpen(false);
		adminApi.markChatRead(conversation.id).catch(() => undefined);
	};

	const sendMessage = () => {
		const text = message.trim();
		if (!text || !hasSelected || sending || selected.status === "ended") {
			if (!text) notify("Type a message first");
			return;
		}
		setSending(true);
		const optimistic: AdminChatMessage = {
			id: `local-${(pendingId.current += 1)}`,
			conversationId: selected.id,
			senderId: null,
			messageType: "text",
			content: text,
			isRead: false,
			createdAt: new Date().toISOString(),
		};
		setMessages((current) => [...current, optimistic]);
		setMessage("");
		adminApi
			.sendChatMessage(selected.id, text)
			.then((result) => {
				setMessages((current) => current.map((item) => (item.id === optimistic.id ? result.sendMessage : item)));
				refreshConversations(selected.id);
			})
			.catch(() => notify("Could not send the message"))
			.finally(() => setSending(false));
	};

	const endChat = () => {
		if (!hasSelected || selected.status === "ended") return;
		setConversations((current) =>
			current.map((item) =>
				item.id === selected.id ? { ...item, status: "ended" } : item,
			),
		);
		adminApi
			.endChatConversation(selected.id)
			.then(() => notify("Conversation ended"))
			.catch(() => notify("Could not end the conversation"));
	};

	const keyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
		if (event.key === "Enter" && !event.shiftKey) {
			event.preventDefault();
			sendMessage();
		}
	};

	const attach = (event: ChangeEvent<HTMLInputElement>) => {
		const file = event.target.files?.[0];
		if (file) {
			setAttachment(file.name);
			notify("Attachment selected");
		}
	};

	const quickReply = (label: string) =>
		setMessage(
			label === "How can I help?"
				? "Hello! How can I help you today?"
				: label === "Order preparing"
					? "Your order is being prepared."
					: label === "Out for delivery"
						? "Your order is out for delivery."
						: "Thank you for contacting PoojaPoint!",
		);

	const quickEmojis = ["😊", "🙏", "👍", "❤️", "😔", "🎉", "🙌", "✨"];

	const insertEmoji = (emoji: string) => {
		setMessage((prev) => prev + (prev ? " " : "") + emoji);
		setShowEmoji(false);
	};

	return (
		<div className="admin-dashboard">
			<AdminIconSprite />
			<AdminSidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} activeHref="/admin/chat" />
			<main className="admin-main">
				<AdminHeader onMenu={() => setSidebarOpen(true)} query={query} onQuery={setQuery} title="Customer Chat" subtitle="Chat directly with PoojaPoint customers" />
				<div className="admin-content admin-chat-content">
					<div className="admin-chat-layout">
						<section className={`admin-chat-conversations ${listOpen ? "is-open" : ""}`}>
							<div className="admin-chat-conv-head">
								<div className="admin-chat-conv-title">
									<span>Conversations</span>
									<span className="admin-chat-count">{totalUnread}</span>
								</div>
								<label className="admin-chat-search">
									<AdminIcon name="search" />
									<input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search conversations..." />
								</label>
							</div>
							<div className="admin-chat-list">
								{loading && conversations.length === 0 && (
									<div className="admin-chat-date"><span>Loading conversations...</span></div>
								)}
								{!loading && conversations.length === 0 && (
									<div className="admin-chat-date"><span>No conversations yet. Customers will appear here when they start a chat.</span></div>
								)}
								{visibleConversations.map((conversation) => {
									const name = conversation.customerName ?? "Guest Customer";
									return (
										<button
											className={`admin-chat-person ${conversation.id === selectedId ? "active" : ""}`}
											type="button"
											key={conversation.id}
											onClick={() => selectConversation(conversation)}
										>
											<span className="admin-chat-avatar">
												{initialsOf(name)}
												{conversation.status === "active" && <i className="admin-chat-online" />}
											</span>
											<span className="admin-chat-person-body">
												<span className="admin-chat-person-top">
													<strong>{name}</strong>
													<small>{timeAgo(conversation.updatedAt)}</small>
												</span>
												<span className="admin-chat-preview">{conversation.lastMessage ?? "No messages yet"}</span>
											</span>
											{conversation.unreadCount > 0 && <span className="admin-chat-unread">{conversation.unreadCount}</span>}
										</button>
									);
								})}
							</div>
						</section>
						<section className="admin-chat-main">
							{!hasSelected ? (
								<div className="admin-chat-date"><span>Select a conversation to start supporting a customer.</span></div>
							) : (
								<>
									<header className="admin-chat-head">
										<button className="admin-chat-action admin-chat-list-button" type="button" aria-label="Open conversations" onClick={() => setListOpen(true)}>
											<AdminIcon name="menu" />
										</button>
										<div className="admin-chat-customer-head">
											<span className="admin-chat-avatar large">
												{initialsOf(selected.customerName ?? "Guest Customer")}
												{selected.status === "active" && <i className="admin-chat-online" />}
											</span>
											<div>
												<strong>{selected.customerName ?? "Guest Customer"}</strong>
												<span className={`admin-chat-status ${statusClass(statusFor(selected))}`}>
													<i />
													{statusFor(selected)}
													{selected.customerName ? " · Customer" : " · Guest"}
												</span>
											</div>
										</div>
										<div className="admin-chat-actions">
											<button className="admin-chat-action" type="button" aria-label="End conversation" onClick={endChat} disabled={selected.status === "ended"}>
												<AdminIcon name="close" />
											</button>
										</div>
									</header>
									<div className="admin-chat-messages">
										{messages.length === 0 && <div className="admin-chat-date"><span>Start of conversation</span></div>}
										{messages.map((item) => {
											const isCustomer = item.senderId != null && item.senderId === selected.customerId;
											return (
												<div className={`admin-chat-message ${isCustomer ? "customer" : "admin"}`} key={item.id}>
													<div>
														<div className="admin-chat-bubble">{item.content}</div>
														<span className="admin-chat-meta">{clockTime(item.createdAt)}</span>
													</div>
												</div>
											);
										})}
									</div>
									<div className="admin-chat-composer">
										<div className="admin-chat-quick">
											{["How can I help?", "Order preparing", "Out for delivery", "Thank you"].map((label) => (
												<button type="button" key={label} onClick={() => quickReply(label)} disabled={selected.status === "ended"}>
													{label}
												</button>
											))}
										</div>
										{attachment && (
											<div className="admin-chat-file">
												<span>{attachment}</span>
												<button type="button" aria-label="Remove attachment" onClick={() => setAttachment("")}>
													<AdminIcon name="close" />
												</button>
											</div>
										)}
										{showEmoji && (
											<div className="admin-chat-emoji-picker">
												{quickEmojis.map((emoji) => (
													<button
														key={emoji}
														type="button"
														className="admin-chat-emoji-btn"
														onClick={() => insertEmoji(emoji)}
														aria-label={`Insert ${emoji}`}
													>
														{emoji}
													</button>
												))}
											</div>
										)}
										<div className="admin-chat-compose">
											<label className="admin-chat-compose-button" aria-label="Attach file">
												<AdminIcon name="upload" />
												<input type="file" accept="image/*,.pdf,.doc,.docx" onChange={attach} disabled={selected.status === "ended"} />
											</label>
											<textarea
												value={message}
												onChange={(event) => setMessage(event.target.value)}
												onKeyDown={keyDown}
												placeholder={selected.status === "ended" ? "Conversation ended — start a new chat" : "Type a message..."}
												rows={1}
												disabled={selected.status === "ended"}
												aria-label="Type a message"
											/>
											<button className="admin-chat-compose-button" type="button" aria-label="Add emoji" disabled={selected.status === "ended"} onClick={() => setShowEmoji(!showEmoji)}>
												<span aria-hidden="true">😊</span>
											</button>
											<button className="admin-chat-send" type="button" aria-label="Send message" onClick={sendMessage} disabled={selected.status === "ended"}>
												<AdminIcon name="send" />
											</button>
										</div>
									</div>
								</>
							)}
						</section>
						{hasSelected && selected.customerName && (
							<aside className="admin-chat-info">
								<div className="admin-chat-info-head">
									<span className="admin-chat-big-avatar">{initialsOf(selected.customerName)}</span>
									<strong>{selected.customerName}</strong>
									<small>{selected.customerEmail}</small>
									<span className="admin-chat-online-label">
										<i />
										{statusFor(selected)}
									</span>
								</div>
								<div className="admin-chat-info-section">
									<h3>Conversation</h3>
									<p><span>Status</span><b>{selected.status === "ended" ? "Ended" : "Active"}</b></p>
									<p><span>Unread</span><b>{selected.unreadCount}</b></p>
									<p><span>Customer</span><b>{selected.customerEmail ?? "Guest (no account)"}</b></p>
								</div>
								<div className="admin-chat-info-section">
									<h3>Quick Actions</h3>
									<button type="button" onClick={() => notify("Customer profile opened")}>
										View Customer
									</button>
									<button type="button" onClick={() => notify("Email action opened")}>
										Send Email
									</button>
									<button
										type="button"
										onClick={() =>
											window.confirm("End this conversation?") && endChat()
										}
									>
										End Conversation
									</button>
								</div>
							</aside>
						)}
					</div>
				</div>
			</main>
			<div className={`admin-chat-toast ${toast ? "show" : ""}`} role="status">
				<span className="admin-chat-toast-icon">
					<AdminIcon name="check" />
				</span>
				<div>
					<strong>PoojaPoint</strong>
					<p>{toast}</p>
				</div>
			</div>
		</div>
	);
}