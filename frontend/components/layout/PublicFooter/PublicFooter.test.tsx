import { render, screen } from "@testing-library/react";
import { PublicFooter } from "./PublicFooter";
import { useChat } from "../../../hooks/useChat";

jest.mock("../../../hooks/useChat", () => ({ useChat: jest.fn() }));

(useChat as jest.Mock).mockReturnValue({ openChat: jest.fn() });

describe("PublicFooter", () => {
  it("renders footer with links and bottom nav", () => {
    render(
      <PublicFooter
        activeNav="home"
        wishlistCount={1}
        cartCount={2}
        onNavChange={jest.fn()}
        onWishlist={jest.fn()}
        onProfile={jest.fn()}
      />
    );
    expect(screen.getByText("PoojaPoint")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Pooja Products" })).toHaveAttribute("href", "/products");
    expect(screen.getByRole("navigation", { name: "Mobile navigation" })).toBeInTheDocument();
  });
});