/**
 * Tests for base provider instrumentation.
 */

import { describe, it, expect, beforeEach, afterEach } from "vitest";

import {
  BaseInstrumentation,
  type ContentCaptureMode,
  type Instrumentor,
  OTEL_SEMCONV_STABILITY_OPT_IN,
  OTEL_SEMCONV_STABILITY_VALUE,
} from "@/ops/_internal/instrumentation/providers/base";

// Mock instrumentor for testing
class MockInstrumentor implements Instrumentor {
  enableCalled = false;
  disableCalled = false;
  tracerProvider: unknown = null;

  enable(): void {
    this.enableCalled = true;
  }

  disable(): void {
    this.disableCalled = true;
  }

  setTracerProvider(tracerProvider: unknown): void {
    this.tracerProvider = tracerProvider;
  }
}

// Test implementation of BaseInstrumentation
let testInstance: TestInstrumentation | null = null;
let mockInstrumentor: MockInstrumentor | null = null;
let contentCaptureConfigured: ContentCaptureMode | null = null;

class TestInstrumentation extends BaseInstrumentation<MockInstrumentor> {
  static readonly INSTANCE_KEY = "test-instrumentation";

  static instance(): TestInstrumentation {
    if (!testInstance) {
      testInstance = new TestInstrumentation();
    }
    return testInstance;
  }

  // Use the parent's getInstance for testing the singleton pattern
  static getInstanceViaParent(): TestInstrumentation {
    return TestInstrumentation.getInstance(TestInstrumentation.INSTANCE_KEY);
  }

  protected createInstrumentor(): MockInstrumentor {
    mockInstrumentor = new MockInstrumentor();
    return mockInstrumentor;
  }

  protected configureContentCapture(captureContent: ContentCaptureMode): void {
    contentCaptureConfigured = captureContent;
    if (captureContent === "enabled") {
      this.setEnvVar("TEST_CONTENT_CAPTURE", "true");
    } else if (captureContent === "disabled") {
      this.setEnvVar("TEST_CONTENT_CAPTURE", "false");
    }
  }

  static resetForTesting(): void {
    if (testInstance) {
      testInstance.uninstrument();
    }
    testInstance = null;
    mockInstrumentor = null;
    contentCaptureConfigured = null;
  }

  static resetViaParent(): void {
    BaseInstrumentation.resetForTesting(TestInstrumentation.INSTANCE_KEY);
  }
}

// Second test class for testing multiple instances
class SecondTestInstrumentation extends BaseInstrumentation<MockInstrumentor> {
  static readonly INSTANCE_KEY = "second-test-instrumentation";

  static instance(): SecondTestInstrumentation {
    return SecondTestInstrumentation.getInstance(
      SecondTestInstrumentation.INSTANCE_KEY,
    );
  }

  protected createInstrumentor(): MockInstrumentor {
    return new MockInstrumentor();
  }

  protected configureContentCapture(): void {
    // no-op
  }
}

