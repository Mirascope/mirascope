import { describe, expect, test } from "bun:test";
import { parseArgs } from "./args";

describe("parseArgs", () => {
  test("defaults", () => {
    const args = parseArgs([]);
    expect(args.gateway).toBe("ws://localhost:18789");
    expect(args.open).toBe(true);
    expect(args.help).toBe(false);
    expect(args.token).toBeUndefined();
    expect(args.port).toBeUndefined();
  });

  test("--gateway", () => {
    const args = parseArgs(["--gateway", "wss://claw.example.com"]);
    expect(args.gateway).toBe("wss://claw.example.com");
  });

  test("--token", () => {
    const args = parseArgs(["--token", "secret123"]);
    expect(args.token).toBe("secret123");
  });

  test("--port", () => {
    const args = parseArgs(["--port", "9999"]);
    expect(args.port).toBe(9999);
  });

  test("--no-open", () => {
    const args = parseArgs(["--no-open"]);
    expect(args.open).toBe(false);
  });

  test("--help", () => {
    const args = parseArgs(["--help"]);
    expect(args.help).toBe(true);
  });

  test("-h alias", () => {
    const args = parseArgs(["-h"]);
    expect(args.help).toBe(true);
  });

  test("rejects invalid protocol", () => {
    expect(() => parseArgs(["--gateway", "http://localhost"])).toThrow(
      "ws:// or wss://",
    );
  });

  test("rejects invalid URL", () => {
    expect(() => parseArgs(["--gateway", "not-a-url"])).toThrow("Invalid");
  });

  test("rejects invalid port", () => {
    expect(() => parseArgs(["--port", "abc"])).toThrow("valid port");
  });

  test("rejects unknown option", () => {
    expect(() => parseArgs(["--foo"])).toThrow("Unknown");
  });

  test("rejects missing value for --gateway", () => {
    expect(() => parseArgs(["--gateway"])).toThrow("requires a value");
  });

  test("all options together", () => {
    const args = parseArgs([
      "--gateway", "wss://claw.example.com",
      "--token", "tok",
      "--port", "8080",
      "--no-open",
    ]);
    expect(args.gateway).toBe("wss://claw.example.com");
    expect(args.token).toBe("tok");
    expect(args.port).toBe(8080);
    expect(args.open).toBe(false);
  });
});
