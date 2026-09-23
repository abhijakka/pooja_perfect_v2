"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { Icon } from "../Icon";
import { PoojaPointLoader } from "../layout/PoojaPointLoader";
import { useChat } from "../../hooks/useChat";

export function ChatApplication() {
	const {
		booting,
		loadingMessages,
		sending,
		conversationId,
		guestStep,
		guestName,
		ended,
		messages,
		error,
		send,
		endChat,
		newChat,
		submitGuestName,
		submitGuestEmail,
		openChat,
		clearError,
	} = useChat();
	const [draft, setDraft] = useState("");
	const [name, setName] = useState("");
	const [email, setEmail] = useState("");
	const [showEmoji, setShowEmoji] = useState(false);
	const bodyRef = useRef<HTMLElement>(null);
	const inputRef = useRef<HTMLInputElement>(null);

	useEffect(() => {
		openChat();
	}, [openChat]);

	useEffect(() => {
		bodyRef.current?.scrollTo({ top: bodyRef.current.scrollHeight });
	}, [messages.length, booting, ended, conversationId]);

	useEffect(() => {
		inputRef.current?.focus();
	}, [conversationId, guestStep]);

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
		<main className="chat-application" aria-label="PoojaPoint customer support">
			{booting && !conversationId && <PoojaPointLoader />}
			<header className="chat-application-header">
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
				<div className="chat-application-actions">
					<Link href="/" className="chat-application-link">
						Continue Shopping
					</Link>
					{conversationId && (
						<button
							className="support-chat-action-button"
							type="button"
							onClick={endChat}
							disabled={ended}
							aria-label="End chat"
						>
							End Chat
						</button>
					)}
					<button
						className="support-chat-action-button"
						type="button"
						onClick={newChat}
						aria-label="Start a new chat"
					>
						New Chat
					</button>
				</div>
			</header>
			<section className="chat-application-body" ref={bodyRef} aria-live="polite">
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
				{sending && (
					<div className="support-chat-message admin">
						<div className="support-chat-message-content">
							<div className="support-chat-typing" aria-label="PoojaPoint Support is typing">
								<span />
								<span />
								<span />
							</div>
						</div>
					</div>
				)}
				{conversationId && loadingMessages && (
					<div className="support-chat-message admin">
						<div className="support-chat-message-content">
							<div className="support-chat-bubble">Loading your conversation...</div>
						</div>
					</div>
				)}
				{ended && (
					<div className="support-chat-ended" role="status">
						This support session has ended. You can still read the conversation above — start a
						new chat whenever you need help again.
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
			</section>
			<footer className="chat-application-footer">
				{needsIdentity ? (
					guestStep === "name" ? (
						<form
							className="support-chat-input-box chat-application-input-box"
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
							className="support-chat-input-box chat-application-input-box"
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
						<form className="support-chat-input-box chat-application-input-box" onSubmit={submit}>
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
		</main>
	);
}