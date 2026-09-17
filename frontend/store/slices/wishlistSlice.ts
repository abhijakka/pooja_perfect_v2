import { createSlice, createSelector, type PayloadAction } from "@reduxjs/toolkit";
import type { RootState } from "../index";

type WishlistState = { items: string[] };

const initialState: WishlistState = { items: [] };

const wishlistSlice = createSlice({
	name: "wishlist",
	initialState,
	reducers: {
		hydrate: (state, action: PayloadAction<string[]>) => {
			state.items = action.payload;
		},
		add: (state, action: PayloadAction<string>) => {
			if (!state.items.includes(action.payload)) {
				state.items.push(action.payload);
			}
		},
		remove: (state, action: PayloadAction<string>) => {
			state.items = state.items.filter((id) => id !== action.payload);
		},
		toggle: (state, action: PayloadAction<string>) => {
			const index = state.items.indexOf(action.payload);
			if (index >= 0) {
				state.items.splice(index, 1);
			} else {
				state.items.push(action.payload);
			}
		},
	},
});

export const { hydrate, add, remove, toggle } = wishlistSlice.actions;

const selectWishlistItems = (state: RootState) => state.wishlist.items;
const selectWishlistCount = createSelector(selectWishlistItems, (items) => items.length);
const selectWishlistContains = (productId: string) => (state: RootState) =>
	state.wishlist.items.includes(productId);

export { selectWishlistItems, selectWishlistCount, selectWishlistContains };
export default wishlistSlice.reducer;