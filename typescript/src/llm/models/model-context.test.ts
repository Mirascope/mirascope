import { describe, expect, it } from "vitest";

import { Model } from "@/llm/models/model";
import {
  createBrowserStorage,
  createStorage,
  modelFromContext,
  useModel,
  withModel,
} from "@/llm/models/model-context";

describe("modelFromContext", () => {
  it("returns undefined when no context is set", () => {
    expect(modelFromContext()).toBeUndefined();
  });

  it("returns the model when inside withModel", () => {
    const model = new Model("anthropic/claude-sonnet-4-20250514");

    withModel(model, () => {
      expect(modelFromContext()).toBe(model);
    });
  });

  it("returns undefined after withModel completes", () => {
    const model = new Model("anthropic/claude-sonnet-4-20250514");

    withModel(model, () => {
      // Context is set here
    });

    expect(modelFromContext()).toBeUndefined();
  });
});

describe("withModel", () => {
  it("returns the result of the function", () => {
    const model = new Model("anthropic/claude-sonnet-4-20250514");

    const result = withModel(model, () => "test-result");

    expect(result).toBe("test-result");
  });

  it("returns the result of an async function", async () => {
    const model = new Model("anthropic/claude-sonnet-4-20250514");

    const result = await withModel(model, async () => {
      await Promise.resolve();
      return "async-result";
    });

    expect(result).toBe("async-result");
  });

  it("maintains context through async/await", async () => {
    const model = new Model("anthropic/claude-sonnet-4-20250514");

    await withModel(model, async () => {
      expect(modelFromContext()).toBe(model);
      await Promise.resolve();
      expect(modelFromContext()).toBe(model);
    });
  });

  it("handles nested contexts correctly", () => {
    const outerModel = new Model("anthropic/claude-sonnet-4-20250514");
    const innerModel = new Model("openai/gpt-4o");

    withModel(outerModel, () => {
      expect(modelFromContext()).toBe(outerModel);

      withModel(innerModel, () => {
        expect(modelFromContext()).toBe(innerModel);
      });

      // Should restore to outer model
      expect(modelFromContext()).toBe(outerModel);
    });

    // Should be undefined outside
    expect(modelFromContext()).toBeUndefined();
  });

  it("handles nested async contexts correctly", async () => {
    const outerModel = new Model("anthropic/claude-sonnet-4-20250514");
    const innerModel = new Model("openai/gpt-4o");

    await withModel(outerModel, async () => {
      expect(modelFromContext()).toBe(outerModel);

      await withModel(innerModel, async () => {
        expect(modelFromContext()).toBe(innerModel);
        await Promise.resolve();
        expect(modelFromContext()).toBe(innerModel);
      });

      // Should restore to outer model
      expect(modelFromContext()).toBe(outerModel);
    });

    // Should be undefined outside
    expect(modelFromContext()).toBeUndefined();
  });

  it("cleans up context on error", () => {
    const model = new Model("anthropic/claude-sonnet-4-20250514");

    expect(() =>
      withModel(model, () => {
        throw new Error("test error");
      }),
    ).toThrow("test error");

    // Context should be cleaned up
    expect(modelFromContext()).toBeUndefined();
  });

  it("cleans up context on async error", async () => {
    const model = new Model("anthropic/claude-sonnet-4-20250514");

    await expect(
      withModel(model, async () => {
        await Promise.resolve();
        throw new Error("async error");
      }),
    ).rejects.toThrow("async error");

    // Context should be cleaned up
    expect(modelFromContext()).toBeUndefined();
  });

  it("allows reusing the same model instance", () => {
    const model = new Model("anthropic/claude-sonnet-4-20250514");

    // Same model nested
    withModel(model, () => {
      expect(modelFromContext()).toBe(model);

      withModel(model, () => {
        expect(modelFromContext()).toBe(model);
      });

      expect(modelFromContext()).toBe(model);
    });

    expect(modelFromContext()).toBeUndefined();
  });
});

describe("useModel", () => {
  it("returns the provided model when no context is set", () => {
    const model = new Model("anthropic/claude-sonnet-4-20250514");

    const result = useModel(model);

    expect(result).toBe(model);
  });

  it("creates a new Model from string when no context is set", () => {
    const result = useModel("openai/gpt-4o");

    expect(result).toBeInstanceOf(Model);
    expect(result.modelId).toBe("openai/gpt-4o");
  });

  it("creates a Model with params from string when no context is set", () => {
    const result = useModel("openai/gpt-4o", { temperature: 0.7 });

    expect(result).toBeInstanceOf(Model);
    expect(result.modelId).toBe("openai/gpt-4o");
    expect(result.params).toEqual({ temperature: 0.7 });
  });

  it("returns context model when context is set (string argument)", () => {
    const contextModel = new Model("anthropic/claude-sonnet-4-20250514");

    withModel(contextModel, () => {
      const result = useModel("openai/gpt-4o");

      // Should return context model, not create a new one
      expect(result).toBe(contextModel);
      expect(result.modelId).toBe("anthropic/claude-sonnet-4-20250514");
    });
  });

  it("returns context model when context is set (Model argument)", () => {
    const contextModel = new Model("anthropic/claude-sonnet-4-20250514");
    const providedModel = new Model("openai/gpt-4o");

    withModel(contextModel, () => {
      const result = useModel(providedModel);

      // Should return context model, not the provided one
      expect(result).toBe(contextModel);
      expect(result.modelId).toBe("anthropic/claude-sonnet-4-20250514");
    });
  });

  it("ignores params when context is set", () => {
    const contextModel = new Model("anthropic/claude-sonnet-4-20250514", {
      temperature: 0.5,
    });

    withModel(contextModel, () => {
      // Params should be ignored since context model is returned
      const result = useModel("openai/gpt-4o", { temperature: 0.9 });

      expect(result).toBe(contextModel);
      expect(result.params).toEqual({ temperature: 0.5 });
    });
  });
});

