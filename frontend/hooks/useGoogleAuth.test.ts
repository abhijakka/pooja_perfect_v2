import { act, waitFor } from "@testing-library/react";
import { makeStore } from "../store";
import { renderHookWithProviders } from "../store/test-utils";
import { authApi } from "../services/api/auth.api";
import { loadGoogleIdentity } from "../services/google/google-identity";
import { useGoogleAuth } from "./useGoogleAuth";

jest.mock("../services/api/auth.api", () => ({
	authApi: { googleConfig: jest.fn(), googleLogin: jest.fn(), me: jest.fn() },
}));

jest.mock("../services/google/google-identity", () => ({
	loadGoogleIdentity: jest.fn(),
}));

const configMock = authApi.googleConfig as jest.Mock;
const loginMock = authApi.googleLogin as jest.Mock;
const meMock = authApi.me as jest.Mock;
const loadMock = loadGoogleIdentity as jest.Mock;

const CLIENT_ID = "1234567890-abc.apps.googleusercontent.com";

const me = (overrides: Record<string, unknown> = {}) => ({
	id: "user-1",
	first_name: "Pooja",
	last_name: "Sharma",
	email: "pooja@example.com",
	role_name: "customer",
	...overrides,
});

/** A stand-in for `google.accounts.id` that hands back a credential immediately. */
function stubGoogle(credential: string | undefined = "google-id-token") {
	const prompt = jest.fn();
	const initialize = jest.fn((params: { callback: (r: { credential?: string }) => void }) => {
		prompt.mockImplementation(() => params.callback({ credential }));
	});
	loadMock.mockResolvedValue({ accounts: { id: { initialize, prompt, cancel: jest.fn() } } });
	return { initialize, prompt };
}

/** `renderHookWithProviders` does not hand back the store, so create one explicitly. */
function renderGoogleAuth(options: Parameters<typeof useGoogleAuth>[0] = {}) {
	const store = makeStore();
	const rendered = renderHookWithProviders(() => useGoogleAuth(options), { store });
	return { ...rendered, store };
}

