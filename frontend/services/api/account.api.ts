import { graphqlClient } from "./client";

export type AccountUser = {
	id: string;
	first_name: string;
	last_name: string;
	email: string;
	phone?: string | null;
	created_at: string;
	status: string;
};

export type AccountAddress = {
	id: string;
	label: string;
	recipient_name: string;
	phone: string;
	address_line1: string;
	city: string;
	state: string;
	postal_code: string;
	country: string;
	is_default: boolean;
};

export type AccountOrder = {
	id: string;
	order_number: string;
	status: string;
	total: number;
	created_at: string;
	items: Array<{ product_name: string; quantity: number; unit_price: number; product_id: string }>;
};

export const accountApi = {
	getOverview: () => graphqlClient<{ current_user: AccountUser; addresses: AccountAddress[]; orders: { items: AccountOrder[] } }>(`
		query AccountOverview {
			current_user { id first_name last_name email phone created_at status }
			addresses { id label recipient_name phone address_line1 city state postal_code country is_default }
				orders(page: 1, page_size: 100) { items { id order_number status total created_at items { product_name quantity unit_price product_id } } }
		}
	`),
};