describe("integration", () => {
  it("context model takes precedence in nested useModel calls", () => {
    const outerModel = new Model("anthropic/claude-sonnet-4-20250514");
    const innerModel = new Model("openai/gpt-4o");
    const fallbackModel = new Model("google/gemini-2.0-flash");

    withModel(outerModel, () => {
      expect(useModel(fallbackModel)).toBe(outerModel);

      withModel(innerModel, () => {
        expect(useModel(fallbackModel)).toBe(innerModel);
      });

      expect(useModel(fallbackModel)).toBe(outerModel);
    });

    expect(useModel(fallbackModel)).toBe(fallbackModel);
  });

  it("works with multiple sequential withModel calls", async () => {
    const modelA = new Model("anthropic/claude-sonnet-4-20250514");
    const modelB = new Model("openai/gpt-4o");

    await withModel(modelA, async () => {
      expect(modelFromContext()).toBe(modelA);
      await Promise.resolve();
    });

    expect(modelFromContext()).toBeUndefined();

    await withModel(modelB, async () => {
      expect(modelFromContext()).toBe(modelB);
      await Promise.resolve();
    });

    expect(modelFromContext()).toBeUndefined();
  });
});

/**
 * Tests for createStorage auto-detection.
 *
 * Note: The fallback to browser storage when AsyncLocalStorage is unavailable
 * is tested indirectly through the createBrowserStorage tests below.
 * The createStorage function uses try/catch to fall back, and since we're
 * running in Node.js, the Node.js path is always taken.
 *
 * The browser fallback behavior is verified by:
 * 1. Direct tests of createBrowserStorage (below)
 * 2. The fact that createStorage delegates to createBrowserStorage on error
 */
describe("createStorage", () => {
  it("creates working storage in Node.js environment", () => {
    // In Node.js, createStorage should return AsyncLocalStorage-based storage
    const storage = createStorage<string>();

    expect(storage.get()).toBeUndefined();

    const result = storage.run("test-value", () => storage.get());
    expect(result).toBe("test-value");

    expect(storage.get()).toBeUndefined();
  });

  it("handles nested runs correctly", () => {
    const storage = createStorage<string>();

    storage.run("outer", () => {
      expect(storage.get()).toBe("outer");

      storage.run("inner", () => {
        expect(storage.get()).toBe("inner");
      });

      expect(storage.get()).toBe("outer");
    });

    expect(storage.get()).toBeUndefined();
  });
});

/**
 * Tests for the browser fallback storage implementation.
 *
 * These tests verify the stack-based storage used in browser environments
 * where AsyncLocalStorage is not available.
 */
describe("createBrowserStorage (browser fallback)", () => {
  it("returns undefined when empty", () => {
    const storage = createBrowserStorage<string>();

    expect(storage.get()).toBeUndefined();
  });

  it("stores and retrieves values via run", () => {
    const storage = createBrowserStorage<string>();

    const result = storage.run("test-value", () => {
      return storage.get();
    });

    expect(result).toBe("test-value");
  });

  it("cleans up after synchronous run completes", () => {
    const storage = createBrowserStorage<string>();

    storage.run("test-value", () => {
      // Value is set during run
    });

    expect(storage.get()).toBeUndefined();
  });

  it("handles nested synchronous runs correctly", () => {
    const storage = createBrowserStorage<string>();

    storage.run("outer", () => {
      expect(storage.get()).toBe("outer");

      storage.run("inner", () => {
        expect(storage.get()).toBe("inner");
      });

      // Should restore to outer value
      expect(storage.get()).toBe("outer");
    });

    expect(storage.get()).toBeUndefined();
  });

  it("cleans up after async run completes", async () => {
    const storage = createBrowserStorage<string>();

    await storage.run("async-value", async () => {
      expect(storage.get()).toBe("async-value");
      await Promise.resolve();
      expect(storage.get()).toBe("async-value");
    });

    expect(storage.get()).toBeUndefined();
  });

  it("cleans up on synchronous error", () => {
    const storage = createBrowserStorage<string>();

    expect(() =>
      storage.run("error-value", () => {
        throw new Error("test error");
      }),
    ).toThrow("test error");

    expect(storage.get()).toBeUndefined();
  });

  it("cleans up on async error", async () => {
    const storage = createBrowserStorage<string>();

    await expect(
      storage.run("async-error-value", async () => {
        await Promise.resolve();
        throw new Error("async error");
      }),
    ).rejects.toThrow("async error");

    expect(storage.get()).toBeUndefined();
  });

  it("handles nested async runs", async () => {
    const storage = createBrowserStorage<string>();

    await storage.run("outer-async", async () => {
      expect(storage.get()).toBe("outer-async");

      await storage.run("inner-async", async () => {
        expect(storage.get()).toBe("inner-async");
        await Promise.resolve();
      });

      expect(storage.get()).toBe("outer-async");
    });

    expect(storage.get()).toBeUndefined();
  });
});
