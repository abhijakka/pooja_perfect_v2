import { renderHookWithProviders } from "../store/test-utils";
import { useAuth } from "./useAuth";

describe("useAuth", () => {
  it("returns an unauthenticated user", () => {
    const { result } = renderHookWithProviders(() => useAuth());
    expect(result.current).toEqual({ user: null, isAuthenticated: false, isReady: false, sessionExpired: false });
  });
});