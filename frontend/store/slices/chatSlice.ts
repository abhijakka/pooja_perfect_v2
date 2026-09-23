import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
import type { UiChatMessage } from "../../types/chat";

export type GuestStep = "none" | "name" | "email" | "done";

type ChatState = {
	open: boolean;
	booting: boolean;
	loadingMessages: boolean;
	sending: boolean;
	error: string | null;
	conversationId: string | null;
	guestName: string;
	guestEmail: string;
	guestStep: GuestStep;
	ended: boolean;
	messages: UiChatMessage[];
	unread: boolean;
};

const initialState: ChatState = {
	open: false,
	booting: false,
	loadingMessages: false,
	sending: false,
	error: null,
	conversationId: null,
	guestName: "",
	guestEmail: "",
	guestStep: "none",
	ended: false,
	messages: [],
	unread: false,
};

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
		setBooting: (state, action: PayloadAction<boolean>) => {
			state.booting = action.payload;
		},
		setLoadingMessages: (state, action: PayloadAction<boolean>) => {
			state.loadingMessages = action.payload;
		},
		setSending: (state, action: PayloadAction<boolean>) => {
			state.sending = action.payload;
		},
		setChatError: (state, action: PayloadAction<string | null>) => {
			state.error = action.payload;
		},
		setConversation: (
			state,
			action: PayloadAction<{ id: string; ended: boolean } | null>,
		) => {
			if (action.payload === null) {
				state.conversationId = null;
				state.ended = false;
				return;
			}
			state.conversationId = action.payload.id;
			state.ended = action.payload.ended;
		},
		setGuestName: (state, action: PayloadAction<string>) => {
			state.guestName = action.payload;
		},
		setGuestEmail: (state, action: PayloadAction<string>) => {
			state.guestEmail = action.payload;
		},
		setGuestStep: (state, action: PayloadAction<GuestStep>) => {
			state.guestStep = action.payload;
		},
		replaceMessages: (state, action: PayloadAction<UiChatMessage[]>) => {
			state.messages = action.payload;
		},
		appendMessage: (state, action: PayloadAction<UiChatMessage>) => {
			const incoming = action.payload;
			if (state.messages.some((message) => message.id === incoming.id)) return;
			state.messages.push(incoming);
			if (!state.open) state.unread = true;
		},
		setUnread: (state, action: PayloadAction<boolean>) => {
			state.unread = action.payload;
		},
		resetChat: (state) => {
			state.conversationId = null;
			state.ended = false;
			state.messages = [];
			state.error = null;
			state.sending = false;
			state.booting = false;
			state.loadingMessages = false;
			state.guestStep = "none";
		},
	},
});

export const {
	openChat,
	closeChat,
	setBooting,
	setLoadingMessages,
	setSending,
	setChatError,
	setConversation,
	setGuestName,
	setGuestEmail,
	setGuestStep,
	replaceMessages,
	appendMessage,
	setUnread,
	resetChat,
} = chatSlice.actions;
export default chatSlice.reducer;