import { act, renderHook, waitFor } from "@testing-library/react";
import { Provider } from "react-redux";
import { makeStore } from "../store";
import { useCart } from "./useCart";
import { cartApi } from "../services/api/cart.api";

jest.mock("../services/api/cart.api", () => {
	const actual = jest.requireActual("../services/api/cart.api");
	return { ...actual, cartApi: { get: jest.fn(), add: jest.fn(), update: jest.fn(), remove: jest.fn(), clear: jest.fn() } };
});

const PRODUCT_ID = "b454f667-5341-4852-bcf3-e6d688462406";

const product = {
	id: PRODUCT_ID,
	name: "Brass Pooja Diya",
	price: 549,
	oldPrice: 699,
	rating: "4.5",
	category: "pooja",
	categoryLabel: "Pooja Essentials",
	slug: "sdfg",
	image: "/diya.png",
};

const serverCart = (quantity: number) => ({
	id: "cart-1",
	itemCount: quantity,
	subtotal: 549 * quantity,
	items: [
		{
			id: "line-1",
			productId: PRODUCT_ID,
			quantity,
			unitPrice: 549,
			product: { id: PRODUCT_ID, name: "Brass Pooja Diya", slug: "sdfg", price: 549, images: [] },
		},
	],
});

function wrapper({ children }: { children: React.ReactNode }) {
	return <Provider store={makeStore()}>{children}</Provider>;
}

const mocked = cartApi as jest.Mocked<typeof cartApi>;

describe("useCart", () => {
	beforeEach(() => jest.clearAllMocks());

	it("persists an add through the backend cart and hydrates from the response", async () => {
		mocked.add.mockResolvedValue({ addToCart: serverCart(2) } as never);
		const { result } = renderHook(() => useCart(), { wrapper });

		act(() => result.current.addItem(product, 2));

		// Optimistic: the badge updates immediately.
		expect(result.current.count).toBe(2);
		expect(mocked.add).toHaveBeenCalledWith(PRODUCT_ID, 2);

		await waitFor(() => expect(result.current.items[0]?.cartItemId).toBe("line-1"));
	});

	it("persists a quantity change by cart line id", async () => {
		mocked.add.mockResolvedValue({ addToCart: serverCart(1) } as never);
		mocked.update.mockResolvedValue({ updateCartItem: serverCart(5) } as never);
		const { result } = renderHook(() => useCart(), { wrapper });

		act(() => result.current.addItem(product));
		await waitFor(() => expect(result.current.items[0]?.cartItemId).toBe("line-1"));

		act(() => result.current.updateQuantity(PRODUCT_ID, 5));

		expect(mocked.update).toHaveBeenCalledWith("line-1", 5);
		await waitFor(() => expect(result.current.count).toBe(5));
	});

	it("persists a removal by cart line id", async () => {
		mocked.add.mockResolvedValue({ addToCart: serverCart(1) } as never);
		mocked.remove.mockResolvedValue({ removeCartItem: { id: "cart-1", itemCount: 0, subtotal: 0, items: [] } } as never);
		const { result } = renderHook(() => useCart(), { wrapper });

		act(() => result.current.addItem(product));
		await waitFor(() => expect(result.current.items[0]?.cartItemId).toBe("line-1"));

		act(() => result.current.removeItem(PRODUCT_ID));

		expect(mocked.remove).toHaveBeenCalledWith("line-1");
		await waitFor(() => expect(result.current.count).toBe(0));
	});

	it("persists a cart clear", async () => {
		mocked.clear.mockResolvedValue({ clearCart: { id: "cart-1", itemCount: 0, subtotal: 0, items: [] } } as never);
		const { result } = renderHook(() => useCart(), { wrapper });

		act(() => result.current.clearCart());

		expect(mocked.clear).toHaveBeenCalledTimes(1);
	});

	it("never sends a non-catalog id to the backend", async () => {
		mocked.add.mockResolvedValue({ addToCart: serverCart(1) } as never);
		const { result } = renderHook(() => useCart(), { wrapper });

		act(() => result.current.addItem({ ...product, id: "diya" }));

		expect(mocked.add).not.toHaveBeenCalled();
		expect(result.current.count).toBe(1);
	});

	it("keeps the optimistic item when the backend is unreachable", async () => {
		mocked.add.mockRejectedValue(new Error("offline"));
		const { result } = renderHook(() => useCart(), { wrapper });

		act(() => result.current.addItem(product));
		await waitFor(() => expect(result.current.count).toBe(1));

		expect(result.current.items[0]?.slug).toBe("sdfg");
	});
});
