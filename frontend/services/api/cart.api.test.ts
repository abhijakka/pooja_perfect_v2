import { environment } from "../../config/environment";
import { cartApi, isBackendProductId, toCartItems } from "./cart.api";

jest.mock("../../config/environment", () => ({
	environment: { apiUrl: "" },
}));

const cartPayload = {
	cart: {
		id: "cart-1",
		itemCount: 2,
		subtotal: 1098,
		items: [
			{
				id: "line-1",
				productId: "b454f66753414852bcf3e6d688462406",
				quantity: 2,
				unitPrice: 549,
				product: {
					id: "b454f66753414852bcf3e6d688462406",
					name: "sdfg",
					slug: "sdfg",
					price: 549,
					images: [{ url: "/primary.png", isPrimary: true }],
				},
			},
		],
	},
};

describe("cartApi", () => {
	const fetchMock = jest.fn();

	beforeEach(() => {
		global.fetch = fetchMock as unknown as typeof fetch;
		fetchMock.mockReset();
		environment.apiUrl = "http://localhost:8000";
	});

	function mockData(data: unknown) {
		fetchMock.mockResolvedValue({ ok: true, status: 200, json: async () => ({ data }) });
	}

	function lastRequest() {
		const [, init] = fetchMock.mock.calls[fetchMock.mock.calls.length - 1];
		return JSON.parse(init.body as string);
	}

	it("reads the cart with cookies so the guest_token cookie is sent", async () => {
		mockData(cartPayload);
		const { cart } = await cartApi.get();
		expect(cart.itemCount).toBe(2);
		const [, init] = fetchMock.mock.calls[0];
		expect(init.credentials).toBe("include");
		expect(lastRequest().query).toContain("query Cart");
	});

	it("adds a product by its UUID and returns the updated cart", async () => {
		mockData({ addToCart: cartPayload.cart });
		const { addToCart } = await cartApi.add("b454f66753414852bcf3e6d688462406", 2);
		expect(addToCart.items[0].quantity).toBe(2);
		expect(lastRequest().variables).toEqual({
			productId: "b454f66753414852bcf3e6d688462406",
			quantity: 2,
		});
		expect(lastRequest().query).toContain("mutation AddToCart");
	});

	it("updates, removes and clears by cart line id", async () => {
		mockData({ updateCartItem: cartPayload.cart });
		await cartApi.update("line-1", 3);
		expect(lastRequest().variables).toEqual({ itemId: "line-1", quantity: 3 });
		mockData({ removeCartItem: cartPayload.cart });
		await cartApi.remove("line-1");
		expect(lastRequest().variables).toEqual({ itemId: "line-1" });
		mockData({ clearCart: cartPayload.cart });
		await cartApi.clear();
		expect(lastRequest().query).toContain("mutation ClearCart");
	});
});

describe("toCartItems", () => {
	it("keeps the cart line id separate from the product id and the slug", () => {
		const [item] = toCartItems(cartPayload.cart);
		expect(item.id).toBe("b454f66753414852bcf3e6d688462406");
		expect(item.cartItemId).toBe("line-1");
		expect(item.slug).toBe("sdfg");
		expect(item.quantity).toBe(2);
		expect(item.image).toBe("/primary.png");
	});

	it("never substitutes a cart line id for a missing product slug", () => {
		const [item] = toCartItems({
			id: "cart-1",
			itemCount: 1,
			subtotal: 0,
			items: [{ id: "line-9", productId: "prod-9", quantity: 1, unitPrice: 10, product: null }],
		});
		expect(item.slug).toBe("");
		expect(item.id).toBe("prod-9");
		expect(item.cartItemId).toBe("line-9");
	});

	it("returns an empty list for a missing cart", () => {
		expect(toCartItems(null)).toEqual([]);
		expect(toCartItems(undefined)).toEqual([]);
	});
});

describe("isBackendProductId", () => {
	it("accepts a UUID and rejects demo or generated ids", () => {
		expect(isBackendProductId("b454f667-5341-4852-bcf3-e6d688462406")).toBe(true);
		expect(isBackendProductId("b454f66753414852bcf3e6d688462406")).toBe(true);
		expect(isBackendProductId("diya")).toBe(false);
		expect(isBackendProductId("sub-1_day-1758800000000")).toBe(false);
		expect(isBackendProductId(undefined)).toBe(false);
	});
});
