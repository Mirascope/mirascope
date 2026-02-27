/**
 * Tests for LLM instrumentation entry point.
 */

import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";

import {
  instrumentLLM,
  uninstrumentLLM,
  isLLMInstrumented,
  resetInstrumentationState,
} from "./llm";
import { unwrapAllModelMethods, isModelInstrumented } from "./model";

// Mock the configuration module
vi.mock("@/ops/_internal/configuration", () => ({
  getTracer: vi.fn(),
}));

import { getTracer } from "@/ops/_internal/configuration";

describe("LLM Instrumentation", () => {
  beforeEach(() => {
    // Reset state before each test
    resetInstrumentationState();
    unwrapAllModelMethods();
    vi.clearAllMocks();
  });

  afterEach(() => {
    // Clean up after each test
    uninstrumentLLM();
  });

  describe("instrumentLLM", () => {
    it("throws error if configure() was not called", () => {
      vi.mocked(getTracer).mockReturnValue(null);

      expect(() => instrumentLLM()).toThrow(
        "You must call configure() before calling instrumentLLM()",
      );
    });

    it("instruments model methods when tracer is configured", () => {
      const mockTracer = {} as ReturnType<typeof getTracer>;
      vi.mocked(getTracer).mockReturnValue(mockTracer);

      expect(isModelInstrumented()).toBe(false);

      instrumentLLM();

      expect(isModelInstrumented()).toBe(true);
    });

    it("is idempotent - calling multiple times has no additional effect", () => {
      const mockTracer = {} as ReturnType<typeof getTracer>;
      vi.mocked(getTracer).mockReturnValue(mockTracer);

      instrumentLLM();
      instrumentLLM();
      instrumentLLM();

      expect(isLLMInstrumented()).toBe(true);
      // Should still be instrumented, not errored
    });
  });

  describe("uninstrumentLLM", () => {
    it("removes instrumentation", () => {
      const mockTracer = {} as ReturnType<typeof getTracer>;
      vi.mocked(getTracer).mockReturnValue(mockTracer);

      instrumentLLM();
      expect(isLLMInstrumented()).toBe(true);

      uninstrumentLLM();
      expect(isLLMInstrumented()).toBe(false);
    });

    it("is idempotent - calling when not instrumented is a no-op", () => {
      expect(isLLMInstrumented()).toBe(false);

      uninstrumentLLM();
      uninstrumentLLM();

      expect(isLLMInstrumented()).toBe(false);
      // Should not error
    });
  });

  describe("isLLMInstrumented", () => {
    it("returns false initially", () => {
      expect(isLLMInstrumented()).toBe(false);
    });

    it("returns true after instrumentLLM()", () => {
      const mockTracer = {} as ReturnType<typeof getTracer>;
      vi.mocked(getTracer).mockReturnValue(mockTracer);

      instrumentLLM();

      expect(isLLMInstrumented()).toBe(true);
    });

    it("returns false after uninstrumentLLM()", () => {
      const mockTracer = {} as ReturnType<typeof getTracer>;
      vi.mocked(getTracer).mockReturnValue(mockTracer);

      instrumentLLM();
      uninstrumentLLM();

      expect(isLLMInstrumented()).toBe(false);
    });
  });
});
