import { render, screen, waitFor } from "@testing-library/react";
import { Provider } from "react-redux";
import AccountPage from "./page";
import { makeStore } from "../../../store";

jest.mock("../../../services/api/account.api", () => ({ accountApi: { getOverview: () => Promise.resolve({ current_user: { first_name: "Abhinav", last_name: "Sharma", email: "abhinav@example.com", phone: "+91 98765 43210", created_at: "2026-08-01", status: "active" }, addresses: [], orders: { items: [] } }) } }));

jest.mock("next/navigation", () => ({ useRouter: () => ({ push: jest.fn() }) }));
jest.mock("../../../hooks/useCart", () => ({ useCart: () => ({ count: 0 }) }));
jest.mock("../../../hooks/useWishlist", () => ({ useWishlist: () => ({ count: 0 }) }));
jest.mock("../../../components/layout/PublicHeader/PublicHeader", () => ({ PublicHeader: () => <header>Header</header> }));
jest.mock("../../../components/layout/PublicFooter/PublicFooter", () => ({ PublicFooter: () => <footer>Footer</footer> }));

describe("AccountPage", () => {
  it("renders the account dashboard", async () => {
    render(<Provider store={makeStore()}><AccountPage /></Provider>);
    await waitFor(() => expect(screen.getByRole("heading", { name: "Abhinav Sharma" })).toBeInTheDocument());
    expect(screen.getAllByText("abhinav@example.com").length).toBeGreaterThan(0);
  });
});