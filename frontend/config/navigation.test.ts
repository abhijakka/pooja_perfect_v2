import { navigation } from "./navigation";

describe("navigation", () => {
  it("defines the nav links", () => {
    expect(navigation).toEqual([
      { label: "Shop", href: "/products" },
      { label: "Cart", href: "/cart" },
    ]);
  });
});