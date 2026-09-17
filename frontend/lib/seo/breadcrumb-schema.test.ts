import { breadcrumbSchema } from "./breadcrumb-schema";

describe("breadcrumbSchema", () => {
  it("builds a breadcrumb list with 1-based positions", () => {
    expect(breadcrumbSchema(["Home", "Products"])).toEqual({
      "@type": "BreadcrumbList",
      itemListElement: [
        { "@type": "ListItem", name: "Home", position: 1 },
        { "@type": "ListItem", name: "Products", position: 2 },
      ],
    });
  });
});