describe("BaseInstrumentation", () => {
  beforeEach(() => {
    TestInstrumentation.resetForTesting();
    // Clear any env vars
    delete process.env[OTEL_SEMCONV_STABILITY_OPT_IN];
    delete process.env["TEST_CONTENT_CAPTURE"];
  });

  afterEach(() => {
    TestInstrumentation.resetForTesting();
    // Clean up env vars
    delete process.env[OTEL_SEMCONV_STABILITY_OPT_IN];
    delete process.env["TEST_CONTENT_CAPTURE"];
  });

  describe("instrument", () => {
    it("creates and enables the instrumentor", () => {
      const instance = TestInstrumentation.instance();

      instance.instrument();

      expect(instance.isInstrumented).toBe(true);
      expect(mockInstrumentor?.enableCalled).toBe(true);
    });

    it("sets semantic convention opt-in environment variable", () => {
      const instance = TestInstrumentation.instance();

      instance.instrument();

      expect(process.env[OTEL_SEMCONV_STABILITY_OPT_IN]).toBe(
        OTEL_SEMCONV_STABILITY_VALUE,
      );
    });

    it("configures content capture with default mode", () => {
      const instance = TestInstrumentation.instance();

      instance.instrument();

      expect(contentCaptureConfigured).toBe("default");
    });

    it("configures content capture with enabled mode", () => {
      const instance = TestInstrumentation.instance();

      instance.instrument({ captureContent: "enabled" });

      expect(contentCaptureConfigured).toBe("enabled");
      expect(process.env["TEST_CONTENT_CAPTURE"]).toBe("true");
    });

    it("configures content capture with disabled mode", () => {
      const instance = TestInstrumentation.instance();

      instance.instrument({ captureContent: "disabled" });

      expect(contentCaptureConfigured).toBe("disabled");
      expect(process.env["TEST_CONTENT_CAPTURE"]).toBe("false");
    });

    it("passes tracer provider to instrumentor", () => {
      const instance = TestInstrumentation.instance();
      const mockTracerProvider = { test: "provider" };

      instance.instrument({
        tracerProvider: mockTracerProvider as unknown as undefined,
      });

      expect(mockInstrumentor?.tracerProvider).toBe(mockTracerProvider);
    });

    it("is idempotent - calling multiple times has no effect", () => {
      const instance = TestInstrumentation.instance();

      instance.instrument();
      const firstInstrumentor = mockInstrumentor;

      instance.instrument();

      // Should still be the same instrumentor
      expect(mockInstrumentor).toBe(firstInstrumentor);
    });

    it("does not override existing semconv env var", () => {
      process.env[OTEL_SEMCONV_STABILITY_OPT_IN] = "custom_value";

      const instance = TestInstrumentation.instance();
      instance.instrument();

      expect(process.env[OTEL_SEMCONV_STABILITY_OPT_IN]).toBe("custom_value");
    });
  });

  describe("uninstrument", () => {
    it("disables the instrumentor", () => {
      const instance = TestInstrumentation.instance();
      instance.instrument();

      instance.uninstrument();

      expect(instance.isInstrumented).toBe(false);
      expect(mockInstrumentor?.disableCalled).toBe(true);
    });

    it("restores environment variables", () => {
      const instance = TestInstrumentation.instance();
      instance.instrument({ captureContent: "enabled" });

      expect(process.env["TEST_CONTENT_CAPTURE"]).toBe("true");

      instance.uninstrument();

      expect(process.env["TEST_CONTENT_CAPTURE"]).toBeUndefined();
    });

    it("restores original environment variable values", () => {
      process.env["TEST_CONTENT_CAPTURE"] = "original";

      const instance = TestInstrumentation.instance();
      instance.instrument({ captureContent: "enabled" });

      expect(process.env["TEST_CONTENT_CAPTURE"]).toBe("true");

      instance.uninstrument();

      expect(process.env["TEST_CONTENT_CAPTURE"]).toBe("original");
    });

    it("is idempotent - calling when not instrumented is a no-op", () => {
      const instance = TestInstrumentation.instance();

      // Should not throw
      instance.uninstrument();
      instance.uninstrument();

      expect(instance.isInstrumented).toBe(false);
    });
  });

  describe("isInstrumented", () => {
    it("returns false initially", () => {
      const instance = TestInstrumentation.instance();

      expect(instance.isInstrumented).toBe(false);
    });

    it("returns true after instrument()", () => {
      const instance = TestInstrumentation.instance();

      instance.instrument();

      expect(instance.isInstrumented).toBe(true);
    });

    it("returns false after uninstrument()", () => {
      const instance = TestInstrumentation.instance();
      instance.instrument();

      instance.uninstrument();

      expect(instance.isInstrumented).toBe(false);
    });
  });

  describe("singleton pattern", () => {
    it("returns the same instance on multiple calls", () => {
      const instance1 = TestInstrumentation.instance();
      const instance2 = TestInstrumentation.instance();

      expect(instance1).toBe(instance2);
    });

    it("resetForTesting clears the instance", () => {
      const instance1 = TestInstrumentation.instance();

      TestInstrumentation.resetForTesting();

      const instance2 = TestInstrumentation.instance();
      expect(instance1).not.toBe(instance2);
    });
  });

  describe("error handling", () => {
    it("restores env vars if instrumentor throws", () => {
      // Create a subclass that throws during instrumentation
      let throwingInstance: ThrowingInstrumentation | null = null;

      class ThrowingInstrumentation extends BaseInstrumentation<MockInstrumentor> {
        static instance(): ThrowingInstrumentation {
          if (!throwingInstance) {
            throwingInstance = new ThrowingInstrumentation();
          }
          return throwingInstance;
        }

        protected createInstrumentor(): MockInstrumentor {
          const instrumentor = new MockInstrumentor();
          instrumentor.enable = () => {
            throw new Error("Instrumentation failed");
          };
          return instrumentor;
        }

        protected configureContentCapture(
          captureContent: ContentCaptureMode,
        ): void {
          if (captureContent === "enabled") {
            this.setEnvVar("THROWING_TEST_VAR", "value");
          }
        }

        static resetForTesting(): void {
          if (throwingInstance) {
            throwingInstance.uninstrument();
          }
          throwingInstance = null;
        }
      }

      const instance = ThrowingInstrumentation.instance();

      expect(() => instance.instrument({ captureContent: "enabled" })).toThrow(
        "Instrumentation failed",
      );

      // Env var should be restored
      expect(process.env["THROWING_TEST_VAR"]).toBeUndefined();

      ThrowingInstrumentation.resetForTesting();
    });
  });

  describe("getInstance static method", () => {
    afterEach(() => {
      // Clean up via the parent class method
      BaseInstrumentation.resetAllForTesting();
    });

    it("creates a new instance when none exists", () => {
      const instance = TestInstrumentation.getInstanceViaParent();

      expect(instance).toBeInstanceOf(TestInstrumentation);
    });

    it("returns the same instance on subsequent calls", () => {
      const instance1 = TestInstrumentation.getInstanceViaParent();
      const instance2 = TestInstrumentation.getInstanceViaParent();

      expect(instance1).toBe(instance2);
    });

    it("maintains separate instances for different keys", () => {
      const instance1 = TestInstrumentation.getInstanceViaParent();
      const instance2 = SecondTestInstrumentation.instance();

      expect(instance1).not.toBe(instance2);
      expect(instance1).toBeInstanceOf(TestInstrumentation);
      expect(instance2).toBeInstanceOf(SecondTestInstrumentation);
    });
  });

  describe("BaseInstrumentation.resetForTesting", () => {
    afterEach(() => {
      BaseInstrumentation.resetAllForTesting();
    });

    it("removes the instance for the given key", () => {
      const instance1 = TestInstrumentation.getInstanceViaParent();
      instance1.instrument();

      BaseInstrumentation.resetForTesting(TestInstrumentation.INSTANCE_KEY);

      const instance2 = TestInstrumentation.getInstanceViaParent();
      expect(instance1).not.toBe(instance2);
    });

    it("disables instrumentor when resetting an instrumented instance", () => {
      const instance = TestInstrumentation.getInstanceViaParent();
      instance.instrument();
      const instrumentor = mockInstrumentor;

      BaseInstrumentation.resetForTesting(TestInstrumentation.INSTANCE_KEY);

      expect(instrumentor?.disableCalled).toBe(true);
    });

    it("is a no-op for non-existent keys", () => {
      // Should not throw
      BaseInstrumentation.resetForTesting("non-existent-key");
    });
  });

  describe("BaseInstrumentation.resetAllForTesting", () => {
    afterEach(() => {
      BaseInstrumentation.resetAllForTesting();
    });

    it("resets all registered instances", () => {
      const instance1 = TestInstrumentation.getInstanceViaParent();
      const instance2 = SecondTestInstrumentation.instance();
      instance1.instrument();
      instance2.instrument();

      BaseInstrumentation.resetAllForTesting();

      // New instances should be different
      const newInstance1 = TestInstrumentation.getInstanceViaParent();
      const newInstance2 = SecondTestInstrumentation.instance();
      expect(newInstance1).not.toBe(instance1);
      expect(newInstance2).not.toBe(instance2);
    });

    it("is safe to call with no instances", () => {
      // Should not throw
      BaseInstrumentation.resetAllForTesting();
    });
  });
});
