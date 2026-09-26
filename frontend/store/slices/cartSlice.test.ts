import cartReducer, { addItem, removeItem, updateQuantity, clearCart, selectCartCount, selectCartTotal } from "./cartSlice";
import { logout } from "./authSlice";

const product = {
  id: "1",
  name: "Brass Diya",
  price: 100,
  oldPrice: 150,
  rating: "4.5",
  category: "pooja",
  categoryLabel: "Pooja",
  slug: "brass-diya",
  image: "/diya.jpg",
};

describe("cartSlice", () => {
  it("adds a new item", () => {
    const state = cartReducer(undefined, addItem({ product }));
    expect(state.items).toHaveLength(1);
    expect(state.items[0].quantity).toBe(1);
  });

  it("merges an existing item with quantity", () => {
    let state = cartReducer(undefined, addItem({ product }));
    state = cartReducer(state, addItem({ product, quantity: 2 }));
    expect(state.items).toHaveLength(1);
    expect(state.items[0].quantity).toBe(3);
  });

  it("clamps quantity to a minimum of 1", () => {
    const state = cartReducer(undefined, addItem({ product, quantity: 0 }));
    expect(state.items[0].quantity).toBe(1);
  });

  it("removes an item", () => {
    let state = cartReducer(undefined, addItem({ product }));
    state = cartReducer(state, removeItem("1"));
    expect(state.items).toHaveLength(0);
  });

  it("updates quantity", () => {
    let state = cartReducer(undefined, addItem({ product }));
    state = cartReducer(state, updateQuantity({ productId: "1", quantity: 5 }));
    expect(state.items[0].quantity).toBe(5);
  });

  it("removes an item when quantity is set to 0", () => {
    let state = cartReducer(undefined, addItem({ product }));
    state = cartReducer(state, updateQuantity({ productId: "1", quantity: 0 }));
    expect(state.items).toHaveLength(0);
  });

  it("clears the cart", () => {
    let state = cartReducer(undefined, addItem({ product }));
    state = cartReducer(state, clearCart());
    expect(state.items).toHaveLength(0);
  });

  it("selects count and total", () => {
    let state = cartReducer(undefined, addItem({ product }));
    state = cartReducer(state, addItem({ product, quantity: 2 }));
    const root = { cart: state } as never;
    expect(selectCartCount(root)).toBe(3);
    expect(selectCartTotal(root)).toBe(300);
  });

  it("drops the cart when the session ends so another visitor never sees it", () => {
    let state = cartReducer(undefined, addItem({ product }));
    state = cartReducer(state, logout());
    expect(state.items).toHaveLength(0);
  });
});