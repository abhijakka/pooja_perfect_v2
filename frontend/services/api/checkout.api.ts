import { graphqlClient } from "./client";

export type CheckoutInput = {
	recipientName: string;
	phone: string;
	addressLine1: string;
	city: string;
	state: string;
	postalCode: string;
	country: string;
	paymentMethod: "upi" | "card" | "netbanking" | "cod";
	addressLine2?: string;
	couponCode?: string;
	notes?: string;
};

export const checkoutApi = {
	placeOrder: (input: CheckoutInput) => graphqlClient<{ checkout: { order: { orderNumber: string; subtotal: number; discount: number; shippingCharge: number; total: number; notes?: string | null; createdAt: string; items: Array<{ id: string; productName: string; quantity: number; unitPrice: number }> } } }>(`
		mutation Checkout($recipientName: String!, $phone: String!, $addressLine1: String!, $city: String!, $state: String!, $postalCode: String!, $country: String!, $paymentMethod: String!, $addressLine2: String, $couponCode: String, $notes: String) {
			checkout(recipientName: $recipientName, phone: $phone, addressLine1: $addressLine1, city: $city, state: $state, postalCode: $postalCode, country: $country, paymentMethod: $paymentMethod, addressLine2: $addressLine2, couponCode: $couponCode, notes: $notes) {
				order { orderNumber subtotal discount shippingCharge total notes createdAt items { id productName quantity unitPrice } }
			}
		}
	`, input),
};
