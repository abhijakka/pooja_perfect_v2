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

export type UnauthorizedHandler = () => void;

let unauthorizedHandler: UnauthorizedHandler | undefined;

export function setUnauthorizedHandler(handler: UnauthorizedHandler | undefined): void {
	unauthorizedHandler = handler;
}

function notifyUnauthorized(): void {
	if (unauthorizedHandler) unauthorizedHandler();
}

/** Public auth endpoints that rightfully return 401 for bad input — not session failures. */
const PUBLIC_AUTH_PATHS = ["/auth/login", "/auth/register", "/auth/google", "/auth/refresh"];

const AUTH_ERROR_MESSAGES = [
	"authentication required",
	"invalid or malformed token",
	"token has expired",
	"not authenticated",
];

function isAuthFailureResponse(status: number, path: string): boolean {
	return status === 401 && !PUBLIC_AUTH_PATHS.some((candidate) => path.startsWith(candidate));
}

function isAuthFailureMessage(message: string): boolean {
	const text = message.toLowerCase();
	return AUTH_ERROR_MESSAGES.some((candidate) => text.includes(candidate));
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
		if (isAuthFailureResponse(response.status, path)) notifyUnauthorized();
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
		if (isAuthFailureResponse(response.status, path)) notifyUnauthorized();
		throw new ApiError(response.status, `GraphQL request failed with status ${response.status}`);
	}

	const body = (await response.json()) as {
		data?: T;
		errors?: Array<{ message: string }>;
	};
	if (body.errors?.length) {
		if (body.errors.some((error) => isAuthFailureMessage(error.message))) notifyUnauthorized();
		throw new GraphQLError(body.errors);
	}
	return body.data as T;
}
