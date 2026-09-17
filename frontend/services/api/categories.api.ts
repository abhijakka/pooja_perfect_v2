import { graphqlClient } from "./client";

export type CategoryDto = {
	id: string;
	name: string;
	slug: string;
	imageUrl?: string | null;
	emoji?: string | null;
	isFeatured?: boolean;
};

export const categoriesApi = {
	list: () => graphqlClient<{ categories: CategoryDto[] }>(`
		query Categories {
			categories {
				id
				name
				slug
				imageUrl
				emoji
				isFeatured
			}
		}
	`),
	bySlug: (slug: string) => graphqlClient<{ category: CategoryDto }>(`
		query Category($slug: String!) {
			category(slug: $slug) {
				id
				name
				slug
				imageUrl
				emoji
				isFeatured
			}
		}
	`, { slug }),
};
