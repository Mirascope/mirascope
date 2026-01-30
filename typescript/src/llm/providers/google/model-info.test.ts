import { describe, expect, it } from "vitest";

import type { GoogleKnownModels } from "@/llm/providers/google/model-info";

import { MODELS_WITHOUT_STRUCTURED_OUTPUT_AND_TOOLS_SUPPORT } from "@/llm/providers/google/model-info";

describe("GoogleKnownModels type", () => {
  it("accepts known model ID", () => {
    const modelId: GoogleKnownModels = "google/gemini-2.0-flash";

    expect(modelId).toBe("google/gemini-2.0-flash");
  });
});

describe("MODELS_WITHOUT_STRUCTURED_OUTPUT_AND_TOOLS_SUPPORT", () => {
  it("is a ReadonlySet", () => {
    expect(MODELS_WITHOUT_STRUCTURED_OUTPUT_AND_TOOLS_SUPPORT).toBeInstanceOf(
      Set,
    );
  });

  it("contains model IDs without google/ prefix", () => {
    // The set should contain raw model names, not prefixed ones
    for (const modelId of MODELS_WITHOUT_STRUCTURED_OUTPUT_AND_TOOLS_SUPPORT) {
      expect(modelId).not.toMatch(/^google\//);
    }
  });

  it("can check if a model lacks support", () => {
    // This tests the interface, not specific models (which may change)
    const hasMethod =
      typeof MODELS_WITHOUT_STRUCTURED_OUTPUT_AND_TOOLS_SUPPORT.has ===
      "function";

    expect(hasMethod).toBe(true);
  });
});
