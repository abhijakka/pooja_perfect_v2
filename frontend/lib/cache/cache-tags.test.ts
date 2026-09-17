import { cacheTags } from "./cache-tags";

describe("cacheTags", () => {
  it("defines the cache tags", () => {
    expect(cacheTags).toEqual({ products: "products", categories: "categories", subscriptions: "subscriptions" });
  });
});