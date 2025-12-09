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
  it("should return 404 for non-existing routes", async () => {
    const req = new Request(
      "http://localhost/api/v0/this-route-does-not-exist",
      { method: "GET" },
    );
    const { matched, response } = await handleRequest(req, {
      app: createTestApp(),
      prefix: "/api/v0",
    });

    expect(response.status).toBe(404);
    expect(matched).toBe(false);
  });

  it("should return 404 when pathname exactly matches prefix (no route)", async () => {
    const req = new Request("http://localhost/api/v0", { method: "GET" });
    const { matched, response } = await handleRequest(req, {
      app: createTestApp(),
      prefix: "/api/v0",
    });

    // The path becomes "/" after stripping prefix, which doesn't match any route
    expect(response.status).toBe(404);
    expect(matched).toBe(false);
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
