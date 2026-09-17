import { render, screen } from "@testing-library/react";
import WishlistPage from "./page";

jest.mock("next/navigation", () => ({ useRouter: () => ({ push: jest.fn() }) }));
jest.mock("../../../hooks/useWishlist", () => ({
  useWishlist: () => ({ items: [], count: 0, add: jest.fn(), remove: jest.fn() }),
}));
jest.mock("../../../hooks/useCart", () => ({
  useCart: () => ({ count: 0, addItem: jest.fn() }),
}));
jest.mock("../../../components/layout/PublicHeader/PublicHeader", () => ({ PublicHeader: () => <header>Header</header> }));
jest.mock("../../../components/layout/PublicFooter/PublicFooter", () => ({ PublicFooter: () => <footer>Footer</footer> }));

describe("WishlistPage", () => {
  it("renders the empty wishlist", () => {
    render(<WishlistPage />);
    expect(screen.getByRole("heading", { name: "Your Wishlist" })).toBeInTheDocument();
    expect(screen.getByText("Your wishlist is waiting")).toBeInTheDocument();
  });
});