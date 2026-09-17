import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

type CheckoutState = { isSubmitting: boolean };

const initialState: CheckoutState = { isSubmitting: false };

const checkoutSlice = createSlice({
	name: "checkout",
	initialState,
	reducers: {
		setSubmitting: (state, action: PayloadAction<boolean>) => {
			state.isSubmitting = action.payload;
		},
	},
});

export const { setSubmitting } = checkoutSlice.actions;
export default checkoutSlice.reducer;