import { describe, it, expect } from "vitest";
import { handleRequest, type App } from "@/api/handler";
import { getDatabase } from "@/db";
import type { PublicUser } from "@/db/schema";

const mockUser: PublicUser = {
  id: "test-user-id",
  email: "test@example.com",
  name: "Test User",
};

const testDatabaseUrl = "postgresql://test:test@localhost:5432/test";

function createTestApp(user: PublicUser = mockUser): App {
  return {
    environment: "test",
    database: getDatabase(testDatabaseUrl),
    authenticatedUser: user,
  };
}

describe("handleRequest", () => {
  it("should return matched=false and 404 for a non-existing route", async () => {
    const req = new Request("http://localhost/api/v0", { method: "GET" });
    const { matched, response } = await handleRequest(req, {
      app: createTestApp(),
      prefix: "/api/v0",
    });

    expect(matched).toBe(false);
    expect(response.status).toBe(404);
  });

  it("should return 500 and matched=false for a request that triggers an exception", async () => {
    const faultyRequest = new Proxy(
      {},
      {
        get() {
          throw new Error("boom");
        },
      },
    ) as Request;

    const { matched, response } = await handleRequest(faultyRequest, {
      app: createTestApp(),
    });

    expect(matched).toBe(false);
    expect(response.status).toBe(500);
    const text = await response.text();
    expect(text).toMatch(/Internal Server Error/);
  });
});
