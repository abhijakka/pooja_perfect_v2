export type CartProduct = {
	id: string;
	name: string;
	price: number;
	oldPrice: number;
	rating: string;
	category: string;
	categoryLabel: string;
	slug: string;
	image: string;
};
export type CartItem = CartProduct & {
	quantity: number;
	/** Server-side cart line id. Required by updateCartItem/removeCartItem mutations. */
	cartItemId?: string;
};
export type Cart = { items: CartItem[] };
