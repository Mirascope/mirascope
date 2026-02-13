import { describe, it, expect } from "vitest";

import { buildGatewayArgs, redactArgs } from "./gateway";

describe("buildGatewayArgs", () => {
  it("builds base args without token", () => {
    const args = buildGatewayArgs();

    expect(args).toEqual([
      "gateway",
      "--port",
      "18789",
      "--verbose",
      "--allow-unconfigured",
      "--bind",
      "lan",
    ]);
  });

  it("appends token args when provided", () => {
    const args = buildGatewayArgs("my-token");

    expect(args).toContain("--token");
    expect(args).toContain("my-token");
    expect(args.indexOf("--token")).toBe(args.length - 2);
    expect(args.indexOf("my-token")).toBe(args.length - 1);
  });
});

describe("redactArgs", () => {
  it("redacts the token value", () => {
    const args = ["gateway", "--token", "secret-123"];
    const redacted = redactArgs(args, "secret-123");

    expect(redacted).toEqual(["gateway", "--token", "***REDACTED***"]);
  });

  it("passes through args when no token", () => {
    const args = ["gateway", "--port", "18789"];
    const redacted = redactArgs(args);

    expect(redacted).toEqual(["gateway", "--port", "18789"]);
  });

  it("does not redact non-matching values", () => {
    const args = ["gateway", "--port", "18789", "--token", "secret"];
    const redacted = redactArgs(args, "secret");

    expect(redacted[2]).toBe("18789");
    expect(redacted[4]).toBe("***REDACTED***");
  });
});
