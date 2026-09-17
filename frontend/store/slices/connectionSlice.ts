import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
import type { RootState } from "../index";

type ConnectionState = {
	isOnline: boolean;
};

const initialState: ConnectionState = {
	isOnline: true,
};

const connectionSlice = createSlice({
	name: "connection",
	initialState,
	reducers: {
		setOnline: (state, action: PayloadAction<boolean>) => {
			state.isOnline = action.payload;
		},
	},
});

export const { setOnline } = connectionSlice.actions;
export const selectIsBackendOnline = (state: RootState) => state.connection.isOnline;
export default connectionSlice.reducer;
