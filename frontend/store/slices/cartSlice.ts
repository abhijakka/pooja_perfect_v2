import { createSlice, createSelector, type PayloadAction } from "@reduxjs/toolkit";
import type { CartItem, CartProduct } from "../../types/cart";
import type { RootState } from "../index";

type CartState = { items: CartItem[] };

const initialState: CartState = { items: [] };

const cartSlice = createSlice({
	name: "cart",
	initialState,
	reducers: {
		hydrate: (state, action: PayloadAction<CartItem[]>) => {
			state.items = action.payload;
		},
		addItem: (state, action: PayloadAction<{ product: CartProduct; quantity?: number }>) => {
			const { product, quantity = 1 } = action.payload;
			const amount = Math.max(1, quantity);
			const existing = state.items.find((item) => item.id === product.id);
			if (existing) {
				existing.quantity += amount;
			} else {
				state.items.push({ ...product, quantity: amount });
			}
		},
		removeItem: (state, action: PayloadAction<string>) => {
			state.items = state.items.filter((item) => item.id !== action.payload);
		},
		updateQuantity: (state, action: PayloadAction<{ productId: string; quantity: number }>) => {
			const { productId, quantity } = action.payload;
			if (quantity <= 0) {
				state.items = state.items.filter((item) => item.id !== productId);
			} else {
				const item = state.items.find((item) => item.id === productId);
				if (item) item.quantity = quantity;
			}
		},
		clearCart: (state) => {
			state.items = [];
		},
	},
});

export const { hydrate, addItem, removeItem, updateQuantity, clearCart } = cartSlice.actions;

const selectCartItems = (state: RootState) => state.cart.items;
const selectCartCount = createSelector(selectCartItems, (items) =>
	items.reduce((total, item) => total + item.quantity, 0)
);
const selectCartTotal = createSelector(selectCartItems, (items) =>
	items.reduce((total, item) => total + item.price * item.quantity, 0)
);

export { selectCartItems, selectCartCount, selectCartTotal };
export default cartSlice.reducer;