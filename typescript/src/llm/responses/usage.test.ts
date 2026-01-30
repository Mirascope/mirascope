/**
 * Tests for Usage utilities.
 */

import { describe, it, expect } from "vitest";

import { createUsage, totalTokens } from "@/llm/responses/usage";

describe("Usage", () => {
  describe("createUsage()", () => {
    it("creates usage with all defaults", () => {
      const usage = createUsage();
      expect(usage.inputTokens).toBe(0);
      expect(usage.outputTokens).toBe(0);
      expect(usage.cacheReadTokens).toBe(0);
      expect(usage.cacheWriteTokens).toBe(0);
      expect(usage.reasoningTokens).toBe(0);
      expect(usage.raw).toBeNull();
    });

    it("creates usage with provided values", () => {
      const raw = { custom: "data" };
      const usage = createUsage({
        inputTokens: 100,
        outputTokens: 50,
        cacheReadTokens: 20,
        cacheWriteTokens: 10,
        reasoningTokens: 30,
        raw,
      });

      expect(usage.inputTokens).toBe(100);
      expect(usage.outputTokens).toBe(50);
      expect(usage.cacheReadTokens).toBe(20);
      expect(usage.cacheWriteTokens).toBe(10);
      expect(usage.reasoningTokens).toBe(30);
      expect(usage.raw).toBe(raw);
    });

    it("uses defaults for missing fields", () => {
      const usage = createUsage({
        inputTokens: 100,
        outputTokens: 50,
      });

      expect(usage.inputTokens).toBe(100);
      expect(usage.outputTokens).toBe(50);
      expect(usage.cacheReadTokens).toBe(0);
      expect(usage.cacheWriteTokens).toBe(0);
      expect(usage.reasoningTokens).toBe(0);
      expect(usage.raw).toBeNull();
    });
  });

  describe("totalTokens()", () => {
    it("calculates total from input and output tokens", () => {
      const usage = createUsage({
        inputTokens: 100,
        outputTokens: 50,
      });
      expect(totalTokens(usage)).toBe(150);
    });

    it("returns 0 for empty usage", () => {
      const usage = createUsage();
      expect(totalTokens(usage)).toBe(0);
    });
  });
});
