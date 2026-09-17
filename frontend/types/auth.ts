// Auth request/response contracts matching the FastAPI backend
// (backend/src/app/schemas/auth/* and schemas/user/user.py).

export type UserRole = "customer" | "admin";
export type UserStatus = "active" | "inactive" | "suspended";

export type UserResponse = {
	id: string;
	first_name: string;
	last_name: string;
	email: string;
	phone: string | null;
	avatar_url: string | null;
	date_of_birth: string | null;
	role_name: UserRole;
	status: UserStatus;
	is_email_verified: boolean;
	is_phone_verified: boolean;
	created_at: string;
	updated_at: string;
};

export type TokenResponse = {
	access_token: string;
	refresh_token: string;
	token_type: string;
	expires_at: string;
};

export type LoginInput = {
	identifier: string;
	password: string;
	remember?: boolean;
};

export type SignupInput = {
	first_name: string;
	last_name: string;
	email: string;
	phone?: string | null;
	password: string;
	confirm_password: string;
};

export type OAuthLoginInput = {
	provider: string;
	id_token: string;
};