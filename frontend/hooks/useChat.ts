import { useCallback } from "react";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import { openChat, closeChat, appendMessage, setTyping, replyFor } from "../store/slices/chatSlice";

export function useChat() {
	const dispatch = useAppDispatch();
	const { open, messages, typing, unread } = useAppSelector((state) => state.chat);

	const send = useCallback((text: string) => {
		const clean = text.trim();
		if (!clean) return;
		dispatch(appendMessage({ id: Date.now(), author: "customer", text: clean, time: "You · Just now" }));
		dispatch(setTyping(true));
		window.setTimeout(() => {
			dispatch(setTyping(false));
			dispatch(appendMessage({ id: Date.now() + 1, author: "admin", text: replyFor(clean), time: "Support · Just now" }));
		}, 1200);
	}, [dispatch]);

	return {
		open,
		messages,
		typing,
		unread,
		openChat: useCallback(() => dispatch(openChat()), [dispatch]),
		closeChat: useCallback(() => dispatch(closeChat()), [dispatch]),
		send,
	};
}
