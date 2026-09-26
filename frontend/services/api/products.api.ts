import { graphqlClient } from "./client";

type ProductImage = { url: string; isPrimary: boolean };

/**
 * Money and rating are `Decimal` on the backend and Strawberry serializes them as JSON
 * strings ("549.00"), so the wire values are `number | string` and must be coerced once,
 * in `toStorefrontProduct`.
 */
export type CatalogProduct = {
	id: string;
	name: string;
	slug: string;
	price: number | string;
	originalPrice?: number | string | null;
	discountPrice?: number | string | null;
	averageRating: number | string;
	isFeatured?: boolean;
	images: ProductImage[];
};

export type CatalogProductDetail = CatalogProduct & {
	categoryId: string;
	shortDescription?: string | null;
	description?: string | null;
	stock: number;
	reviewCount: number;
};

type CategoryRef = { id: string; name: string; slug: string };

type ProductPage = { items: CatalogProduct[]; pagination: { total: number } };

/** Fields shared by every product selection, so list and detail never drift apart. */
export const PRODUCT_FIELDS = `
	id
	name
	slug
	price
	originalPrice
	discountPrice
	averageRating
	reviewCount
	isFeatured
	categoryId
	images { url isPrimary }
`;

/**
 * A product is identified by its slug for navigation and by its UUID for cart mutations.
 * `bySlug` also returns the category list so `categoryId` can be resolved to a real
 * category name in the same round trip instead of a hardcoded label.
 */
export const productsApi = {
	list: (variables: { page?: number; pageSize?: number; isFeatured?: boolean } = {}) => graphqlClient<{ products: ProductPage }>(`
		query Products($page: Int, $pageSize: Int, $isFeatured: Boolean) {
			products(page: $page, pageSize: $pageSize, isFeatured: $isFeatured) {
				items {${PRODUCT_FIELDS}}
				pagination { total }
			}
		}
	`, variables),
	featured: (variables: { page?: number; pageSize?: number } = {}) =>
		productsApi.list({ ...variables, isFeatured: true }),
	bySlug: (slug: string) =>
		graphqlClient<{ product: CatalogProductDetail; categories: CategoryRef[] }>(`
			query ProductBySlug($slug: String!) {
				product(slug: $slug) {${PRODUCT_FIELDS}
					shortDescription
					description
					stock
				}
				categories { id name slug }
			}
		`, { slug }),
};

export function categoryNameFor(categories: CategoryRef[], categoryId: string | null | undefined): string {
	const match = categories.find((category) => category.id === categoryId);
	return match?.name ?? "Pooja Essentials";
}

export function categorySlugFor(categories: CategoryRef[], categoryId: string | null | undefined): string {
	const match = categories.find((category) => category.id === categoryId);
	return match?.slug ?? "pooja";
}
