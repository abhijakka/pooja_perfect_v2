import { graphqlClient } from "./client";

export type CartApiItem = {
	id: string;
	productId: string;
	quantity: number;
	unitPrice: number;
	product?: {
		id: string;
		name: string;
		slug: string;
		price: number;
		images?: Array<{ url: string; isPrimary: boolean }>;
	} | null;
};

export type CartApiResponse = {
	cart: {
		id: string;
		itemCount: number;
		subtotal: number;
		items: CartApiItem[];
	};
};

export const cartApi = {
	get: () => graphqlClient<CartApiResponse>(`
		query Cart {
			cart {
				id
				itemCount
				subtotal
				items {
					id
					productId
					quantity
					unitPrice
					product {
						id
						name
						slug
						price
						images { url isPrimary }
					}
				}
			}
		}
	`),
	add: (productId: string, quantity = 1) => graphqlClient<CartApiResponse>(`
		mutation AddToCart($productId: UUID!, $quantity: Int!) {
			addToCart(productId: $productId, quantity: $quantity) {
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
			}
		}
	`, { productId, quantity }),
	update: (itemId: string, quantity: number) => graphqlClient<CartApiResponse>(`
		mutation UpdateCartItem($itemId: UUID!, $quantity: Int!) {
			updateCartItem(itemId: $itemId, quantity: $quantity) {
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
			}
		}
	`, { itemId, quantity }),
	remove: (itemId: string) => graphqlClient<CartApiResponse>(`
		mutation RemoveCartItem($itemId: UUID!) {
			removeCartItem(itemId: $itemId) {
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
			}
		}
	`, { itemId }),
	clear: () => graphqlClient<CartApiResponse>(`
		mutation ClearCart {
			clearCart {
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
			}
		}
	`),
};
