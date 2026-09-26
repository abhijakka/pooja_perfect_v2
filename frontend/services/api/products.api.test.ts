import { environment } from "../../config/environment";
import { categoryNameFor, categorySlugFor, productsApi } from "./products.api";

jest.mock("../../config/environment", () => ({
	environment: { apiUrl: "" },
}));

const product = {
	id: "b454f667-5341-4852-bcf3-e6d688462406",
	name: "Brass Pooja Diya",
	slug: "sdfg",
	price: "549.00",
	originalPrice: "699.00",
	discountPrice: null,
	averageRating: "4.50",
	reviewCount: 12,
	isFeatured: true,
	stock: 10,
	categoryId: "07d7a289-918a-473e-a770-cf7909d8f0bd",
	shortDescription: "A warm brass diya",
	description: "Long description",
	images: [{ url: "/diya.png", isPrimary: true }],
};

describe("productsApi", () => {
	const fetchMock = jest.fn();

	beforeEach(() => {
		global.fetch = fetchMock as unknown as typeof fetch;
		fetchMock.mockReset();
		environment.apiUrl = "http://localhost:8000";
		fetchMock.mockResolvedValue({
			ok: true,
			status: 200,
			json: async () => ({
				data: {
					product,
					categories: [
						{ id: "07d7a289-918a-473e-a770-cf7909d8f0bd", name: "Pooja Essentials", slug: "pooja" },
					],
				},
			}),
		});
	});

	function lastRequest() {
		const [, init] = fetchMock.mock.calls[fetchMock.mock.calls.length - 1];
		return JSON.parse(init.body as string);
	}

	it("fetches a single product by slug from the public GraphQL endpoint", async () => {
		const { product: result } = await productsApi.bySlug("sdfg");
		expect(result.slug).toBe("sdfg");
		expect(lastRequest().query).toContain("product(slug: $slug)");
		expect(lastRequest().variables).toEqual({ slug: "sdfg" });
		expect(lastRequest().query).toContain("categories { id name slug }");
	});

	it("posts to /graphql so no duplicate product endpoint is introduced", async () => {
		await productsApi.bySlug("sdfg");
		expect(fetchMock.mock.calls[0][0]).toBe("http://localhost:8000/graphql");
	});

	it("keeps the list query working with the shared field selection", async () => {
		fetchMock.mockResolvedValue({
			ok: true,
			status: 200,
			json: async () => ({ data: { products: { items: [product], pagination: { total: 1 } } } }),
		});
		const { products } = await productsApi.list({ page: 1, pageSize: 20 });
		expect(products.items).toHaveLength(1);
		expect(lastRequest().query).toContain("items {");
	});
});

describe("category resolution", () => {
	const categories = [{ id: "cat-1", name: "Divine Idols", slug: "idols" }];

	it("resolves a real category name and slug from the product categoryId", () => {
		expect(categoryNameFor(categories, "cat-1")).toBe("Divine Idols");
		expect(categorySlugFor(categories, "cat-1")).toBe("idols");
	});

	it("falls back without throwing for an unknown categoryId", () => {
		expect(categoryNameFor(categories, "missing")).toBe("Pooja Essentials");
		expect(categorySlugFor(categories, null)).toBe("pooja");
	});
});
