import { graphqlClient } from "./client";

export type AccountUser = {
	id: string;
	firstName: string;
	lastName: string;
	email: string;
	phone?: string | null;
	createdAt: string;
	status: string;
};

export type AccountAddress = {
	id: string;
	label: string;
	recipientName: string;
	phone: string;
	addressLine1: string;
	city: string;
	state: string;
	postalCode: string;
	country: string;
	isDefault: boolean;
};

export type AccountOrder = {
	id: string;
	orderNumber: string;
	status: string;
	total: number;
	createdAt: string;
	items: Array<{ productName: string; quantity: number; unitPrice: number; productId: string }>;
};

export const accountApi = {
	getOverview: () => graphqlClient<{ currentUser: AccountUser; addresses: AccountAddress[]; orders: { items: AccountOrder[] } }>(`
		query AccountOverview {
			currentUser { id firstName lastName email phone createdAt status }
			addresses { id label recipientName phone addressLine1 city state postalCode country isDefault }
			orders(page: 1, pageSize: 100) { items { id orderNumber status total createdAt items { productName quantity unitPrice productId } } }
		}
	`),
};

