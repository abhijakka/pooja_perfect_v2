import { graphqlClient } from "./client";

type ProductImage = { url: string; isPrimary: boolean };
export type CatalogProduct = {
	id: string;
	name: string;
	slug: string;
	price: number;
	originalPrice?: number | null;
	discountPrice?: number | null;
	averageRating: number;
	isFeatured?: boolean;
	images: ProductImage[];
};

type ProductPage = { items: CatalogProduct[]; pagination: { total: number } };

export const productsApi = {
	list: (variables: { page?: number; pageSize?: number; isFeatured?: boolean } = {}) => graphqlClient<{ products: ProductPage }>(`
		query Products($page: Int, $pageSize: Int, $isFeatured: Boolean) {
			products(page: $page, pageSize: $pageSize, isFeatured: $isFeatured) {
				items { id name slug price originalPrice discountPrice averageRating isFeatured images { url isPrimary } }
				pagination { total }
			}
		}
	`, variables),
	featured: (variables: { page?: number; pageSize?: number } = {}) =>
		productsApi.list({ ...variables, isFeatured: true }),
};
