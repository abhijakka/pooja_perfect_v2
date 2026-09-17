import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

export type ChatMessage = { id: number; author: "admin" | "customer"; text: string; time: string };

type ChatState = { open: boolean; messages: ChatMessage[]; typing: boolean; unread: boolean };

const initialMessages: ChatMessage[] = [
	{ id: 1, author: "admin", text: "Hi! Welcome to PoojaPoint. How can we help you today?", time: "Support · 10:32 AM" },
	{ id: 2, author: "customer", text: "Hi, I need help finding a pooja gift under ₹1000.", time: "You · 10:33 AM" },
	{ id: 3, author: "admin", text: "Of course! We have several beautiful options under ₹1000. I will help you find the best one.", time: "Support · 10:34 AM" },
];

const initialState: ChatState = { open: false, messages: initialMessages, typing: false, unread: true };

export function replyFor(text: string): string {
	const message = text.toLowerCase();
	if (message.includes("gift")) return "Absolutely! We can help you choose a beautiful pooja gift. What is your preferred budget?";
	if (message.includes("order")) return "Sure! Please share your order number and we will check the current status for you.";
	if (message.includes("delivery")) return "Sure. Please share your PIN code and we will help you with delivery information.";
	return "Thanks for your message! Our PoojaPoint support team can help with products, orders, payments and delivery.";
}

const chatSlice = createSlice({
	name: "chat",
	initialState,
	reducers: {
		openChat: (state) => {
			state.open = true;
			state.unread = false;
		},
		closeChat: (state) => {
			state.open = false;
		},
		appendMessage: (state, action: PayloadAction<ChatMessage>) => {
			state.messages.push(action.payload);
		},
		setTyping: (state, action: PayloadAction<boolean>) => {
			state.typing = action.payload;
		},
	},
});

export const { openChat, closeChat, appendMessage, setTyping } = chatSlice.actions;
export default chatSlice.reducer;