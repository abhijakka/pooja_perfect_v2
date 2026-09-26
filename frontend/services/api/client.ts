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
/** Attempts a silent token refresh. Resolves true when the session is usable again. */
export type SessionRefresher = () => Promise<boolean>;

let unauthorizedHandler: UnauthorizedHandler | undefined;
let sessionRefresher: SessionRefresher | undefined;
let refreshInFlight: Promise<boolean> | null = null;

export function setUnauthorizedHandler(handler: UnauthorizedHandler | undefined): void {
	unauthorizedHandler = handler;
}

export function setSessionRefresher(refresher: SessionRefresher | undefined): void {
	sessionRefresher = refresher;
	refreshInFlight = null;
}

/**
 * Try to recover an expired access token from the HttpOnly refresh_token cookie.
 * Single-flight, so a burst of parallel 401s triggers exactly one POST /auth/refresh.
 */
async function refreshSession(): Promise<boolean> {
	if (!sessionRefresher) return false;
	refreshInFlight ??= sessionRefresher().finally(() => {
		refreshInFlight = null;
	});
	try {
		return await refreshInFlight;
	} catch {
		return false;
	}
}

/** An auth failure is only fatal once a refresh has been attempted and also failed. */
async function handleAuthFailure(): Promise<boolean> {
	if (await refreshSession()) return true; // session recovered, the caller may retry
	notifyUnauthorized();
	return false;
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
	/** Internal: bounds the refresh-and-replay to a single extra attempt. */
	retried = false,
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
		if (isAuthFailureResponse(response.status, path)) {
			const recovered = await handleAuthFailure();
			if (recovered && !retried) return apiClient<T>(path, init, token, true);
			if (!recovered) throw new ApiError(response.status, detail);
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
	/** Internal: bounds the refresh-and-replay to a single extra attempt. */
	retried = false,
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
		const recovered = isAuthFailureResponse(response.status, path) && (await handleAuthFailure());
		if (recovered && !retried) return graphqlRequest<T>(path, query, variables, token, true);
		throw new ApiError(response.status, `GraphQL request failed with status ${response.status}`);
	}

	const body = (await response.json()) as {
		data?: T;
		errors?: Array<{ message: string }>;
	};
	if (body.errors?.length) {
		if (body.errors.some((error) => isAuthFailureMessage(error.message))) {
			const recovered = await handleAuthFailure();
			if (recovered && !retried) return graphqlRequest<T>(path, query, variables, token, true);
		}
		throw new GraphQLError(body.errors);
	}
	return body.data as T;
}
