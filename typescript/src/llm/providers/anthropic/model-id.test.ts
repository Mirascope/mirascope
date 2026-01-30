import { describe, expect, it } from "vitest";

import type { AnthropicModelId } from "@/llm/providers/anthropic/model-id";

import { modelName } from "@/llm/providers/anthropic/model-id";

describe("model-id", () => {
  describe("AnthropicModelId type", () => {
    it("accepts known model ids", () => {
      const modelId: AnthropicModelId = "anthropic/claude-sonnet-4-5";
      expect(modelId).toBe("anthropic/claude-sonnet-4-5");
    });

    it("accepts custom model ids", () => {
      const modelId: AnthropicModelId = "anthropic/my-custom-model";
      expect(modelId).toBe("anthropic/my-custom-model");
    });
  });

  describe("modelName", () => {
    it("removes anthropic/ prefix", () => {
      expect(modelName("anthropic/claude-sonnet-4-5")).toBe(
        "claude-sonnet-4-5",
      );
    });

    it("removes anthropic-beta/ prefix", () => {
      expect(modelName("anthropic-beta/claude-sonnet-4-5")).toBe(
        "claude-sonnet-4-5",
      );
    });

    it("returns model name unchanged if no prefix", () => {
      expect(modelName("claude-sonnet-4-5")).toBe("claude-sonnet-4-5");
    });

    it("handles nested prefixes by removing first one", () => {
      expect(modelName("anthropic/anthropic/model")).toBe("anthropic/model");
    });
  });
});
