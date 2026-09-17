import { environment } from "../../config/environment";

export class ApiError extends Error {
	readonly status: number;
	readonly detail?: string;

	constructor(status: number, detail?: string) {
		super(detail ?? `Request failed with status ${status}`);
		this.name = "ApiError";
		this.status = status;
		this.detail = detail;
	}
}

export class GraphQLError extends Error {
	readonly errors: Array<{ message: string }>;

	constructor(errors: Array<{ message: string }>) {
		super(errors.map((error) => error.message).join("; "));
		this.name = "GraphQLError";
		this.errors = errors;
	}
}

export async function apiClient<T>(
	path: string,
	init: RequestInit = {},
	token?: string,
): Promise<T> {
	const baseUrl = environment.apiUrl.replace(/\/+$/, "");
	if (!baseUrl) {
		throw new Error("API client is not configured");
	}

	const headers = new Headers(init.headers);
	headers.set("Content-Type", "application/json");
	if (token) headers.set("Authorization", `Bearer ${token}`);

	const requestInit: RequestInit = { ...init, headers };
	if (!requestInit.credentials && path.startsWith("/auth")) {
		requestInit.credentials = "include";
	}
	if (!requestInit.credentials && path.startsWith("/admin")) {
		requestInit.credentials = "include";
	}

	const response = await fetch(`${baseUrl}${path}`, requestInit);

	if (!response.ok) {
		let detail: string | undefined;
		try {
			const body = (await response.json()) as { detail?: string };
			detail = body.detail;
		} catch {
			// non-JSON error body
		}
		throw new ApiError(response.status, detail);
	}

	if (response.status === 204) return undefined as T;
	return (await response.json()) as T;
}

export async function graphqlClient<T>(
	query: string,
	variables: Record<string, unknown> = {},
	token?: string,
): Promise<T> {
	return graphqlRequest<T>("/graphql", query, variables, token);
}

export async function adminGraphqlClient<T>(
	query: string,
	variables: Record<string, unknown> = {},
	token?: string,
): Promise<T> {
	return graphqlRequest<T>("/admin/graphql", query, variables, token);
}

async function graphqlRequest<T>(
	path: string,
	query: string,
	variables: Record<string, unknown>,
	token?: string,
): Promise<T> {
	const baseUrl = environment.apiUrl.replace(/\/+$/, "");
	if (!baseUrl) {
		throw new Error("API client is not configured");
	}

	const headers = new Headers({ "Content-Type": "application/json" });
	if (token) headers.set("Authorization", `Bearer ${token}`);

	const response = await fetch(`${baseUrl}${path}`, {
		method: "POST",
		headers,
		body: JSON.stringify({ query, variables }),
		credentials: "include",
	});

	if (!response.ok) {
		throw new ApiError(response.status, `GraphQL request failed with status ${response.status}`);
	}

	const body = (await response.json()) as {
		data?: T;
		errors?: Array<{ message: string }>;
	};
	if (body.errors?.length) throw new GraphQLError(body.errors);
	return body.data as T;
}
