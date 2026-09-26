import ProductPage, { generateMetadata } from "./page";
import { productsApi } from "../../../../services/api/products.api";

const notFoundMock = jest.fn(() => {
	throw new Error("NEXT_NOT_FOUND");
});

jest.mock("next/navigation", () => ({ notFound: () => notFoundMock() }));
jest.mock("../../../../services/api/products.api", () => ({
	productsApi: { bySlug: jest.fn() },
	categoryNameFor: jest.requireActual("../../../../services/api/products.api").categoryNameFor,
	categorySlugFor: jest.requireActual("../../../../services/api/products.api").categorySlugFor,
}));
jest.mock("./ProductDetailPage", () => ({
	__esModule: true,
	default: ({ product }: { product: { slug: string; name: string } }) => (
		<div data-testid="detail">{product.name}</div>
	),
}));

const mocked = productsApi as jest.Mocked<typeof productsApi>;

const backendProduct = {
	id: "b454f667-5341-4852-bcf3-e6d688462406",
	name: "Brass Pooja Diya",
	slug: "sdfg",
	price: "549.00",
	originalPrice: "699.00",
	discountPrice: null,
	averageRating: "4.50",
	reviewCount: 3,
	isFeatured: true,
	stock: 10,
	categoryId: "cat-1",
	shortDescription: null,
	description: null,
	images: [{ url: "/diya.png", isPrimary: true }],
};

const params = (slug: string) => ({ params: Promise.resolve({ slug }) });

describe("/products/[slug]", () => {
	beforeEach(() => jest.clearAllMocks());

	it("renders a real catalog product fetched by slug from the backend", async () => {
		mocked.bySlug.mockResolvedValue({
			product: backendProduct,
			categories: [{ id: "cat-1", name: "Divine Idols", slug: "idols" }],
		});

		await expect(ProductPage(params("sdfg"))).resolves.toBeTruthy();
		expect(mocked.bySlug).toHaveBeenCalledWith("sdfg");
		expect(notFoundMock).not.toHaveBeenCalled();
	});

	it("404s only when the backend has no such product and no demo entry exists", async () => {
		mocked.bySlug.mockRejectedValue(Object.assign(new Error("not found"), { name: "GraphQLError" }));

		await expect(ProductPage(params("no-such-product"))).rejects.toThrow("NEXT_NOT_FOUND");
		expect(notFoundMock).toHaveBeenCalled();
	});

	it("falls back to the documented demo catalog when the backend is unavailable", async () => {
		mocked.bySlug.mockRejectedValue(new Error("network down"));

		await expect(ProductPage(params("premium-brass-pooja-diya"))).resolves.toBeTruthy();
		expect(notFoundMock).not.toHaveBeenCalled();
	});

	it("builds metadata from the backend product", async () => {
		mocked.bySlug.mockResolvedValue({
			product: backendProduct,
			categories: [{ id: "cat-1", name: "Divine Idols", slug: "idols" }],
		});

		const metadata = await generateMetadata(params("sdfg"));
		expect(metadata.title).toBe("Brass Pooja Diya | PoojaPoint");
		expect(metadata.description).toContain("Divine Idols");
	});
});
