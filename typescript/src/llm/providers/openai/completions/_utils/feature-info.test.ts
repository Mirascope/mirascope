/**
 * Tests for CompletionsModelFeatureInfo and featureInfoForOpenAIModel.
 */

import { describe, expect, it } from "vitest";

import {
  EMPTY_FEATURE_INFO,
  featureInfoForOpenAIModel,
} from "@/llm/providers/openai/completions/_utils/feature-info";

describe("CompletionsModelFeatureInfo", () => {
  describe("EMPTY_FEATURE_INFO", () => {
    it("has all undefined fields", () => {
      expect(EMPTY_FEATURE_INFO.audioSupport).toBeUndefined();
      expect(EMPTY_FEATURE_INFO.strictSupport).toBeUndefined();
      expect(EMPTY_FEATURE_INFO.jsonObjectSupport).toBeUndefined();
      expect(EMPTY_FEATURE_INFO.isReasoningModel).toBeUndefined();
    });

    it("is frozen", () => {
      expect(Object.isFrozen(EMPTY_FEATURE_INFO)).toBe(true);
    });
  });

  describe("featureInfoForOpenAIModel", () => {
    it("returns correct info for gpt-4o (modern model)", () => {
      const info = featureInfoForOpenAIModel("gpt-4o");
      // gpt-4o does not support audio
      expect(info.audioSupport).toBe(false);
      // gpt-4o supports strict mode
      expect(info.strictSupport).toBe(true);
      // gpt-4o supports json object mode
      expect(info.jsonObjectSupport).toBe(true);
      // gpt-4o is not a reasoning model
      expect(info.isReasoningModel).toBe(false);
    });

    it("returns correct info for gpt-4 (legacy model)", () => {
      const info = featureInfoForOpenAIModel("gpt-4");
      // gpt-4 does not support audio
      expect(info.audioSupport).toBe(false);
      // gpt-4 does not support strict mode
      expect(info.strictSupport).toBe(false);
      // gpt-4 does not support json object mode
      expect(info.jsonObjectSupport).toBe(false);
      // gpt-4 is not a reasoning model
      expect(info.isReasoningModel).toBe(false);
    });

    it("returns correct info for o1 (reasoning model)", () => {
      const info = featureInfoForOpenAIModel("o1");
      // o1 does not support audio
      expect(info.audioSupport).toBe(false);
      // o1 supports strict mode
      expect(info.strictSupport).toBe(true);
      // o1 supports json object mode
      expect(info.jsonObjectSupport).toBe(true);
      // o1 IS a reasoning model
      expect(info.isReasoningModel).toBe(true);
    });

    it("returns correct info for o3-mini (reasoning model)", () => {
      const info = featureInfoForOpenAIModel("o3-mini");
      // o3-mini is a reasoning model
      expect(info.isReasoningModel).toBe(true);
    });

    it("returns correct info for gpt-4o-search-preview (search model)", () => {
      const info = featureInfoForOpenAIModel("gpt-4o-search-preview");
      // Search models don't support json object mode
      expect(info.jsonObjectSupport).toBe(false);
    });

    it("returns optimistic defaults for unknown model", () => {
      const info = featureInfoForOpenAIModel("unknown-future-model");
      // Unknown models get optimistic defaults (not in any exclusion set)
      expect(info.audioSupport).toBe(true);
      expect(info.strictSupport).toBe(true);
      expect(info.jsonObjectSupport).toBe(true);
      expect(info.isReasoningModel).toBe(true);
    });
  });
});
