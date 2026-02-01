import { describe, it, expect } from "vitest";

import {
  SESSION_HEADER_NAME,
  session,
  currentSession,
  extractSessionId,
} from "./session";

describe("session", () => {
  describe("SESSION_HEADER_NAME", () => {
    it("should be 'Mirascope-Session-Id'", () => {
      expect(SESSION_HEADER_NAME).toBe("Mirascope-Session-Id");
    });
  });

  describe("session()", () => {
    it("should create session with explicit id", async () => {
      const capturedSession = await session(
        { id: "test-session-123" },
        async () => {
          return currentSession();
        },
      );

      expect(capturedSession).not.toBeNull();
      expect(capturedSession?.id).toBe("test-session-123");
    });

    it("should auto-generate UUID when id not provided", async () => {
      const capturedSession = await session({}, async () => {
        return currentSession();
      });

      expect(capturedSession).not.toBeNull();
      expect(capturedSession?.id).toBeDefined();
      // UUID format check
      expect(capturedSession?.id).toMatch(
        /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i,
      );
    });

    it("should include attributes when provided", async () => {
      const capturedSession = await session(
        {
          id: "test-session",
          attributes: { userId: "user-123", environment: "test" },
        },
        async () => {
          return currentSession();
        },
      );

      expect(capturedSession?.attributes).toEqual({
        userId: "user-123",
        environment: "test",
      });
    });

    it("should return function result", async () => {
      const result = await session({ id: "test" }, async () => {
        return "test-result";
      });

      expect(result).toBe("test-result");
    });

    it("should work with sync functions", async () => {
      const result = await session({ id: "test" }, () => {
        return 42;
      });

      expect(result).toBe(42);
    });

    it("should propagate errors", async () => {
      await expect(
        session({ id: "test" }, async () => {
          throw new Error("test error");
        }),
      ).rejects.toThrow("test error");
    });

    it("should clear session after function completes", async () => {
      await session({ id: "test-session" }, async () => {
        expect(currentSession()?.id).toBe("test-session");
      });

      expect(currentSession()).toBeNull();
    });
  });

  describe("nested sessions", () => {
    it("should override parent session", async () => {
      const sessionIds: string[] = [];

      await session({ id: "outer" }, async () => {
        sessionIds.push(currentSession()?.id ?? "");

        await session({ id: "inner" }, async () => {
          sessionIds.push(currentSession()?.id ?? "");
        });

        sessionIds.push(currentSession()?.id ?? "");
      });

      expect(sessionIds).toEqual(["outer", "inner", "outer"]);
    });

    it("should restore parent session after nested session ends", async () => {
      await session({ id: "parent" }, async () => {
        expect(currentSession()?.id).toBe("parent");

        await session({ id: "child" }, async () => {
          expect(currentSession()?.id).toBe("child");
        });

        expect(currentSession()?.id).toBe("parent");
      });
    });

    it("should support deeply nested sessions", async () => {
      const sessionIds: string[] = [];

      await session({ id: "level1" }, async () => {
        sessionIds.push(currentSession()?.id ?? "");

        await session({ id: "level2" }, async () => {
          sessionIds.push(currentSession()?.id ?? "");

          await session({ id: "level3" }, async () => {
            sessionIds.push(currentSession()?.id ?? "");
          });

          sessionIds.push(currentSession()?.id ?? "");
        });

        sessionIds.push(currentSession()?.id ?? "");
      });

      expect(sessionIds).toEqual([
        "level1",
        "level2",
        "level3",
        "level2",
        "level1",
      ]);
    });
  });

  describe("currentSession()", () => {
    it("should return null when no session is active", () => {
      expect(currentSession()).toBeNull();
    });

    it("should return session context when session is active", async () => {
      await session({ id: "active-session" }, async () => {
        const ctx = currentSession();
        expect(ctx).not.toBeNull();
        expect(ctx?.id).toBe("active-session");
      });
    });
  });

  describe("extractSessionId()", () => {
    it("should extract session id from headers", () => {
      const headers = { "Mirascope-Session-Id": "session-123" };
      expect(extractSessionId(headers)).toBe("session-123");
    });

    it("should be case-insensitive", () => {
      const headers1 = { "mirascope-session-id": "session-123" };
      const headers2 = { "MIRASCOPE-SESSION-ID": "session-456" };
      const headers3 = { "Mirascope-Session-Id": "session-789" };

      expect(extractSessionId(headers1)).toBe("session-123");
      expect(extractSessionId(headers2)).toBe("session-456");
      expect(extractSessionId(headers3)).toBe("session-789");
    });

    it("should return null when header not present", () => {
      const headers = { "Content-Type": "application/json" };
      expect(extractSessionId(headers)).toBeNull();
    });

    it("should handle array header values", () => {
      const headers = { "Mirascope-Session-Id": ["session-1", "session-2"] };
      expect(extractSessionId(headers)).toBe("session-1");
    });

    it("should return null for array with undefined first element", () => {
      const headers = {
        "Mirascope-Session-Id": [undefined, "session-2"] as unknown as string[],
      };
      expect(extractSessionId(headers)).toBeNull();
    });

    it("should return null for empty array", () => {
      const headers = { "Mirascope-Session-Id": [] as string[] };
      expect(extractSessionId(headers)).toBeNull();
    });

    it("should handle undefined values", () => {
      const headers = { "Mirascope-Session-Id": undefined };
      expect(extractSessionId(headers)).toBeNull();
    });

    it("should handle empty string", () => {
      const headers = { "Mirascope-Session-Id": "" };
      expect(extractSessionId(headers)).toBe("");
    });
  });

  describe("async boundary propagation", () => {
    it("should propagate session across async operations", async () => {
      await session({ id: "async-test" }, async () => {
        // Simulate async operations
        await Promise.resolve();
        expect(currentSession()?.id).toBe("async-test");

        await new Promise((resolve) => setTimeout(resolve, 10));
        expect(currentSession()?.id).toBe("async-test");
      });
    });

    it("should maintain separate sessions in concurrent operations", async () => {
      const results: string[] = [];

      await Promise.all([
        session({ id: "session-a" }, async () => {
          await new Promise((resolve) => setTimeout(resolve, 20));
          results.push(`a:${currentSession()?.id}`);
        }),
        session({ id: "session-b" }, async () => {
          await new Promise((resolve) => setTimeout(resolve, 10));
          results.push(`b:${currentSession()?.id}`);
        }),
      ]);

      expect(results).toContain("a:session-a");
      expect(results).toContain("b:session-b");
    });
  });
});
