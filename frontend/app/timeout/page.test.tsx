import { render, screen } from "@testing-library/react";
import ServerTimeoutPage from "./page";

jest.mock("../../hooks/useCart", () => ({ useCart: () => ({ count: 0 }) }));
jest.mock("../../hooks/useWishlist", () => ({ useWishlist: () => ({ count: 0 }) }));
jest.mock("../../components/layout/PublicHeader/PublicHeader", () => ({ PublicHeader: () => <header>Header</header> }));
jest.mock("../../components/layout/PublicFooter/PublicFooter", () => ({ PublicFooter: () => <footer>Footer</footer> }));

describe("ServerTimeoutPage", () => {
  it("renders the timeout page", () => {
    render(<ServerTimeoutPage />);
    expect(screen.getByRole("heading", { name: "The server took too long." })).toBeInTheDocument();
  });
});