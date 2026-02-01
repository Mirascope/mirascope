/**
 * Unit tests for shared provider utilities.
 */

import { describe, it, expect } from "vitest";

import { getIncludeThoughts } from "./_utils";

describe("getIncludeThoughts", () => {
  it("returns false when params is empty", () => {
    expect(getIncludeThoughts({})).toBe(false);
  });

  it("returns false when params is undefined", () => {
    expect(getIncludeThoughts()).toBe(false);
  });

  it("returns false when thinking is not set", () => {
    expect(getIncludeThoughts({ maxTokens: 1000 })).toBe(false);
  });

  it("returns false when includeThoughts is not set", () => {
    expect(getIncludeThoughts({ thinking: { level: "medium" } })).toBe(false);
  });

  it("returns true when includeThoughts is true", () => {
    expect(
      getIncludeThoughts({
        thinking: { level: "medium", includeThoughts: true },
      }),
    ).toBe(true);
  });

  it("returns false when includeThoughts is false", () => {
    expect(
      getIncludeThoughts({
        thinking: { level: "medium", includeThoughts: false },
      }),
    ).toBe(false);
  });
});
