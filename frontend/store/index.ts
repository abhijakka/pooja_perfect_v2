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
		store.subscribe(() => {
			try {
				const { items } = store.getState().wishlist;
				window.localStorage.setItem("poojapoint-wishlist", JSON.stringify(items));
			} catch {}
			try {
				const { items } = store.getState().cart;
				window.localStorage.setItem("poojapoint-cart", JSON.stringify(items));
			} catch {}
		});
	}

	return store;
};

export type AppStore = ReturnType<typeof makeStore>;
export type RootState = ReturnType<AppStore["getState"]>;
export type AppDispatch = AppStore["dispatch"];