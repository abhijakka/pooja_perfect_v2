import { render, screen } from "@testing-library/react";
import OtpPage from "./page";

jest.mock("next/navigation", () => ({ useRouter: () => ({ push: jest.fn() }) }));
jest.mock("../../../hooks/useCart", () => ({ useCart: () => ({ count: 0 }) }));
jest.mock("../../../hooks/useWishlist", () => ({ useWishlist: () => ({ count: 0 }) }));
jest.mock("../../../components/layout/PublicHeader/PublicHeader", () => ({ PublicHeader: () => <header>Header</header> }));
jest.mock("../../../components/layout/PublicFooter/PublicFooter", () => ({ PublicFooter: () => <footer>Footer</footer> }));

describe("OtpPage", () => {
  it("renders the OTP verification form", () => {
    render(<OtpPage />);
    expect(screen.getByRole("heading", { name: "Verify your account" })).toBeInTheDocument();
    expect(screen.getAllByRole("textbox")).toHaveLength(6);
  });
});