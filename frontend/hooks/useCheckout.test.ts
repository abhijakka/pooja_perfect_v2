import { renderHookWithProviders } from "../store/test-utils";
import { useCheckout } from "./useCheckout";

describe("useCheckout", () => {
  it("returns an idle checkout state", () => {
    const { result } = renderHookWithProviders(() => useCheckout());
    expect(result.current.isSubmitting).toBe(false);
    expect(typeof result.current.submit).toBe("function");
  });
});