import { useCallback } from "react";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import { addItem, removeItem, updateQuantity, clearCart, selectCartItems, selectCartCount, selectCartTotal } from "../store/slices/cartSlice";
import type { CartProduct } from "../types/cart";

export function useCart() {
	const dispatch = useAppDispatch();
	const items = useAppSelector(selectCartItems);
	const count = useAppSelector(selectCartCount);
	const total = useAppSelector(selectCartTotal);

	return {
		items,
		count,
		total,
		addItem: useCallback((product: CartProduct, quantity?: number) => dispatch(addItem({ product, quantity })), [dispatch]),
		removeItem: useCallback((productId: string) => dispatch(removeItem(productId)), [dispatch]),
		updateQuantity: useCallback((productId: string, quantity: number) => dispatch(updateQuantity({ productId, quantity })), [dispatch]),
		clearCart: useCallback(() => dispatch(clearCart()), [dispatch]),
	};
}
