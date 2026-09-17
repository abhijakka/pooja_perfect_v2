import { useDebounce } from "./useDebounce";

describe("useDebounce", () => {
  it("returns the value unchanged", () => {
    expect(useDebounce("diya", 300)).toBe("diya");
  });
});