describe("useGoogleAuth", () => {
	beforeEach(() => {
		jest.clearAllMocks();
		configMock.mockResolvedValue({ client_id: CLIENT_ID });
		loginMock.mockResolvedValue({
			access_token: "a",
			refresh_token: "r",
			token_type: "bearer",
			expires_at: "2030-01-01T00:00:00Z",
		});
		meMock.mockResolvedValue(me());
	});

	// A dismissal is only reported after its grace window, so one test needs
	// fake timers. Restore them even if that test throws, or every later hook
	// is left with a null `result.current`.
	afterEach(() => {
		jest.useRealTimers();
	});

	it("authenticates with the same session the password path produces", async () => {
		const google = stubGoogle();
		const onError = jest.fn();
		const { result } = renderGoogleAuth({ onError });

		let user: unknown;
		await act(async () => {
			user = await result.current.signInWithGoogle();
		});

		// The public client id is read from the backend, never hard-coded.
		expect(configMock).toHaveBeenCalledTimes(1);
		expect(google.initialize).toHaveBeenCalledWith(
			expect.objectContaining({ client_id: CLIENT_ID }),
		);
		// Only the id_token is posted; no Google profile value is forwarded.
		expect(loginMock).toHaveBeenCalledWith({
			provider: "google",
			id_token: "google-id-token",
		});
		expect(meMock).toHaveBeenCalledTimes(1);
		expect(user).toEqual(me());
		expect(onError).not.toHaveBeenCalled();
	});

	it("sets the authenticated user and the token expiry in the store", async () => {
		stubGoogle();
		const { result, store } = renderGoogleAuth();

		await act(async () => {
			await result.current.signInWithGoogle();
		});

		await waitFor(() => {
			expect(store.getState().auth.isAuthenticated).toBe(true);
		});
		expect(store.getState().auth.user).toEqual({
			id: "user-1",
			name: "Pooja Sharma",
			email: "pooja@example.com",
			role_name: "customer",
		});
		expect(store.getState().auth.accessTokenExpiresAt).toBe(
			Date.parse("2030-01-01T00:00:00Z"),
		);
	});

	it("surfaces the admin role so the caller can route to the admin area", async () => {
		stubGoogle();
		meMock.mockResolvedValue(me({ role_name: "admin" }));
		const { result, store } = renderGoogleAuth();

		await act(async () => {
			await result.current.signInWithGoogle();
		});

		await waitFor(() => {
			expect(store.getState().auth.user?.role_name).toBe("admin");
		});
		// A Google sign-in never grants admin by itself; the role is whatever the
		// backend already had on the user record.
		expect(store.getState().auth.user?.role_name).not.toBe("customer");
	});

	it("reports a rejected credential without touching the store", async () => {
		stubGoogle();
		loginMock.mockRejectedValue(new Error("Google authentication failed"));
		const onError = jest.fn();
		const { result, store } = renderGoogleAuth({ onError });

		let user: unknown = "untouched";
		await act(async () => {
			user = await result.current.signInWithGoogle();
		});

		expect(user).toBeNull();
		expect(onError).toHaveBeenCalledWith("Google sign in could not be completed. Please try again.");
		// No redirect, no logout, no partial session.
		expect(store.getState().auth.isAuthenticated).toBe(false);
		expect(store.getState().auth.user).toBeNull();
		expect(result.current.isBusy).toBe(false);
	});

	it("reports a cancelled sign-in", async () => {
		jest.useFakeTimers();
		loadMock.mockResolvedValue({
			accounts: {
				id: {
					initialize: jest.fn(),
					// Google reports a dismissed moment and no credential ever follows.
					prompt: jest.fn((n?: (v: Record<string, () => boolean>) => void) =>
						n?.({ isDismissedMoment: () => true }),
					),
					cancel: jest.fn(),
				},
			},
		});
		const onError = jest.fn();
		const { result } = renderGoogleAuth({ onError });

		let user: unknown = "untouched";
		await act(async () => {
			const attempt = result.current.signInWithGoogle();
			await jest.advanceTimersByTimeAsync(5000);
			user = await attempt;
		});

		expect(user).toBeNull();
		expect(onError).toHaveBeenCalledWith("Google sign in was cancelled.");
		expect(result.current.isBusy).toBe(false);
	});

	it("still signs in when FedCM dismisses the chooser before the credential arrives", async () => {
		// FedCM closes its account chooser the instant an account is picked and
		// Google reports that close as a dismissed moment, with the credential
		// callback arriving a tick later. Failing on the dismissal is what made a
		// successful sign-in report "cancelled" and never redirect.
		const initialize = jest.fn();
		const prompt = jest.fn((n?: (v: Record<string, () => boolean>) => void) => {
			n?.({ isDismissedMoment: () => true });
			initialize.mock.calls[0][0].callback({ credential: "google-id-token" });
		});
		loadMock.mockResolvedValue({ accounts: { id: { initialize, prompt, cancel: jest.fn() } } });
		const onError = jest.fn();
		const { result, store } = renderGoogleAuth({ onError });

		let user: unknown = null;
		await act(async () => {
			user = await result.current.signInWithGoogle();
		});

		expect(onError).not.toHaveBeenCalled();
		expect(loginMock).toHaveBeenCalledWith({ provider: "google", id_token: "google-id-token" });
		expect(user).toEqual(me());
		await waitFor(() => {
			expect(store.getState().auth.isAuthenticated).toBe(true);
		});
		expect(result.current.isBusy).toBe(false);
	});

	it("reports a disabled provider", async () => {
		loadMock.mockResolvedValue({
			accounts: {
				id: {
					initialize: jest.fn(),
					prompt: jest.fn((n?: (v: Record<string, () => boolean>) => void) =>
						n?.({ isDisabled: () => true }),
					),
					cancel: jest.fn(),
				},
			},
		});
		const onError = jest.fn();
		const { result } = renderGoogleAuth({ onError });

		await act(async () => {
			await result.current.signInWithGoogle();
		});

		expect(onError).toHaveBeenCalledWith("Google sign in is turned off for this browser.");
	});

	it("refuses to start when the backend has no client id configured", async () => {
		configMock.mockResolvedValue({ client_id: "" });
		const onError = jest.fn();
		const { result } = renderGoogleAuth({ onError });

		let user: unknown = "untouched";
		await act(async () => {
			user = await result.current.signInWithGoogle();
		});

		expect(user).toBeNull();
		expect(loadMock).not.toHaveBeenCalled();
		expect(loginMock).not.toHaveBeenCalled();
		expect(onError).toHaveBeenCalledWith("Google sign in is not configured yet.");
	});

	it("reports an unreachable backend instead of throwing", async () => {
		configMock.mockRejectedValue(new Error("network down"));
		const onError = jest.fn();
		const { result, store } = renderGoogleAuth({ onError });

		let user: unknown = "untouched";
		await act(async () => {
			user = await result.current.signInWithGoogle();
		});

		expect(user).toBeNull();
		expect(onError).toHaveBeenCalledWith(
			"Google sign in is unavailable. Please try again or use email and password.",
		);
		expect(store.getState().auth.isAuthenticated).toBe(false);
	});

	it("reports a Google script that cannot load", async () => {
		loadMock.mockRejectedValue(new Error("script blocked"));
		const onError = jest.fn();
		const { result } = renderGoogleAuth({ onError });

		await act(async () => {
			await result.current.signInWithGoogle();
		});

		expect(onError).toHaveBeenCalledWith(
			"Google sign in is unavailable. Please try again or use email and password.",
		);
		expect(loginMock).not.toHaveBeenCalled();
	});
});
