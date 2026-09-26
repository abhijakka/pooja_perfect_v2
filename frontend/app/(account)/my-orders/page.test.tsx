import { render, screen, waitFor } from "@testing-library/react";
import OrdersPage from "./page";

jest.mock("../../../services/api/account.api", () => ({ accountApi: { getOverview: () => Promise.resolve({ currentUser: {}, addresses: [], orders: { items: [{ id: "1", orderNumber: "PP-BACKEND-001", status: "processing", total: 100, createdAt: "2026-08-19T00:00:00Z", items: [{ productId: "1", productName: "Backend Diya", quantity: 1, unitPrice: 100 }] }] } }) } }));

jest.mock("next/navigation", () => ({ useRouter: () => ({ push: jest.fn() }) }));
jest.mock("../../../hooks/useCart", () => ({ useCart: () => ({ count: 0, addItem: jest.fn() }) }));
jest.mock("../../../hooks/useWishlist", () => ({ useWishlist: () => ({ count: 0 }) }));
jest.mock("../../../components/layout/PublicHeader/PublicHeader", () => ({ PublicHeader: () => <header>Header</header> }));
jest.mock("../../../components/layout/PublicFooter/PublicFooter", () => ({ PublicFooter: () => <footer>Footer</footer> }));

describe("OrdersPage", () => {
  it("renders the order list", async () => {
    render(<OrdersPage />);
    expect(screen.getByRole("heading", { name: "My Orders" })).toBeInTheDocument();
    await waitFor(() => expect(screen.getByText("PP-BACKEND-001")).toBeInTheDocument());
  }, 15000);
});