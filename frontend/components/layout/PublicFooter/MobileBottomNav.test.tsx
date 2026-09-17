import { render, screen, fireEvent } from "@testing-library/react";
import { MobileBottomNav } from "./MobileBottomNav";
import { useChat } from "../../../hooks/useChat";

jest.mock("../../../hooks/useChat", () => ({ useChat: jest.fn() }));

const mockUseChat = useChat as jest.Mock;

describe("MobileBottomNav", () => {
  beforeEach(() => {
    mockUseChat.mockReturnValue({ openChat: jest.fn() });
  });

  it("renders nav items and badges", () => {
    render(
      <MobileBottomNav
        activeNav="home"
        wishlistCount={2}
        cartCount={3}
        onNavChange={jest.fn()}
        onWishlist={jest.fn()}
        onProfile={jest.fn()}
      />
    );
    expect(screen.getByRole("navigation", { name: "Mobile navigation" })).toBeInTheDocument();
    expect(screen.getByText("Home")).toBeInTheDocument();
    expect(screen.getByText("2")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
  });

  it("calls onWishlist and openChat on nav clicks", () => {
    const onWishlist = jest.fn();
    const onNavChange = jest.fn();
    const openChat = jest.fn();
    mockUseChat.mockReturnValue({ openChat });
    render(
      <MobileBottomNav
        activeNav="home"
        wishlistCount={1}
        cartCount={0}
        onNavChange={onNavChange}
        onWishlist={onWishlist}
        onProfile={jest.fn()}
      />
    );
    fireEvent.click(screen.getByText("Wishlist"));
    expect(onWishlist).toHaveBeenCalled();
    expect(onNavChange).toHaveBeenCalledWith("wishlist");
    fireEvent.click(screen.getByText("Support"));
    expect(openChat).toHaveBeenCalled();
  });
});