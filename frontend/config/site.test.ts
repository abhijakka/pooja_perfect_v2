import { siteConfig } from "./site";

describe("siteConfig", () => {
  it("defines the site config", () => {
    expect(siteConfig.name).toBe("PoojaPoint");
    expect(siteConfig.url).toMatch(/^https?:\/\//);
  });
});