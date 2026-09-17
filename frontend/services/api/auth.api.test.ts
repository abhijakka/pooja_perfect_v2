import { authApi } from "./auth.api";
import { apiClient } from "./client";

jest.mock("./client", () => ({
	apiClient: jest.fn(),
}));

const apiClientMock = apiClient as jest.Mock;

describe("authApi", () => {
	beforeEach(() => apiClientMock.mockReset());

	it("registers a user", () => {
		const input = {
			first_name: "Abhinav",
			last_name: "Sharma",
			email: "abhinav@example.com",
			password: "password123",
			confirm_password: "password123",
		};
		authApi.register(input);
		expect(apiClientMock).toHaveBeenCalledWith("/auth/register", {
			method: "POST",
			body: JSON.stringify(input),
			credentials: "include",
		});
	});

	it("logs in", () => {
		const input = { identifier: "abhinav@example.com", password: "password123" };
		authApi.login(input);
		expect(apiClientMock).toHaveBeenCalledWith("/auth/login", {
			method: "POST",
			body: JSON.stringify(input),
			credentials: "include",
		});
	});

	it("refreshes a token", () => {
		authApi.refresh("refresh-token");
		expect(apiClientMock).toHaveBeenCalledWith("/auth/refresh", {
			method: "POST",
			body: JSON.stringify({ refresh_token: "refresh-token" }),
			credentials: "include",
		});
	});

	it("logs out", () => {
		authApi.logout("refresh-token");
		expect(apiClientMock).toHaveBeenCalledWith("/auth/logout", {
			method: "POST",
			body: JSON.stringify({ refresh_token: "refresh-token" }),
			credentials: "include",
		});
	});

	it("fetches the current user using cookie auth", () => {
		authApi.me();
		expect(apiClientMock).toHaveBeenCalledWith("/auth/me", { method: "GET", credentials: "include" });
	});

	it("logs in with google", () => {
		const input = { provider: "google", id_token: "id-token" };
		authApi.googleLogin(input);
		expect(apiClientMock).toHaveBeenCalledWith("/auth/google", {
			method: "POST",
			body: JSON.stringify(input),
			credentials: "include",
		});
	});
});