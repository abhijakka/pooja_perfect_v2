import { SITE_NAME } from "./constants";

describe("constants", () => {
  it("exposes the site name", () => {
    expect(SITE_NAME).toBe("PoojaPoint");
  });
});