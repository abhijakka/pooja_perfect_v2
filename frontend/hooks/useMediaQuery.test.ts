import { useMediaQuery } from "./useMediaQuery";

describe("useMediaQuery", () => {
  it("returns false for any query", () => {
    expect(useMediaQuery("(min-width: 768px)")).toBe(false);
  });
});