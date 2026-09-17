import { apiClient } from "./client";
import type {
	LoginInput,
	OAuthLoginInput,
	SignupInput,
	TokenResponse,
	UserResponse,
} from "../../types/auth";

// ponytail: only auth is wired because it is the only backend API implemented.
// The other <domain>.api.ts files stay as stubs until their endpoints exist.
export const authApi = {
	register: (data: SignupInput) =>
		apiClient<UserResponse>("/auth/register", { method: "POST", credentials: "include", body: JSON.stringify(data) }),
	login: (data: LoginInput) =>
		apiClient<TokenResponse>("/auth/login", { method: "POST", credentials: "include", body: JSON.stringify(data) }),
	refresh: (refreshToken?: string) =>
		apiClient<TokenResponse>("/auth/refresh", { method: "POST", credentials: "include", ...(refreshToken ? { body: JSON.stringify({ refresh_token: refreshToken }) } : {}) }),
	logout: (refreshToken?: string) =>
		apiClient<void>("/auth/logout", { method: "POST", credentials: "include", ...(refreshToken ? { body: JSON.stringify({ refresh_token: refreshToken }) } : {}) }),
	me: () =>
		apiClient<UserResponse>("/auth/me", { method: "GET", credentials: "include" }),
	googleLogin: (data: OAuthLoginInput) =>
		apiClient<TokenResponse>("/auth/google", { method: "POST", credentials: "include", body: JSON.stringify(data) }),
};
