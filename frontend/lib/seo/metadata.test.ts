import { defaultMetadata } from "./metadata";

describe("defaultMetadata", () => {
  it("defines the default metadata", () => {
    expect(defaultMetadata).toEqual({ title: "PoojaPoint", description: "Sacred essentials for modern homes." });
  });
});