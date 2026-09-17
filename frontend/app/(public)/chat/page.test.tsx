import { render, screen } from "@testing-library/react";
import ChatPage from "./page";

jest.mock("../../../hooks/useChat", () => ({ useChat: () => ({ openChat: jest.fn() }) }));

describe("ChatPage", () => {
  it("renders the chat page", () => {
    render(<ChatPage />);
    expect(screen.getByRole("heading", { name: "Chat with PoojaPoint Support" })).toBeInTheDocument();
  });
});