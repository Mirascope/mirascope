import { describe, it, expect } from "vitest";

import { extractClawId, startupErrorHint } from "./utils";

describe("extractClawId", () => {
  it("extracts clawId from standard hostname", () => {
    expect(extractClawId("abc-123.claws.mirascope.com")).toBe("abc-123");
  });

  it("extracts clawId from hostname with port", () => {
    // Host header can include port
    expect(extractClawId("abc-123.claws.mirascope.com:443")).toBe("abc-123");
  });

  it("extracts UUID-style clawId", () => {
    expect(
      extractClawId("550e8400-e29b-41d4-a716-446655440000.claws.mirascope.com"),
    ).toBe("550e8400-e29b-41d4-a716-446655440000");
  });

  it("returns null for single-part host (no dots)", () => {
    expect(extractClawId("localhost")).toBeNull();
  });

  it("returns null for empty string", () => {
    expect(extractClawId("")).toBeNull();
  });

  it("returns null if first segment is empty (leading dot)", () => {
    expect(extractClawId(".claws.mirascope.com")).toBeNull();
  });

  it("handles two-part hostname", () => {
    expect(extractClawId("claw-1.localhost")).toBe("claw-1");
  });
});

describe("startupErrorHint", () => {
  it("hints about API key for auth-related errors", () => {
    expect(startupErrorHint("Missing API key for OpenAI")).toContain("API key");
    expect(startupErrorHint("401 Unauthorized")).toContain("API key");
  });

  it("hints about memory for OOM errors", () => {
    expect(startupErrorHint("Process killed: out of memory")).toContain(
      "out of memory",
    );
    expect(startupErrorHint("Container OOM killed")).toContain("out of memory");
  });

  it("hints about crashes for connection refused", () => {
    expect(startupErrorHint("ECONNREFUSED 127.0.0.1:8080")).toContain(
      "crashed",
    );
  });

  it("returns undefined for unknown errors", () => {
    expect(startupErrorHint("Something weird happened")).toBeUndefined();
  });
});
