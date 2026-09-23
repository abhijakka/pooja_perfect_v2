"use client";

import { useEffect, useRef, useState, useSyncExternalStore } from "react";
import { usePathname } from "next/navigation";
import { Icon } from "../Icon";
import { useChat } from "../../hooks/useChat";

export function SupportChat() {
	const pathname = usePathname();
	const {
		open,
		messages,
		sending,
		booting,
		error,
		conversationId,
		guestStep,
		guestName,
		ended,
		unread,
		openChat,
		closeChat,
		send,
		endChat,
		newChat,
		submitGuestName,
		submitGuestEmail,
		clearError,
	} = useChat();
	const mounted = useSyncExternalStore(() => () => undefined, () => true, () => false);
	const [draft, setDraft] = useState("");
	const [name, setName] = useState("");
	const [email, setEmail] = useState("");
	const [showEmoji, setShowEmoji] = useState(false);
	const bodyRef = useRef<HTMLDivElement>(null);
	const inputRef = useRef<HTMLInputElement>(null);

	useEffect(() => {
		if (!open) return;
		inputRef.current?.focus();
		bodyRef.current?.scrollTo({ top: bodyRef.current.scrollHeight });
	}, [open, messages.length, booting, conversationId]);

	useEffect(() => {
		const closeOnEscape = (event: KeyboardEvent) => {
			if (event.key === "Escape") closeChat();
		};
		window.addEventListener("keydown", closeOnEscape);
		return () => window.removeEventListener("keydown", closeOnEscape);
	}, [closeChat]);

	const submit = (event: React.FormEvent<HTMLFormElement>) => {
		event.preventDefault();
		send(draft);
		setDraft("");
	};

	const insertEmoji = (emoji: string) => {
		setDraft((prev) => prev + emoji);
		setShowEmoji(false);
		inputRef.current?.focus();
	};

	const quickEmojis = ["😊", "🙏", "👍", "❤️", "😔", "🎉", "🙌", "✨"];

	if (!mounted || pathname.startsWith("/admin") || pathname.startsWith("/chat")) {
		return null;
	}

	const needsIdentity = guestStep === "name" || guestStep === "email";
	const greeting =
		guestStep === "name" ? (
			<div className="support-chat-message admin">
				<div className="support-chat-message-content">
					<div className="support-chat-bubble">
						Hi! Welcome to PoojaPoint support. May I know your name?
					</div>
				</div>
			</div>
		) : guestStep === "email" ? (
			<div className="support-chat-message admin">
				<div className="support-chat-message-content">
					<div className="support-chat-bubble">
						Thanks{guestName ? `, ${guestName}` : ""}! What is your email address?
					</div>
				</div>
			</div>
		) : null;

	return (
		<>
			<button
				className="support-chat-launcher"
				onClick={open ? closeChat : openChat}
				aria-label={open ? "Close customer support" : "Open customer support"}
			>
				<Icon name="chat" />
				{unread && !open && <span className="support-chat-notification">1</span>}
			</button>
			<section
				className={`support-chat-window ${open ? "open" : ""}`}
				aria-label="PoojaPoint customer support"
				aria-hidden={!open}
			>
				<header className="support-chat-header">
					<div className="support-chat-admin">
						<div className="support-chat-avatar">
							PP<span />
						</div>
						<div>
							<strong>PoojaPoint Support</strong>
							<span>
								<i /> Online · Usually replies quickly
							</span>
						</div>
					</div>
					<button className="support-chat-close" onClick={closeChat} aria-label="Close chat">
						×
					</button>
				</header>
				{conversationId && (
					<div className="support-chat-actions">
						<button
							className="support-chat-action-button"
							type="button"
							onClick={endChat}
							disabled={ended}
							aria-label="End chat"
						>
							End Chat
						</button>
						<button
							className="support-chat-action-button"
							type="button"
							onClick={newChat}
							aria-label="Start a new chat"
						>
							New Chat
						</button>
					</div>
				)}
				<div className="support-chat-body" ref={bodyRef} aria-live="polite">
					{greeting}
					{messages.length > 0 && <div className="support-chat-date">TODAY</div>}
					{messages.map((message) => (
						<div className={`support-chat-message ${message.author}`} key={message.id}>
							<div className="support-chat-message-content">
								<div className="support-chat-bubble">{message.text}</div>
								<div className="support-chat-time">{message.time}</div>
							</div>
						</div>
					))}
					{booting && !conversationId && (
						<div className="support-chat-message admin">
							<div className="support-chat-message-content">
								<div className="support-chat-bubble">Connecting you to support...</div>
							</div>
						</div>
					)}
					{ended && (
						<div className="support-chat-ended" role="status">
							This support session has ended. Click “New Chat” whenever you need help again.
						</div>
					)}
					{error && (
						<div className="support-chat-error" role="alert">
							{error}
							<button type="button" aria-label="Dismiss error" onClick={clearError}>
								×
							</button>
						</div>
					)}
				</div>
				<footer className="support-chat-footer">
					{needsIdentity ? (
						guestStep === "name" ? (
							<form
								className="support-chat-input-box"
								onSubmit={(event) => {
									event.preventDefault();
									submitGuestName(name);
								}}
							>
								<input
									ref={inputRef}
									className="support-chat-input"
									value={name}
									onChange={(event) => setName(event.target.value)}
									placeholder="Enter your name"
									autoComplete="name"
									aria-label="Enter your name"
								/>
								<button className="support-chat-send" type="submit" aria-label="Submit name">
									<Icon name="arrow-right" />
								</button>
							</form>
						) : (
							<form
								className="support-chat-input-box"
								onSubmit={(event) => {
									event.preventDefault();
									submitGuestEmail(email);
								}}
							>
								<input
									ref={inputRef}
									className="support-chat-input"
									type="email"
									value={email}
									onChange={(event) => setEmail(event.target.value)}
									placeholder="Enter your email address"
									autoComplete="email"
									aria-label="Enter your email address"
								/>
								<button className="support-chat-send" type="submit" aria-label="Submit email">
									<Icon name="arrow-right" />
								</button>
							</form>
						)
					) : (
						<>
							{showEmoji && (
								<div className="support-chat-emoji-picker">
									{quickEmojis.map((emoji) => (
										<button
											key={emoji}
											type="button"
											className="support-chat-emoji-btn"
											onClick={() => insertEmoji(emoji)}
											aria-label={`Insert ${emoji}`}
										>
											{emoji}
										</button>
									))}
								</div>
							)}
							<form className="support-chat-input-box" onSubmit={submit}>
								<button
									type="button"
									className={`support-chat-emoji-toggle ${showEmoji ? "active" : ""}`}
									onClick={() => setShowEmoji(!showEmoji)}
									aria-label="Toggle emoji picker"
								>
									😊
								</button>
								<input
									ref={inputRef}
									className="support-chat-input"
									value={draft}
									onChange={(event) => setDraft(event.target.value)}
									placeholder={ended ? "Chat ended — start a new chat" : "Type your message..."}
									disabled={ended || booting || !conversationId}
									autoComplete="off"
									aria-label="Message support"
								/>
								<button
									className="support-chat-send"
									type="submit"
									aria-label="Send message"
									disabled={ended || sending || booting || !conversationId}
								>
									<Icon name="arrow-right" />
								</button>
							</form>
						</>
					)}
					<div className="support-chat-note">PoojaPoint Support · Your conversation is private</div>
				</footer>
			</section>
		</>
	);
}