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

describe("SupportChat", () => {
  beforeEach(() => {
    mockUsePathname.mockReturnValue("/");
    mockUseChat.mockReturnValue({
      open: false,
      messages: [],
      typing: false,
      unread: 1,
      openChat: jest.fn(),
      closeChat: jest.fn(),
      send: jest.fn(),
    });
  });

  it("renders the launcher and opens the chat", () => {
    render(<SupportChat />);
    const launcher = screen.getByRole("button", { name: "Open customer support" });
    fireEvent.click(launcher);
    expect(mockUseChat.mock.results[0].value.openChat).toHaveBeenCalled();
  });

  it("renders messages and sends a draft", () => {
    const send = jest.fn();
    mockUseChat.mockReturnValue({
      open: true,
      messages: [{ id: "1", author: "admin", text: "Namaste!", time: "10:00" }],
      typing: false,
      unread: 0,
      openChat: jest.fn(),
      closeChat: jest.fn(),
      send,
    });
    render(<SupportChat />);
    expect(screen.getByText("Namaste!")).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText("Message support"), {
      target: { value: "hello" },
    });
    fireEvent.click(screen.getByLabelText("Send message"));
    expect(send).toHaveBeenCalledWith("hello");
  });

  it("renders nothing on admin pages", () => {
    mockUsePathname.mockReturnValue("/admin");
    const { container } = render(<SupportChat />);
    expect(container).toBeEmptyDOMElement();
  });
});