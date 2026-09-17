import wishlistReducer, { add, remove, toggle, selectWishlistCount } from "./wishlistSlice";

describe("wishlistSlice", () => {
  it("adds a product", () => {
    const state = wishlistReducer(undefined, add("1"));
    expect(state.items).toEqual(["1"]);
  });

  it("does not add a duplicate", () => {
    let state = wishlistReducer(undefined, add("1"));
    state = wishlistReducer(state, add("1"));
    expect(state.items).toEqual(["1"]);
  });

  it("removes a product", () => {
    let state = wishlistReducer(undefined, add("1"));
    state = wishlistReducer(state, remove("1"));
    expect(state.items).toEqual([]);
  });

  it("toggles a product on and off", () => {
    let state = wishlistReducer(undefined, toggle("1"));
    expect(state.items).toEqual(["1"]);
    state = wishlistReducer(state, toggle("1"));
    expect(state.items).toEqual([]);
  });

  it("selects the count", () => {
    let state = wishlistReducer(undefined, add("1"));
    state = wishlistReducer(state, add("2"));
    expect(selectWishlistCount({ wishlist: state } as never)).toBe(2);
  });
});