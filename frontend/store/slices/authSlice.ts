import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
import type { Customer } from "../../types/customer";

type AuthState = { user: Customer | null; isAuthenticated: boolean; isReady: boolean; accessTokenExpiresAt: number | null; sessionExpired: boolean };

const initialState: AuthState = { user: null, isAuthenticated: false, isReady: false, accessTokenExpiresAt: null, sessionExpired: false };

const authSlice = createSlice({
	name: "auth",
	initialState,
	reducers: {
		setUser: (state, action: PayloadAction<Customer>) => {
			state.user = action.payload;
			state.isAuthenticated = Boolean(action.payload);
			state.sessionExpired = false;
		},
		setTokenExpiry: (state, action: PayloadAction<number>) => {
			state.accessTokenExpiresAt = action.payload;
		},
		setSessionExpired: (state) => {
			state.sessionExpired = true;
		},
		logout: (state) => {
			state.user = null;
			state.isAuthenticated = false;
			state.accessTokenExpiresAt = null;
		},
		setAuthReady: (state) => {
			state.isReady = true;
		},
	},
});

export const { setUser, setTokenExpiry, setSessionExpired, logout, setAuthReady } = authSlice.actions;
export default authSlice.reducer;