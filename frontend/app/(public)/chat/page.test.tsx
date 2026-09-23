import { render, screen } from "@testing-library/react";
import ChatPage from "./page";

const mockOpenChat = jest.fn();

jest.mock("../../../hooks/useChat", () => ({
  useChat: () => ({
    open: true,
    booting: false,
    loadingMessages: false,
    sending: false,
    error: null,
    conversationId: "conv-1",
    guestName: "",
    guestEmail: "",
    guestStep: "done",
    ended: false,
    messages: [],
    unread: false,
    openChat: mockOpenChat,
    closeChat: jest.fn(),
    send: jest.fn(),
    endChat: jest.fn(),
    newChat: jest.fn(),
    submitGuestName: jest.fn(),
    submitGuestEmail: jest.fn(),
    clearError: jest.fn(),
  }),
}));

describe("ChatPage", () => {
  beforeEach(() => {
    mockOpenChat.mockClear();
  });

  it("renders the full-page chat application", () => {
    render(<ChatPage />);
    expect(screen.getByLabelText("Message support")).toBeInTheDocument();
    expect(mockOpenChat).toHaveBeenCalled();
  });
});