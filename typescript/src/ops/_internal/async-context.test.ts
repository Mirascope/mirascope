import { describe, it, expect } from "vitest";

import {
  opsContextStorage,
  getCurrentContext,
  runWithContext,
} from "./async-context";

describe("async-context", () => {
  describe("opsContextStorage", () => {
    it("should be an AsyncLocalStorage instance", () => {
      expect(opsContextStorage).toBeDefined();
      expect(typeof opsContextStorage.run).toBe("function");
      expect(typeof opsContextStorage.getStore).toBe("function");
    });
  });

  describe("getCurrentContext()", () => {
    it("should return undefined when no context is set", () => {
      expect(getCurrentContext()).toBeUndefined();
    });

    it("should return context when inside runWithContext", () => {
      const context = { sessionId: "test-123" };

      runWithContext(context, () => {
        expect(getCurrentContext()).toEqual(context);
      });
    });
  });

  describe("runWithContext()", () => {
    it("should run function with given context", () => {
      const context = { sessionId: "session-456" };

      const result = runWithContext(context, () => {
        return getCurrentContext()?.sessionId;
      });

      expect(result).toBe("session-456");
    });

    it("should return function result", () => {
      const context = { sessionId: "test" };

      const result = runWithContext(context, () => {
        return "hello world";
      });

      expect(result).toBe("hello world");
    });

    it("should support context with attributes", () => {
      const context = {
        sessionId: "test-session",
        sessionAttributes: { userId: "user-1", role: "admin" },
      };

      runWithContext(context, () => {
        const current = getCurrentContext();
        expect(current?.sessionId).toBe("test-session");
        expect(current?.sessionAttributes).toEqual({
          userId: "user-1",
          role: "admin",
        });
      });
    });

    it("should clear context after function completes", () => {
      const context = { sessionId: "temp-session" };

      runWithContext(context, () => {
        expect(getCurrentContext()).toBeDefined();
      });

      expect(getCurrentContext()).toBeUndefined();
    });

    it("should support nested contexts", () => {
      const outer = { sessionId: "outer" };
      const inner = { sessionId: "inner" };

      runWithContext(outer, () => {
        expect(getCurrentContext()?.sessionId).toBe("outer");

        runWithContext(inner, () => {
          expect(getCurrentContext()?.sessionId).toBe("inner");
        });

        expect(getCurrentContext()?.sessionId).toBe("outer");
      });
    });
  });
});
