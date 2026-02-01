/**
 * Tests for LLM instrumentation entry point.
 */

import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";

import {
  instrumentLlm,
  uninstrumentLlm,
  isLlmInstrumented,
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
    uninstrumentLlm();
  });

  describe("instrumentLlm", () => {
    it("throws error if configure() was not called", () => {
      vi.mocked(getTracer).mockReturnValue(null);

      expect(() => instrumentLlm()).toThrow(
        "You must call configure() before calling instrumentLlm()",
      );
    });

    it("instruments model methods when tracer is configured", () => {
      const mockTracer = {} as ReturnType<typeof getTracer>;
      vi.mocked(getTracer).mockReturnValue(mockTracer);

      expect(isModelInstrumented()).toBe(false);

      instrumentLlm();

      expect(isModelInstrumented()).toBe(true);
    });

    it("is idempotent - calling multiple times has no additional effect", () => {
      const mockTracer = {} as ReturnType<typeof getTracer>;
      vi.mocked(getTracer).mockReturnValue(mockTracer);

      instrumentLlm();
      instrumentLlm();
      instrumentLlm();

      expect(isLlmInstrumented()).toBe(true);
      // Should still be instrumented, not errored
    });
  });

  describe("uninstrumentLlm", () => {
    it("removes instrumentation", () => {
      const mockTracer = {} as ReturnType<typeof getTracer>;
      vi.mocked(getTracer).mockReturnValue(mockTracer);

      instrumentLlm();
      expect(isLlmInstrumented()).toBe(true);

      uninstrumentLlm();
      expect(isLlmInstrumented()).toBe(false);
    });

    it("is idempotent - calling when not instrumented is a no-op", () => {
      expect(isLlmInstrumented()).toBe(false);

      uninstrumentLlm();
      uninstrumentLlm();

      expect(isLlmInstrumented()).toBe(false);
      // Should not error
    });
  });

  describe("isLlmInstrumented", () => {
    it("returns false initially", () => {
      expect(isLlmInstrumented()).toBe(false);
    });

    it("returns true after instrumentLlm()", () => {
      const mockTracer = {} as ReturnType<typeof getTracer>;
      vi.mocked(getTracer).mockReturnValue(mockTracer);

      instrumentLlm();

      expect(isLlmInstrumented()).toBe(true);
    });

    it("returns false after uninstrumentLlm()", () => {
      const mockTracer = {} as ReturnType<typeof getTracer>;
      vi.mocked(getTracer).mockReturnValue(mockTracer);

      instrumentLlm();
      uninstrumentLlm();

      expect(isLlmInstrumented()).toBe(false);
    });
  });
});
