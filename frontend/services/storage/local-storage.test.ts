import { localStorageService } from "./local-storage";

describe("localStorageService", () => {
  it("returns null for missing keys", () => {
    expect(localStorageService.get("missing")).toBeNull();
  });
});