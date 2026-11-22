import { describe, expect, it } from "vitest";

import { cacheWriteTokens } from "./cache-write";

describe("cacheWriteTokens", () => {
  it("returns zero for missing or malformed SDK usage", () => {
    expect(cacheWriteTokens(undefined)).toBe(0);
    expect(cacheWriteTokens({ cache_write_tokens: "invalid" })).toBe(0);
  });

  it("keeps a valid cache write count", () => {
    expect(cacheWriteTokens({ cache_write_tokens: 30 })).toBe(30);
  });
});
