import { SocketManager } from "./socket-manager";

describe("SocketManager", () => {
  it("disconnects without throwing", () => {
    expect(() => new SocketManager().disconnect()).not.toThrow();
  });
});