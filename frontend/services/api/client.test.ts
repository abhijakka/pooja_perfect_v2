import { environment } from "../../config/environment";
import { apiClient, ApiError, graphqlClient, setSessionRefresher, setUnauthorizedHandler } from "./client";

jest.mock("../../config/environment", () => ({
	environment: { apiUrl: "" },
}));

describe("apiClient", () => {
	const fetchMock = jest.fn();

	beforeEach(() => {
		global.fetch = fetchMock as unknown as typeof fetch;
		fetchMock.mockReset();
		environment.apiUrl = "";
	});

	it("throws until configured", async () => {
		await expect(apiClient("/products")).rejects.toThrow("API client is not configured");
	});

	it("GETs JSON from the configured base URL", async () => {
		environment.apiUrl = "http://localhost:8000/";
		fetchMock.mockResolvedValue({ ok: true, status: 200, json: async () => ({ id: "1" }) });

		await expect(apiClient<{ id: string }>("/products", { method: "GET" })).resolves.toEqual({ id: "1" });
		expect(fetchMock).toHaveBeenCalledWith(
			"http://localhost:8000/products",
			expect.objectContaining({ method: "GET" }),
		);
	});

	it("includes cookies for cookie-authenticated requests", async () => {
		environment.apiUrl = "http://localhost:8000";
		fetchMock.mockResolvedValue({ ok: true, status: 200, json: async () => ({}) });

		await apiClient("/auth/me", { method: "GET", credentials: "include" });
		const [, init] = fetchMock.mock.calls[0];
		expect(init.credentials).toBe("include");
	});

	it("throws ApiError with backend detail on HTTP error", async () => {
		environment.apiUrl = "http://localhost:8000";
		fetchMock.mockResolvedValue({
			ok: false,
			status: 401,
			json: async () => ({ detail: "Invalid credentials" }),
		});

		await expect(apiClient("/auth/login", { method: "POST" })).rejects.toMatchObject({
			name: "ApiError",
			status: 401,
			detail: "Invalid credentials",
		});
	});

	it("returns undefined for 204 responses", async () => {
		environment.apiUrl = "http://localhost:8000";
		fetchMock.mockResolvedValue({
			ok: true,
			status: 204,
			json: async () => {
				throw new Error("no body");
			},
		});

		await expect(apiClient<void>("/auth/logout", { method: "POST" })).resolves.toBeUndefined();
	});

	it("notifies the unauthorized handler on a protected-endpoint 401", async () => {
		environment.apiUrl = "http://localhost:8000";
		const handler = jest.fn();
		setUnauthorizedHandler(handler);
		fetchMock.mockResolvedValue({
			ok: false,
			status: 401,
			json: async () => ({ detail: "Token has expired" }),
		});

		await expect(apiClient("/auth/me", { method: "GET" })).rejects.toBeInstanceOf(ApiError);
		expect(handler).toHaveBeenCalledTimes(1);
		setUnauthorizedHandler(undefined);
	});

	it("does not notify the unauthorized handler for public auth 401s", async () => {
		environment.apiUrl = "http://localhost:8000";
		const handler = jest.fn();
		setUnauthorizedHandler(handler);
		fetchMock.mockResolvedValue({
			ok: false,
			status: 401,
			json: async () => ({ detail: "Invalid credentials" }),
		});

		await expect(apiClient("/auth/login", { method: "POST" })).rejects.toBeInstanceOf(ApiError);
		expect(handler).not.toHaveBeenCalled();
		setUnauthorizedHandler(undefined);
	});

	it("notifies the unauthorized handler when GraphQL reports an auth error", async () => {
		environment.apiUrl = "http://localhost:8000";
		const handler = jest.fn();
		setUnauthorizedHandler(handler);
		fetchMock.mockResolvedValue({
			ok: true,
			status: 200,
			json: async () => ({
				data: null,
				errors: [{ message: "Authentication required" }],
			}),
		});

		await expect(graphqlClient("{ currentUser { id } }")).rejects.toThrow("Authentication required");
		expect(handler).toHaveBeenCalledTimes(1);
		setUnauthorizedHandler(undefined);
	});
});

