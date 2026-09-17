import chatReducer, { openChat, closeChat, appendMessage, setTyping, replyFor } from "./chatSlice";

describe("chatSlice", () => {
  it("opens and closes the chat", () => {
    let state = chatReducer(undefined, openChat());
    expect(state.open).toBe(true);
    expect(state.unread).toBe(false);
    state = chatReducer(state, closeChat());
    expect(state.open).toBe(false);
  });

  it("appends a message", () => {
    const message = { id: 4, author: "customer" as const, text: "Hi", time: "You · Just now" };
    const state = chatReducer(undefined, appendMessage(message));
    expect(state.messages).toHaveLength(4);
    expect(state.messages[3]).toEqual(message);
  });

  it("sets typing state", () => {
    const state = chatReducer(undefined, setTyping(true));
    expect(state.typing).toBe(true);
  });

  it("replyFor returns a relevant reply", () => {
    expect(replyFor("I need a gift")).toContain("budget");
    expect(replyFor("where is my order")).toContain("order number");
    expect(replyFor("delivery time")).toContain("PIN code");
    expect(replyFor("hello")).toContain("PoojaPoint support team");
  });
});