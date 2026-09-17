import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
import type { Subscription } from "../../types/subscription";

type SubscriptionState = { subscriptions: Subscription[] };

const initialState: SubscriptionState = { subscriptions: [] };

const subscriptionSlice = createSlice({
	name: "subscription",
	initialState,
	reducers: {
		setSubscriptions: (state, action: PayloadAction<Subscription[]>) => {
			state.subscriptions = action.payload;
		},
	},
});

export const { setSubscriptions } = subscriptionSlice.actions;
export default subscriptionSlice.reducer;