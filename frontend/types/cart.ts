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
export type CartItem = CartProduct & { quantity: number };
export type Cart = { items: CartItem[] };
