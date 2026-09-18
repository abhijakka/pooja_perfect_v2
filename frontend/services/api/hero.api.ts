import { graphqlClient } from "./client";

export type PublicHeroImage = {
	id: string;
	url: string;
	altText?: string | null;
	mediaType: string;
	displayOrder: number;
	isPrimary: boolean;
};

export type PublicHero = {
	id: string;
	title: string;
	subtitle?: string | null;
	badge?: string | null;
	accent?: string | null;
	ctaLabel?: string | null;
	ctaLink?: string | null;
	displayOrder: number;
	isActive: boolean;
	images: PublicHeroImage[];
};

export const heroesApi = {
	list: () => graphqlClient<{ heroes: PublicHero[] }>(`
		query Heroes {
			heroes {
				id
				title
				subtitle
				badge
				accent
				ctaLabel
				ctaLink
				displayOrder
				isActive
				images {
					id
					url
					altText
					mediaType
					displayOrder
					isPrimary
				}
			}
		}
	`),
};