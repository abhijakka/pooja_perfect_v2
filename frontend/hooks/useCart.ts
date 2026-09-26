import { useCallback } from "react";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import { addItem, removeItem, updateQuantity, clearCart, hydrate, selectCartItems, selectCartCount, selectCartTotal } from "../store/slices/cartSlice";
import { setOnline } from "../store/slices/connectionSlice";
import { cartApi, isBackendProductId, toCartItems } from "../services/api/cart.api";
import type { CartProduct } from "../types/cart";

/**
 * The backend cart is the single source of truth. Every mutation goes through the existing
 * cart GraphQL operations and the response becomes the new state, so the cart survives
 * navigation, refresh and sign-in. Local state is updated optimistically first and kept
 * when the backend is unreachable, so the storefront stays usable offline.
 */
export function useCart() {
	const dispatch = useAppDispatch();
	const items = useAppSelector(selectCartItems);
	const count = useAppSelector(selectCartCount);
	const total = useAppSelector(selectCartTotal);

	const applyServerCart = useCallback(
		(cart: Parameters<typeof toCartItems>[0]) => {
			dispatch(hydrate(toCartItems(cart)));
			dispatch(setOnline(true));
		},
		[dispatch],
	);

	const settle = useCallback(
		(request: Promise<unknown>) => {
			request.catch(() => dispatch(setOnline(false)));
		},
		[dispatch],
	);

	const addItemToCart = useCallback(
		(product: CartProduct, quantity?: number) => {
			dispatch(addItem({ product, quantity }));
			if (!isBackendProductId(product.id)) return;
			settle(
				cartApi.add(product.id, Math.max(1, quantity ?? 1)).then(({ addToCart }) => applyServerCart(addToCart)),
			);
		},
		[applyServerCart, dispatch, settle],
	);

	const removeItemFromCart = useCallback(
		(productId: string) => {
			dispatch(removeItem(productId));
			const target = items.find((item) => item.id === productId);
			if (!target?.cartItemId) return;
			settle(
				cartApi.remove(target.cartItemId).then(({ removeCartItem }) => applyServerCart(removeCartItem)),
			);
		},
		[applyServerCart, dispatch, items, settle],
	);

	const setItemQuantity = useCallback(
		(productId: string, quantity: number) => {
			dispatch(updateQuantity({ productId, quantity }));
			const target = items.find((item) => item.id === productId);
			if (!target?.cartItemId) return;
			settle(
				cartApi.update(target.cartItemId, Math.max(1, quantity)).then(({ updateCartItem }) =>
					applyServerCart(updateCartItem),
				),
			);
		},
		[applyServerCart, dispatch, items, settle],
	);

	const emptyCart = useCallback(() => {
		dispatch(clearCart());
		settle(cartApi.clear().then(({ clearCart: cart }) => applyServerCart(cart)));
	}, [applyServerCart, dispatch, settle]);

	return {
		items,
		count,
		total,
		addItem: addItemToCart,
		removeItem: removeItemFromCart,
		updateQuantity: setItemQuantity,
		clearCart: emptyCart,
	};
}
