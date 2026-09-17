import { environment, resolveApiUrl } from "./environment";

describe("environment", () => {
  it("defaults to the local backend API URL", () => {
    expect(environment.apiUrl).toBe("http://localhost:8000");
  });

  it("derives the API URL from a LAN host so mobile devices work", () => {
    expect(resolveApiUrl("192.168.1.34", "http:")).toBe("http://192.168.1.34:8000");
  });

  it("keeps localhost for local access", () => {
    expect(resolveApiUrl("localhost", "http:")).toBe("http://localhost:8000");
    expect(resolveApiUrl("127.0.0.1", "http:")).toBe("http://localhost:8000");
  });
});