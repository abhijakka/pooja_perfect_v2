import { render, screen } from "@testing-library/react";
import ServiceUnavailablePage from "./page";

jest.mock("../../hooks/useCart", () => ({ useCart: () => ({ count: 0 }) }));
jest.mock("../../hooks/useWishlist", () => ({ useWishlist: () => ({ count: 0 }) }));
jest.mock("../../components/layout/PublicHeader/PublicHeader", () => ({ PublicHeader: () => <header>Header</header> }));
jest.mock("../../components/layout/PublicFooter/PublicFooter", () => ({ PublicFooter: () => <footer>Footer</footer> }));

describe("ServiceUnavailablePage", () => {
  it("renders the 503 page", () => {
    render(<ServiceUnavailablePage />);
    expect(screen.getByRole("heading", { name: "Service unavailable." })).toBeInTheDocument();
  });
});