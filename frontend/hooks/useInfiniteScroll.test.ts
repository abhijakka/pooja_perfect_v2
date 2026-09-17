import { useInfiniteScroll } from "./useInfiniteScroll";

describe("useInfiniteScroll", () => {
  it("exposes a loadMore function", () => {
    expect(typeof useInfiniteScroll().loadMore).toBe("function");
  });
});