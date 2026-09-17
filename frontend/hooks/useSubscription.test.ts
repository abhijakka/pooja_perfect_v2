import { renderHookWithProviders } from "../store/test-utils";
import { useSubscription } from "./useSubscription";

describe("useSubscription", () => {
  it("returns an empty subscription list", () => {
    const { result } = renderHookWithProviders(() => useSubscription());
    expect(result.current.subscriptions).toEqual([]);
  });
});