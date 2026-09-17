import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
import type { Customer } from "../../types/customer";

type AuthState = { user: Customer | null; isAuthenticated: boolean; isReady: boolean };

const initialState: AuthState = { user: null, isAuthenticated: false, isReady: false };

const authSlice = createSlice({
	name: "auth",
	initialState,
	reducers: {
		setUser: (state, action: PayloadAction<Customer>) => {
			state.user = action.payload;
			state.isAuthenticated = Boolean(action.payload);
		},
		logout: (state) => {
			state.user = null;
			state.isAuthenticated = false;
		},
		setAuthReady: (state) => {
			state.isReady = true;
		},
	},
});

export const { setUser, logout, setAuthReady } = authSlice.actions;
export default authSlice.reducer;