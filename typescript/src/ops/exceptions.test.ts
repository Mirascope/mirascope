import { describe, it, expect } from "vitest";

import { MirascopeError } from "@/llm/exceptions";

import { ConfigurationError, ClosureComputationError } from "./exceptions";

describe("exceptions", () => {
  describe("ConfigurationError", () => {
    it("should extend MirascopeError", () => {
      const error = new ConfigurationError("Invalid configuration");
      expect(error).toBeInstanceOf(MirascopeError);
      expect(error).toBeInstanceOf(Error);
    });

    it("should have correct name", () => {
      const error = new ConfigurationError("test");
      expect(error.name).toBe("ConfigurationError");
    });

    it("should preserve message", () => {
      const error = new ConfigurationError("test message");
      expect(error.message).toBe("test message");
    });

    it("should be throwable and catchable", () => {
      const throwError = () => {
        throw new ConfigurationError("configuration failed");
      };

      expect(throwError).toThrow(ConfigurationError);
      expect(throwError).toThrow("configuration failed");
    });
  });

  describe("ClosureComputationError", () => {
    it("should extend MirascopeError", () => {
      const error = new ClosureComputationError(
        "myFunc",
        "Cannot compute closure",
      );
      expect(error).toBeInstanceOf(MirascopeError);
      expect(error).toBeInstanceOf(Error);
    });

    it("should store qualifiedName", () => {
      const error = new ClosureComputationError(
        "module.myFunc",
        "error message",
      );
      expect(error.qualifiedName).toBe("module.myFunc");
    });

    it("should have correct name", () => {
      const error = new ClosureComputationError("fn", "msg");
      expect(error.name).toBe("ClosureComputationError");
    });

    it("should preserve message", () => {
      const error = new ClosureComputationError(
        "myFunc",
        "Cannot determine closure variables",
      );
      expect(error.message).toBe("Cannot determine closure variables");
    });

    it("should be throwable and catchable", () => {
      const throwError = () => {
        throw new ClosureComputationError("fn", "closure computation failed");
      };

      expect(throwError).toThrow(ClosureComputationError);
      expect(throwError).toThrow("closure computation failed");
    });

    it("should allow accessing qualifiedName after catch", () => {
      try {
        throw new ClosureComputationError(
          "myModule.myFunc",
          "failed to compute",
        );
      } catch (error) {
        expect(error).toBeInstanceOf(ClosureComputationError);
        if (error instanceof ClosureComputationError) {
          expect(error.qualifiedName).toBe("myModule.myFunc");
        }
      }
    });
  });
});
