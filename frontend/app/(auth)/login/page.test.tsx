import { fireEvent, screen, waitFor } from "@testing-library/react";
import { renderWithProviders } from "../../../store/test-utils";
import LoginPage from "./page";

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

describe("LoginPage", () => {
  beforeEach(() => {
    push.mockReset();
    signInWithGoogle.mockReset();
  });

  it("renders the sign-in form", () => {
    renderWithProviders(<LoginPage />);
    expect(screen.getByRole("heading", { name: "Sign in" })).toBeInTheDocument();
    expect(screen.getByLabelText("Email or mobile number")).toBeInTheDocument();
    expect(screen.getByLabelText("Password")).toBeInTheDocument();
  });

  it("starts a Google sign-in instead of showing a placeholder message", () => {
    renderWithProviders(<LoginPage />);
    fireEvent.click(screen.getByRole("button", { name: /continue with google/i }));
    expect(signInWithGoogle).toHaveBeenCalledTimes(1);
    expect(screen.queryByText(/ready to connect/i)).not.toBeInTheDocument();
  });

  it("lands a Google customer on the homepage", async () => {
    signInWithGoogle.mockResolvedValue(CUSTOMER);
    renderWithProviders(<LoginPage />);
    fireEvent.click(screen.getByRole("button", { name: /continue with google/i }));
    await waitFor(() => expect(screen.getByText(/welcome back to poojapoint/i)).toBeInTheDocument());
    await waitFor(() => expect(push).toHaveBeenCalledWith("/"), { timeout: 2000 });
  });

  it("lands a Google admin on the admin area", async () => {
    signInWithGoogle.mockResolvedValue({ ...CUSTOMER, role_name: "admin" });
    renderWithProviders(<LoginPage />);
    fireEvent.click(screen.getByRole("button", { name: /continue with google/i }));
    await waitFor(() => expect(push).toHaveBeenCalledWith("/admin"), { timeout: 2000 });
  });

  it("stays on the page and does not redirect when Google sign-in fails", async () => {
    signInWithGoogle.mockResolvedValue(null);
    renderWithProviders(<LoginPage />);
    fireEvent.click(screen.getByRole("button", { name: /continue with google/i }));
    await waitFor(() => expect(signInWithGoogle).toHaveBeenCalled());
    expect(push).not.toHaveBeenCalled();
  });
});
