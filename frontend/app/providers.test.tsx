import { fireEvent, render, screen, waitFor } from "@testing-library/react";

const replace = jest.fn();
jest.mock("next/navigation", () => ({ useRouter: () => ({ replace, push: jest.fn() }) }));

jest.mock("../hooks/useVisitorTracking", () => ({ useVisitorTracking: jest.fn() }));

jest.mock("../context/ChatContext", () => ({
	ChatProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
	useChat: jest.fn(),
}));

jest.mock("../components/chat/SupportChat", () => ({ SupportChat: () => null }));

const me = jest.fn();
jest.mock("../services/api/auth.api", () => ({
	authApi: { me: (...args: unknown[]) => me(...args), refresh: jest.fn() },
}));

const cartGet = jest.fn().mockResolvedValue({ cart: null });
jest.mock("../services/api/cart.api", () => ({
	cartApi: { get: (...args: unknown[]) => cartGet(...args) },
	toCartItems: jest.fn().mockReturnValue([]),
}));

import Providers from "./providers";
import { useAppDispatch } from "../store/hooks";
import { setUser } from "../store/slices/authSlice";

/**
 * `Providers` creates the Redux <Provider> itself, so any `useSelector`/`useDispatch`
 * called in its own body would run with no store in context and react-redux v9 throws
 * "could not find react-redux context value". This renders the real tree to prove the
 * store-aware hooks all live below <Provider>.
 */
describe("Providers", () => {
	beforeEach(() => {
		replace.mockClear();
		me.mockReset();
		cartGet.mockClear();
		cartGet.mockResolvedValue({ cart: null });
	});

	it("renders without a redux context error and hydrates auth readiness", async () => {
		me.mockResolvedValue({
			id: "u1",
			first_name: "Ada",
			last_name: "L",
			email: "ada@example.com",
			role_name: "customer",
			expires_at: new Date(Date.now() + 1_800_000).toISOString(),
		});

		expect(() => render(<Providers>{<span>app shell</span>}</Providers>)).not.toThrow();

		expect(screen.getByText("app shell")).toBeInTheDocument();
		await waitFor(() => expect(me).toHaveBeenCalledTimes(1));
	});

	it("keeps an anonymous visitor on the current page when /auth/me returns 401", async () => {
		const { ApiError } = await import("../services/api/client");
		me.mockRejectedValue(new ApiError(401, "Not authenticated"));

		render(<Providers>{<span>public page</span>}</Providers>);

		expect(screen.getByText("public page")).toBeInTheDocument();
		await waitFor(() => expect(me).toHaveBeenCalled());
		expect(replace).not.toHaveBeenCalled();
	});

	it("re-reads the backend cart when the visitor signs in", async () => {
		// /auth/me settles as an anonymous guest. A later sign-in must re-read the cart,
		// because the backend resolves a different one for a customer than for a guest token.
		const { ApiError } = await import("../services/api/client");
		me.mockRejectedValue(new ApiError(401, "Not authenticated"));

		function SignIn() {
			const dispatch = useAppDispatch();
			return (
				<button
					type="button"
					onClick={() =>
						dispatch(
							setUser({
								id: "u1",
								first_name: "Ada",
								last_name: "L",
								email: "ada@example.com",
								role_name: "customer",
							} as never),
						)
					}
				>
					sign in
				</button>
			);
		}

		render(
			<Providers>
				<SignIn />
			</Providers>,
		);

		// Let /auth/me settle so the baseline (guest) cart read has finished.
		await waitFor(() => expect(me).toHaveBeenCalled());
		await waitFor(() => expect(cartGet.mock.calls.length).toBeGreaterThan(0));
		const beforeSignIn = cartGet.mock.calls.length;

		fireEvent.click(screen.getByText("sign in"));

		await waitFor(() =>
			expect(cartGet.mock.calls.length).toBeGreaterThan(beforeSignIn),
		);
	});
});
