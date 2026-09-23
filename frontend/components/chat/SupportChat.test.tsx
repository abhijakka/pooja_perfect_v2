import { render, screen, fireEvent } from "@testing-library/react";
import { SupportChat } from "./SupportChat";
import { useChat } from "../../hooks/useChat";
import { usePathname } from "next/navigation";

jest.mock("../../hooks/useChat", () => ({ useChat: jest.fn() }));
jest.mock("next/navigation", () => ({ usePathname: jest.fn() }));

beforeAll(() => {
  Element.prototype.scrollTo = jest.fn();
});

const mockUseChat = useChat as jest.Mock;
const mockUsePathname = usePathname as jest.Mock;

const baseChat = {
  open: false,
  messages: [],
  sending: false,
  booting: false,
  error: null,
  conversationId: "conv-1",
  guestStep: "done",
  guestName: "",
  guestEmail: "",
  ended: false,
  unread: false,
  openChat: jest.fn(),
  closeChat: jest.fn(),
  send: jest.fn(),
  endChat: jest.fn(),
  newChat: jest.fn(),
  submitGuestName: jest.fn(),
  submitGuestEmail: jest.fn(),
  clearError: jest.fn(),
};

describe("SupportChat", () => {
  beforeEach(() => {
    mockUsePathname.mockReturnValue("/");
    mockUseChat.mockReturnValue({ ...baseChat });
  });

  it("renders the launcher and opens the chat", () => {
    render(<SupportChat />);
    const launcher = screen.getByRole("button", { name: "Open customer support" });
    fireEvent.click(launcher);
    expect(mockUseChat.mock.results[0].value.openChat).toHaveBeenCalled();
  });

  it("renders messages and sends a draft", () => {
    mockUseChat.mockReturnValue({
      ...baseChat,
      open: true,
      messages: [{ id: "1", author: "admin", text: "Namaste!", time: "10:00" }],
    });
    render(<SupportChat />);
    expect(screen.getByText("Namaste!")).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText("Message support"), {
      target: { value: "hello" },
    });
    fireEvent.click(screen.getByLabelText("Send message"));
    expect(baseChat.send).toHaveBeenCalledWith("hello");
  });

  it("walks a guest through name and email", () => {
    mockUseChat.mockReturnValue({
      ...baseChat,
      open: true,
      conversationId: null,
      guestStep: "name",
    });
    render(<SupportChat />);
    expect(screen.getByText(/May I know your name\?/)).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText("Your name"), { target: { value: "Ravi" } });
    fireEvent.click(screen.getByLabelText("Submit name"));
    expect(baseChat.submitGuestName).toHaveBeenCalledWith("Ravi");
  });

  it("shows the ended state and disables the composer", () => {
    mockUseChat.mockReturnValue({ ...baseChat, open: true, ended: true });
    render(<SupportChat />);
    expect(screen.getByRole("status")).toBeInTheDocument();
    expect(screen.getByLabelText("Message support")).toBeDisabled();
  });

  it("marks the chat unread as a notification", () => {
    mockUseChat.mockReturnValue({ ...baseChat, open: false, unread: true });
    render(<SupportChat />);
    expect(screen.getByText("1")).toBeInTheDocument();
  });

  it("renders nothing on admin pages", () => {
    mockUsePathname.mockReturnValue("/admin");
    const { container } = render(<SupportChat />);
    expect(container).toBeEmptyDOMElement();
  });

  it("renders nothing on the full chat page", () => {
    mockUsePathname.mockReturnValue("/chat");
    const { container } = render(<SupportChat />);
    expect(container).toBeEmptyDOMElement();
  });
});