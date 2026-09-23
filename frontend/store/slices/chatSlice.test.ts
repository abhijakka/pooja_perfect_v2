import chatReducer, {
	openChat,
	closeChat,
	appendMessage,
	setBooting,
	setSending,
	setConversation,
	setGuestName,
	setGuestEmail,
	setGuestStep,
	replaceMessages,
	resetChat,
	setChatError,
} from "./chatSlice";

describe("chatSlice", () => {
	it("opens and closes the chat", () => {
		let state = chatReducer(undefined, openChat());
		expect(state.open).toBe(true);
		expect(state.unread).toBe(false);
		state = chatReducer(state, closeChat());
		expect(state.open).toBe(false);
	});

	it("appends a message and dedupes by id", () => {
		const message = { id: "msg-1", author: "customer" as const, text: "Hi", time: "10:00" };
		let state = chatReducer(undefined, appendMessage(message));
		expect(state.messages).toHaveLength(1);
		expect(state.messages[0]).toEqual(message);
		state = chatReducer(state, appendMessage(message));
		expect(state.messages).toHaveLength(1);
	});

	it("marks unread when a message arrives while closed", () => {
		const state = chatReducer(
			chatReducer(undefined, closeChat()),
			appendMessage({ id: "a", author: "admin", text: "Hello", time: "10:00" }),
		);
		expect(state.unread).toBe(true);
	});

	it("tracks booting and sending flags", () => {
		let state = chatReducer(undefined, setBooting(true));
		expect(state.booting).toBe(true);
		state = chatReducer(state, setBooting(false));
		expect(state.booting).toBe(false);
		state = chatReducer(state, setSending(true));
		expect(state.sending).toBe(true);
	});

	it("sets the conversation and its ended status", () => {
		const state = chatReducer(undefined, setConversation({ id: "conv-1", ended: true }));
		expect(state.conversationId).toBe("conv-1");
		expect(state.ended).toBe(true);
	});

	it("stores guest identity and step", () => {
		let state = chatReducer(undefined, setGuestStep("name"));
		expect(state.guestStep).toBe("name");
		state = chatReducer(state, setGuestName("Ravi"));
		state = chatReducer(state, setGuestEmail("ravi@example.com"));
		state = chatReducer(state, setGuestStep("done"));
		expect(state.guestName).toBe("Ravi");
		expect(state.guestEmail).toBe("ravi@example.com");
		expect(state.guestStep).toBe("done");
	});

	it("replaces the full message list", () => {
		const state = chatReducer(
			chatReducer(undefined, appendMessage({ id: "1", author: "admin", text: "old", time: "" })),
			replaceMessages([{ id: "2", author: "customer", text: "new", time: "" }]),
		);
		expect(state.messages).toHaveLength(1);
		expect(state.messages[0].text).toBe("new");
	});

	it("stores an error and resets all chat UI state", () => {
		let state = chatReducer(
			chatReducer(chatReducer(undefined, openChat()), setChatError("boom")),
			setConversation({ id: "conv", ended: false }),
		);
		state = chatReducer(state, appendMessage({ id: "9", author: "admin", text: "x", time: "" }));
		expect(state.error).toBe("boom");
		state = chatReducer(state, resetChat());
		expect(state.open).toBe(true);
		expect(state.conversationId).toBe(null);
		expect(state.messages).toHaveLength(0);
		expect(state.error).toBe(null);
		expect(state.guestStep).toBe("none");
	});
});