import { environment } from "../../config/environment";
import { apiClient, ApiError } from "./client";

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
});