import { render, screen } from "@testing-library/react";
import AdminHeroRoute from "./page";

jest.mock("next/navigation", () => ({ useRouter: () => ({ push: jest.fn(), replace: jest.fn() }) }));
jest.mock("react-redux", () => {
	const actual = jest.requireActual("react-redux");
	return { ...actual, useDispatch: Object.assign(() => jest.fn(), { withTypes: () => () => jest.fn() }) };
});

jest.mock("../../../services/api/admin.api", () => ({
	adminApi: {
		listHeroes: jest.fn().mockResolvedValue({
			heroes: [
				{
					id: "1",
					title: "Festive Glow",
					subtitle: "Celebrate with light",
					badge: "Bestseller",
					accent: "rose",
					ctaLabel: "Shop now",
					ctaLink: "/products",
					displayOrder: 0,
					startsAt: null,
					endsAt: null,
					seoTitle: "Festive",
					seoDescription: "Festive collection",
					isActive: true,
					createdAt: "2026-01-01T00:00:00Z",
					updatedAt: "2026-01-01T00:00:00Z",
					images: [],
				},
			],
		}),
		createHero: jest.fn(),
		updateHero: jest.fn(),
		deleteHero: jest.fn(),
		setHeroActive: jest.fn(),
		uploadHeroImage: jest.fn(),
		removeHeroImage: jest.fn(),
	},
}));

describe("AdminHeroRoute", () => {
	it("renders the hero section management page with media and seo fields", async () => {
		render(<AdminHeroRoute />);
		expect(screen.getAllByText("Hero Section").length).toBeGreaterThan(0);
		expect(
			screen.getByText(
				"Customize the storefront banner and promotional content",
			),
		).toBeInTheDocument();
		expect(await screen.findByText("Media upload")).toBeInTheDocument();
		expect(screen.getByText("SEO details")).toBeInTheDocument();
		expect(screen.getByText("Slide editor")).toBeInTheDocument();
	});
});
