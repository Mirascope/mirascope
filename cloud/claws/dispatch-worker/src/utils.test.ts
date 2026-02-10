import { describe, it, expect } from "vitest";

import { extractClawId } from "./utils";

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
