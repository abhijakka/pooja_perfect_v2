import { productSchema } from "./product-schema";

describe("productSchema", () => {
  it("builds a product schema", () => {
    expect(productSchema({ name: "Diya", price: 349 })).toEqual({
      "@type": "Product",
      name: "Diya",
      offers: { price: 349, priceCurrency: "INR" },
    });
  });
});