import { describe, expect, test } from "bun:test";
import { gatewayToHttpUrl } from "./gateway";

describe("gatewayToHttpUrl", () => {
  test("ws → http", () => {
    expect(gatewayToHttpUrl("ws://localhost:18789")).toBe("http://localhost:18789");
  });

  test("wss → https", () => {
    expect(gatewayToHttpUrl("wss://claw.example.com")).toBe("https://claw.example.com");
  });

  test("preserves path", () => {
    expect(gatewayToHttpUrl("wss://host/path")).toBe("https://host/path");
  });
});
