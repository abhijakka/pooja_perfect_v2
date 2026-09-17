import { cartStorage } from "./cart-storage";

describe("cartStorage", () => {
  it("returns an empty cart", () => {
    expect(cartStorage.get()).toEqual({ items: [] });
  });
});