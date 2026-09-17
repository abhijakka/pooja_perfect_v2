import { render, screen } from "@testing-library/react";
import CartPage from "./page";

jest.mock("../../../hooks/useCart", () => ({
  useCart: () => ({ items: [], count: 0, total: 0, updateQuantity: jest.fn(), removeItem: jest.fn(), clearCart: jest.fn(), addItem: jest.fn() }),
}));
jest.mock("../../../hooks/useWishlist", () => ({ useWishlist: () => ({ items: [], count: 0, toggle: jest.fn() }) }));
jest.mock("../../../components/layout/PublicHeader/PublicHeader", () => ({ PublicHeader: () => <header>Header</header> }));
jest.mock("../../../components/layout/PublicFooter/PublicFooter", () => ({ PublicFooter: () => <footer>Footer</footer> }));

describe("CartPage", () => {
  it("renders the empty cart", () => {
    render(<CartPage />);
    expect(screen.getByRole("heading", { name: "Your Cart" })).toBeInTheDocument();
    expect(screen.getAllByText("Your cart is empty").length).toBeGreaterThan(0);
  });
});