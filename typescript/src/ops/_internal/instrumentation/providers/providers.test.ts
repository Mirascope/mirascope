/**
 * Tests for provider SDK instrumentation.
 *
 * Note: These tests verify the instrumentation API without requiring
 * the optional instrumentation packages to be installed.
 */

import { describe, it, expect, beforeEach, afterEach } from "vitest";

import {
  isAnthropicInstrumented,
  uninstrumentAnthropic,
  resetAnthropicInstrumentationForTesting,
} from "@/ops/_internal/instrumentation/providers/anthropic";
import {
  isGoogleGenaiInstrumented,
  uninstrumentGoogleGenai,
  resetGoogleGenaiInstrumentationForTesting,
} from "@/ops/_internal/instrumentation/providers/google-genai";
import {
  isOpenaiInstrumented,
  uninstrumentOpenai,
  resetOpenaiInstrumentationForTesting,
} from "@/ops/_internal/instrumentation/providers/openai";

describe("OpenAI Instrumentation", () => {
  beforeEach(() => {
    resetOpenaiInstrumentationForTesting();
  });

  afterEach(() => {
    resetOpenaiInstrumentationForTesting();
  });

  describe("isOpenaiInstrumented", () => {
    it("returns false initially", () => {
      expect(isOpenaiInstrumented()).toBe(false);
    });

    it("returns false after uninstrument when not instrumented", () => {
      uninstrumentOpenai();
      expect(isOpenaiInstrumented()).toBe(false);
    });
  });

  describe("uninstrumentOpenai", () => {
    it("is safe to call when not instrumented", () => {
      // Should not throw
      uninstrumentOpenai();
      uninstrumentOpenai();
      expect(isOpenaiInstrumented()).toBe(false);
    });
  });
});

describe("Anthropic Instrumentation", () => {
  beforeEach(() => {
    resetAnthropicInstrumentationForTesting();
  });

  afterEach(() => {
    resetAnthropicInstrumentationForTesting();
  });

  describe("isAnthropicInstrumented", () => {
    it("returns false initially", () => {
      expect(isAnthropicInstrumented()).toBe(false);
    });

    it("returns false after uninstrument when not instrumented", () => {
      uninstrumentAnthropic();
      expect(isAnthropicInstrumented()).toBe(false);
    });
  });

  describe("uninstrumentAnthropic", () => {
    it("is safe to call when not instrumented", () => {
      // Should not throw
      uninstrumentAnthropic();
      uninstrumentAnthropic();
      expect(isAnthropicInstrumented()).toBe(false);
    });
  });
});

describe("Google GenAI Instrumentation", () => {
  beforeEach(() => {
    resetGoogleGenaiInstrumentationForTesting();
  });

  afterEach(() => {
    resetGoogleGenaiInstrumentationForTesting();
  });

  describe("isGoogleGenaiInstrumented", () => {
    it("returns false initially", () => {
      expect(isGoogleGenaiInstrumented()).toBe(false);
    });

    it("returns false after uninstrument when not instrumented", () => {
      uninstrumentGoogleGenai();
      expect(isGoogleGenaiInstrumented()).toBe(false);
    });
  });

  describe("uninstrumentGoogleGenai", () => {
    it("is safe to call when not instrumented", () => {
      // Should not throw
      uninstrumentGoogleGenai();
      uninstrumentGoogleGenai();
      expect(isGoogleGenaiInstrumented()).toBe(false);
    });
  });
});
