import { describe, it, expect } from "@effect/vitest";

import {
  isEffectQueryFailure,
  getFailureTag,
  getFailure,
  getErrorMessage,
  type EffectQueryFailure,
} from "./errors";

// Mock EffectQueryFailure for testing
function createMockEffectQueryFailure<E>(failure: E): EffectQueryFailure<E> {
  return {
    _tag: "EffectQueryFailure",
    failure,
    failureCause: {} as never,
    match: () => undefined as never,
  };
}

describe("isEffectQueryFailure", () => {
  it("should return true for valid EffectQueryFailure objects", () => {
    const error = createMockEffectQueryFailure({
      _tag: "TestError",
      message: "test",
    });
    expect(isEffectQueryFailure(error)).toBe(true);
  });

  it("should return false for null", () => {
    expect(isEffectQueryFailure(null)).toBe(false);
  });

  it("should return false for undefined", () => {
    expect(isEffectQueryFailure(undefined)).toBe(false);
  });

  it("should return false for regular Error objects", () => {
    expect(isEffectQueryFailure(new Error("test"))).toBe(false);
  });

  it("should return false for objects with wrong _tag", () => {
    expect(isEffectQueryFailure({ _tag: "OtherError", failure: {} })).toBe(
      false,
    );
  });

  it("should return false for plain objects", () => {
    expect(isEffectQueryFailure({ message: "test" })).toBe(false);
  });

  it("should return false for primitives", () => {
    expect(isEffectQueryFailure("string")).toBe(false);
    expect(isEffectQueryFailure(123)).toBe(false);
    expect(isEffectQueryFailure(true)).toBe(false);
  });
});

describe("getFailureTag", () => {
  it("should return the _tag from the nested failure object", () => {
    const error = createMockEffectQueryFailure({
      _tag: "PlanLimitExceededError",
      message: "Limit exceeded",
    });
    expect(getFailureTag(error)).toBe("PlanLimitExceededError");
  });

  it("should return undefined for non-EffectQueryFailure errors", () => {
    expect(getFailureTag(new Error("test"))).toBe(undefined);
  });

  it("should return undefined when failure is null", () => {
    const error = createMockEffectQueryFailure(null);
    expect(getFailureTag(error)).toBe(undefined);
  });

  it("should return undefined when failure has no _tag", () => {
    const error = createMockEffectQueryFailure({ message: "no tag" });
    expect(getFailureTag(error)).toBe(undefined);
  });

  it("should return undefined for primitive failures", () => {
    const error = createMockEffectQueryFailure("string error");
    expect(getFailureTag(error)).toBe(undefined);
  });
});

describe("getFailure", () => {
  it("should return the failure object", () => {
    const failure = { _tag: "TestError", message: "test", extra: 123 };
    const error = createMockEffectQueryFailure(failure);
    expect(getFailure(error)).toBe(failure);
  });

  it("should return undefined for non-EffectQueryFailure errors", () => {
    expect(getFailure(new Error("test"))).toBe(undefined);
  });

  it("should return null if failure is null", () => {
    const error = createMockEffectQueryFailure(null);
    expect(getFailure(error)).toBe(null);
  });

  it("should preserve type information", () => {
    interface CustomError {
      _tag: string;
      message: string;
      customField: number;
    }
    const failure: CustomError = {
      _tag: "CustomError",
      message: "test",
      customField: 42,
    };
    const error = createMockEffectQueryFailure(failure);
    const result = getFailure<CustomError>(error);
    expect(result?.customField).toBe(42);
  });
});

describe("getErrorMessage", () => {
  it("should extract message from EffectQueryFailure", () => {
    const error = createMockEffectQueryFailure({
      _tag: "PlanLimitExceededError",
      message: "Cannot create project: free plan limit is 1 project(s)",
    });
    expect(getErrorMessage(error, "fallback")).toBe(
      "Cannot create project: free plan limit is 1 project(s)",
    );
  });

  it("should return fallback for non-EffectQueryFailure errors", () => {
    expect(getErrorMessage(new Error("original"), "fallback")).toBe("fallback");
  });

  it("should return fallback when failure is null", () => {
    const error = createMockEffectQueryFailure(null);
    expect(getErrorMessage(error, "fallback")).toBe("fallback");
  });

  it("should return fallback when failure has no message", () => {
    const error = createMockEffectQueryFailure({ _tag: "ErrorWithoutMessage" });
    expect(getErrorMessage(error, "fallback")).toBe("fallback");
  });

  it("should return fallback when message is not a string", () => {
    const error = createMockEffectQueryFailure({ _tag: "Error", message: 123 });
    expect(getErrorMessage(error, "fallback")).toBe("fallback");
  });

  it("should return fallback for null input", () => {
    expect(getErrorMessage(null, "fallback")).toBe("fallback");
  });

  it("should return fallback for undefined input", () => {
    expect(getErrorMessage(undefined, "fallback")).toBe("fallback");
  });

  it("should handle empty string message", () => {
    const error = createMockEffectQueryFailure({ _tag: "Error", message: "" });
    expect(getErrorMessage(error, "fallback")).toBe("");
  });
});
