import { describe, it, expect } from "vitest";
import { Effect } from "effect";
import { withTestClient } from "@/tests/api";

describe(
  "Health API",
  withTestClient((client) => {
    it("GET /health", async () => {
      const result = await Effect.runPromise(client.health.check());
      expect(result).toMatchObject({
        status: "ok",
        timestamp: expect.any(String) as unknown,
        environment: "test",
      });
    });
  }),
);
