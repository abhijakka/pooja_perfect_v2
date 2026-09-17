import { useCallback } from "react";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import { add, remove, toggle, selectWishlistItems, selectWishlistCount } from "../store/slices/wishlistSlice";

export function useWishlist() {
	const dispatch = useAppDispatch();
	const items = useAppSelector(selectWishlistItems);
	const count = useAppSelector(selectWishlistCount);

	return {
		items,
		count,
		add: useCallback((productId: string) => dispatch(add(productId)), [dispatch]),
		remove: useCallback((productId: string) => dispatch(remove(productId)), [dispatch]),
		toggle: useCallback((productId: string) => dispatch(toggle(productId)), [dispatch]),
		contains: useCallback((productId: string) => items.includes(productId), [items]),
	};
}
