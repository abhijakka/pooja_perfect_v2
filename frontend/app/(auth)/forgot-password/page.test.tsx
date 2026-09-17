import { render, screen } from "@testing-library/react";
import ForgotPasswordPage from "./page";

jest.mock("next/navigation", () => ({ useRouter: () => ({ push: jest.fn() }) }));
jest.mock("../../../hooks/useCart", () => ({ useCart: () => ({ count: 0 }) }));
jest.mock("../../../hooks/useWishlist", () => ({ useWishlist: () => ({ count: 0 }) }));
jest.mock("../../../components/layout/PublicHeader/PublicHeader", () => ({ PublicHeader: () => <header>Header</header> }));
jest.mock("../../../components/layout/PublicFooter/PublicFooter", () => ({ PublicFooter: () => <footer>Footer</footer> }));

describe("ForgotPasswordPage", () => {
  it("renders the recovery form", () => {
    render(<ForgotPasswordPage />);
    expect(screen.getByRole("heading", { name: "Forgot password?" })).toBeInTheDocument();
    expect(screen.getByLabelText("Email or mobile number")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /send recovery link/i })).toBeInTheDocument();
  });
});
