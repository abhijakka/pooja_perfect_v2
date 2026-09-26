import { fireEvent, screen, waitFor } from "@testing-library/react";
import { renderWithProviders } from "../../../store/test-utils";
import SignupPage from "./page";

const push = jest.fn();
jest.mock("next/navigation", () => ({ useRouter: () => ({ push: (...args: string[]) => push(...args) }) }));
jest.mock("../../../hooks/useCart", () => ({ useCart: () => ({ count: 0 }) }));
jest.mock("../../../hooks/useWishlist", () => ({ useWishlist: () => ({ count: 0 }) }));
jest.mock("../../../components/layout/PublicHeader/PublicHeader", () => ({ PublicHeader: () => <header>Header</header> }));
jest.mock("../../../components/layout/PublicFooter/PublicFooter", () => ({ PublicFooter: () => <footer>Footer</footer> }));

const signInWithGoogle = jest.fn();
jest.mock("../../../hooks/useGoogleAuth", () => ({
	useGoogleAuth: () => ({ isBusy: false, signInWithGoogle: (...args: unknown[]) => signInWithGoogle(...args) }),
}));

const CUSTOMER = { id: "u1", first_name: "Pooja", last_name: "Sharma", email: "pooja@example.com", role_name: "customer" };

describe("SignupPage", () => {
  beforeEach(() => {
    push.mockReset();
    signInWithGoogle.mockReset();
  });

  it("renders the sign-up form", () => {
    renderWithProviders(<SignupPage />);
    expect(screen.getByRole("heading", { name: "Create your account" })).toBeInTheDocument();
    expect(screen.getByLabelText("First name")).toBeInTheDocument();
    expect(screen.getByLabelText("Email address")).toBeInTheDocument();
  });

  it("starts a Google sign-up instead of showing a placeholder message", () => {
    renderWithProviders(<SignupPage />);
    fireEvent.click(screen.getByRole("button", { name: /continue with google/i }));
    expect(signInWithGoogle).toHaveBeenCalledTimes(1);
    expect(screen.queryByText(/ready to connect/i)).not.toBeInTheDocument();
  });

  it("authenticates and lands a new Google customer on the homepage", async () => {
    signInWithGoogle.mockResolvedValue(CUSTOMER);
    renderWithProviders(<SignupPage />);
    fireEvent.click(screen.getByRole("button", { name: /continue with google/i }));
    await waitFor(() => expect(screen.getByText(/welcome to poojapoint/i)).toBeInTheDocument());
    // Already authenticated, so it must not bounce back to /login.
    await waitFor(() => expect(push).toHaveBeenCalledWith("/"), { timeout: 2000 });
    expect(push).not.toHaveBeenCalledWith("/login");
  });

  it("lands a Google admin on the admin area", async () => {
    signInWithGoogle.mockResolvedValue({ ...CUSTOMER, role_name: "admin" });
    renderWithProviders(<SignupPage />);
    fireEvent.click(screen.getByRole("button", { name: /continue with google/i }));
    await waitFor(() => expect(push).toHaveBeenCalledWith("/admin"), { timeout: 2000 });
  });

  it("stays on the page and does not redirect when Google sign-up fails", async () => {
    signInWithGoogle.mockResolvedValue(null);
    renderWithProviders(<SignupPage />);
    fireEvent.click(screen.getByRole("button", { name: /continue with google/i }));
    await waitFor(() => expect(signInWithGoogle).toHaveBeenCalled());
    expect(push).not.toHaveBeenCalled();
  });
});
