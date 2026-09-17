import { render, screen } from "@testing-library/react";
import CheckoutPage from "./page";

jest.mock("next/navigation", () => ({ useRouter: () => ({ push: jest.fn() }) }));
jest.mock("../../../hooks/useCart", () => ({
  useCart: () => ({ items: [], count: 0, total: 0, clearCart: jest.fn() }),
}));
jest.mock("../../../hooks/useWishlist", () => ({ useWishlist: () => ({ count: 0 }) }));
jest.mock("../../../components/layout/PublicHeader/PublicHeader", () => ({ PublicHeader: () => <header>Header</header> }));
jest.mock("../../../components/layout/PublicFooter/PublicFooter", () => ({ PublicFooter: () => <footer>Footer</footer> }));

describe("CheckoutPage", () => {
  it("renders the checkout form", () => {
    render(<CheckoutPage />);
    expect(screen.getByRole("heading", { name: "Checkout" })).toBeInTheDocument();
  });
});