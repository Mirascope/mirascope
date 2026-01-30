import { describe, expect, it } from "vitest";

import type { GoogleModelId } from "@/llm/providers/google/model-id";

import { modelName } from "@/llm/providers/google/model-id";

describe("modelName", () => {
  it("removes google/ prefix from known model", () => {
    const modelId: GoogleModelId = "google/gemini-2.0-flash";

    expect(modelName(modelId)).toBe("gemini-2.0-flash");
  });

  it("removes google/ prefix from custom model", () => {
    const modelId: GoogleModelId = "google/custom-model";

    expect(modelName(modelId)).toBe("custom-model");
  });

  it("handles model without prefix", () => {
    const modelId: GoogleModelId = "gemini-2.0-flash";

    expect(modelName(modelId)).toBe("gemini-2.0-flash");
  });

  it("preserves full model name after prefix removal", () => {
    const modelId: GoogleModelId =
      "google/gemini-2.5-flash-lite-preview-09-2025";

    expect(modelName(modelId)).toBe("gemini-2.5-flash-lite-preview-09-2025");
  });
});

describe("GoogleModelId type", () => {
  it("accepts known model IDs", () => {
    const modelId: GoogleModelId = "google/gemini-2.0-flash";

    expect(modelId).toBe("google/gemini-2.0-flash");
  });

  it("accepts custom string model IDs", () => {
    const modelId: GoogleModelId = "google/my-custom-model";

    expect(modelId).toBe("google/my-custom-model");
  });
});
