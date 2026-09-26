import { graphqlClient } from "./client";
import type { CartItem } from "../../types/cart";

export type CartApiItem = {
	id: string;
	productId: string;
	quantity: number;
	/** Decimal on the backend, serialized as a JSON string by Strawberry. */
	unitPrice: number | string;
	product?: {
		id: string;
		name: string;
		slug: string;
		price: number | string;
		images?: Array<{ url: string; isPrimary: boolean }>;
	} | null;
};

export type CartApi = {
	id: string;
	itemCount: number;
	subtotal: number;
	items: CartApiItem[];
};

export type CartApiResponse = { cart: CartApi };

/** One selection reused by every cart operation so responses can never drift. */
const CART_FIELDS = `
	id
	itemCount
	subtotal
	items {
		id
		productId
		quantity
		unitPrice
		product { id name slug price images { url isPrimary } }
	}
`;

export const cartApi = {
	get: () => graphqlClient<CartApiResponse>(`
		query Cart {
			cart {${CART_FIELDS}}
		}
	`),
	add: (productId: string, quantity = 1) => graphqlClient<{ addToCart: CartApi }>(`
		mutation AddToCart($productId: UUID!, $quantity: Int!) {
			addToCart(productId: $productId, quantity: $quantity) {${CART_FIELDS}}
		}
	`, { productId, quantity }),
	update: (itemId: string, quantity: number) => graphqlClient<{ updateCartItem: CartApi }>(`
		mutation UpdateCartItem($itemId: UUID!, $quantity: Int!) {
			updateCartItem(itemId: $itemId, quantity: $quantity) {${CART_FIELDS}}
		}
	`, { itemId, quantity }),
	remove: (itemId: string) => graphqlClient<{ removeCartItem: CartApi }>(`
		mutation RemoveCartItem($itemId: UUID!) {
			removeCartItem(itemId: $itemId) {${CART_FIELDS}}
		}
	`, { itemId }),
	clear: () => graphqlClient<{ clearCart: CartApi }>(`
		mutation ClearCart {
			clearCart {${CART_FIELDS}}
		}
	`),
};

const UUID_RE = /^[0-9a-f]{8}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{12}$/i;

/** Products outside the backend catalog (demo/subscription lines) cannot be sent as a productId. */
export function isBackendProductId(id: string | undefined | null): boolean {
	return Boolean(id && UUID_RE.test(id));
}

/**
 * The single translation from the cart GraphQL payload to the storefront cart rows.
 * `slug` is only ever a real product slug — a cart line id is never substituted for it,
 * so `/products/<slug>` links can never be built from a cart-line UUID.
 */
export function toCartItems(cart: CartApi | null | undefined): CartItem[] {
	return (cart?.items ?? []).map((item) => {
		const product = item.product;
		const price = Number(item.unitPrice ?? product?.price ?? 0);
		const listPrice = Number(product?.price ?? item.unitPrice ?? 0);
		return {
			cartItemId: item.id,
			id: item.productId ?? product?.id ?? item.id,
			name: product?.name ?? "Unavailable product",
			price: Number.isFinite(price) ? price : 0,
			oldPrice: Number.isFinite(listPrice) && listPrice > 0 ? listPrice : Number.isFinite(price) ? price : 0,
			rating: "5.0",
			category: "pooja",
			categoryLabel: "Pooja Essentials",
			slug: product?.slug ?? "",
			image: product?.images?.find((image) => image.isPrimary)?.url ?? product?.images?.[0]?.url ?? "",
			quantity: item.quantity,
		};
	});
}
