import { configureStore } from "@reduxjs/toolkit";
import cartReducer from "./slices/cartSlice";
import wishlistReducer from "./slices/wishlistSlice";
import chatReducer from "./slices/chatSlice";
import authReducer from "./slices/authSlice";
import checkoutReducer from "./slices/checkoutSlice";
import subscriptionReducer from "./slices/subscriptionSlice";
import connectionReducer from "./slices/connectionSlice";

export const makeStore = () => {
	const store = configureStore({
		reducer: {
			cart: cartReducer,
			wishlist: wishlistReducer,
			chat: chatReducer,
			auth: authReducer,
			checkout: checkoutReducer,
			subscription: subscriptionReducer,
			connection: connectionReducer,
		},
	});

	if (typeof window !== "undefined") {
		// The wishlist is a local convenience list. The cart deliberately has no local
		// mirror: the backend cart (guest_token cookie or customer id) is the only cart,
		// so a second client-side copy can never disagree with it.
		store.subscribe(() => {
			try {
				const { items } = store.getState().wishlist;
				window.localStorage.setItem("poojapoint-wishlist", JSON.stringify(items));
			} catch {}
		});
	}

	return store;
};

export type AppStore = ReturnType<typeof makeStore>;
export type RootState = ReturnType<AppStore["getState"]>;
export type AppDispatch = AppStore["dispatch"];