describe("session recovery", () => {
	const fetchMock = jest.fn();

	beforeEach(() => {
		global.fetch = fetchMock as unknown as typeof fetch;
		fetchMock.mockReset();
		environment.apiUrl = "http://localhost:8000";
	});

	afterEach(() => {
		setSessionRefresher(undefined);
		setUnauthorizedHandler(undefined);
	});

	const unauthorized = {
		ok: false,
		status: 401,
		json: async () => ({ detail: "Token has expired" }),
	};

	it("replays a REST request after a successful refresh instead of logging out", async () => {
		const handler = jest.fn();
		setUnauthorizedHandler(handler);
		setSessionRefresher(async () => true);
		fetchMock.mockResolvedValueOnce(unauthorized).mockResolvedValueOnce({
			ok: true,
			status: 200,
			json: async () => ({ id: "1" }),
		});

		await expect(apiClient<{ id: string }>("/auth/me")).resolves.toEqual({ id: "1" });
		expect(handler).not.toHaveBeenCalled();
		expect(fetchMock).toHaveBeenCalledTimes(2);
	});

	it("replays a GraphQL request after a successful refresh instead of logging out", async () => {
		const handler = jest.fn();
		setUnauthorizedHandler(handler);
		setSessionRefresher(async () => true);
		fetchMock.mockResolvedValueOnce({
			ok: true,
			status: 200,
			json: async () => ({ data: null, errors: [{ message: "Authentication required" }] }),
		}).mockResolvedValueOnce({
			ok: true,
			status: 200,
			json: async () => ({ data: { currentUser: { id: "1" } } }),
		});

		await expect(graphqlClient<{ currentUser: { id: string } }>("{ currentUser { id } }")).resolves.toEqual({
			currentUser: { id: "1" },
		});
		expect(handler).not.toHaveBeenCalled();
	});

	it("logs out only after the refresh itself fails", async () => {
		const handler = jest.fn();
		setUnauthorizedHandler(handler);
		setSessionRefresher(async () => false);
		fetchMock.mockResolvedValue(unauthorized);

		await expect(apiClient("/auth/me")).rejects.toBeInstanceOf(ApiError);
		expect(handler).toHaveBeenCalledTimes(1);
	});

	it("survives a failing refresh and still reports the original error", async () => {
		const handler = jest.fn();
		setUnauthorizedHandler(handler);
		setSessionRefresher(async () => {
			throw new Error("network down");
		});
		fetchMock.mockResolvedValue(unauthorized);

		await expect(apiClient("/auth/me")).rejects.toMatchObject({ status: 401 });
		expect(handler).toHaveBeenCalledTimes(1);
	});

	it("refreshes once for a burst of concurrent failures", async () => {
		let resolveRefresh: (value: boolean) => void = () => {};
		const refresher = jest.fn(
			() =>
				new Promise<boolean>((resolve) => {
					resolveRefresh = resolve;
				}),
		);
		setSessionRefresher(refresher);
		fetchMock.mockResolvedValue(unauthorized);

		const requests = Promise.all([apiClient("/a").catch(() => null), apiClient("/b").catch(() => null)]);
		// Let both requests reach the auth-failure branch before the refresh settles.
		await Promise.resolve();
		await Promise.resolve();
		expect(refresher).toHaveBeenCalledTimes(1);
		resolveRefresh(false);
		await requests;
	});

	it("does not retry forever when the replay fails the same way", async () => {
		setSessionRefresher(async () => true);
		fetchMock.mockResolvedValue(unauthorized);

		await expect(apiClient("/auth/me")).rejects.toBeInstanceOf(ApiError);
		expect(fetchMock).toHaveBeenCalledTimes(2);
	});
});
