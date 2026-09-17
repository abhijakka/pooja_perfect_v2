"use client";

import { useEffect, useRef, useState, useSyncExternalStore } from "react";
import { usePathname } from "next/navigation";
import { Icon } from "../Icon";
import { useChat } from "../../hooks/useChat";

export function SupportChat() {
	const pathname = usePathname();
	const { open, messages, typing, unread, openChat, closeChat, send } = useChat();
	const mounted = useSyncExternalStore(() => () => undefined, () => true, () => false);
	const [draft, setDraft] = useState("");
	const bodyRef = useRef<HTMLDivElement>(null);
	const inputRef = useRef<HTMLInputElement>(null);

	useEffect(() => {
		if (!open) return;
		inputRef.current?.focus();
		bodyRef.current?.scrollTo({ top: bodyRef.current.scrollHeight });
	}, [open, messages.length, typing]);

	useEffect(() => {
		const closeOnEscape = (event: KeyboardEvent) => {
			if (event.key === "Escape") closeChat();
		};
		window.addEventListener("keydown", closeOnEscape);
		return () => window.removeEventListener("keydown", closeOnEscape);
	}, [closeChat]);

	const submit = (event: React.FormEvent<HTMLFormElement>) => {
		event.preventDefault();
		if (!draft.trim()) return;
		send(draft);
		setDraft("");
	};
	if (!mounted || pathname.startsWith("/admin")) return null;

	return <>
		<button className="support-chat-launcher" onClick={open ? closeChat : openChat} aria-label={open ? "Close customer support" : "Open customer support"}>
			<Icon name="chat" />
			{unread && !open && <span className="support-chat-notification">1</span>}
		</button>
		<section className={`support-chat-window ${open ? "open" : ""}`} aria-label="PoojaPoint customer support" aria-hidden={!open}>
			<header className="support-chat-header"><div className="support-chat-admin"><div className="support-chat-avatar">PP<span /></div><div><strong>PoojaPoint Support</strong><span><i /> Online · Usually replies quickly</span></div></div><button className="support-chat-close" onClick={closeChat} aria-label="Close chat">×</button></header>
			<div className="support-chat-body" ref={bodyRef} aria-live="polite"><div className="support-chat-date">TODAY</div>{messages.map((message) => <div className={`support-chat-message ${message.author}`} key={message.id}><div className="support-chat-message-content"><div className="support-chat-bubble">{message.text}</div><div className="support-chat-time">{message.time}</div></div></div>)}{typing && <div className="support-chat-message admin"><div className="support-chat-typing"><span /><span /><span /></div></div>}</div>
			<footer className="support-chat-footer"><form className="support-chat-input-box" onSubmit={submit}><input ref={inputRef} className="support-chat-input" value={draft} onChange={(event) => setDraft(event.target.value)} placeholder="Type your message..." autoComplete="off" aria-label="Message support" /><button className="support-chat-send" type="submit" aria-label="Send message"><Icon name="arrow-right" /></button></form><div className="support-chat-note">PoojaPoint Support · Your conversation is private</div></footer>
		</section>
	</>;
}
