import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { handleRequest } from "@/api/handler";
import type { PublicUser } from "@/db/schema";

// Mock authenticated user for tests
const mockUser: PublicUser = {
  id: "test-user-id",
  email: "test@example.com",
  name: "Test User",
};

describe("handleRequest", () => {
  const originalEnv = process.env.DATABASE_URL;

  beforeEach(() => {
    // Clear DATABASE_URL for tests that need it
    delete process.env.DATABASE_URL;
  });

  afterEach(() => {
    // Restore original env
    if (originalEnv !== undefined) {
      process.env.DATABASE_URL = originalEnv;
    }
  });

  it("should return matched=false and 404 for a non-existing route", async () => {
    const req = new Request("http://localhost/api/v0", { method: "GET" });
    const { matched, response } = await handleRequest(req, {
      environment: "test",
      prefix: "/api/v0",
      authenticatedUser: mockUser,
      databaseUrl: "postgresql://test:test@localhost:5432/test",
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
      environment: "test",
      authenticatedUser: mockUser,
      databaseUrl: "postgresql://test:test@localhost:5432/test",
    });

    expect(matched).toBe(false);
    expect(response.status).toBe(500);
    const text = await response.text();
    expect(text).toMatch(/Internal Server Error/);
  });

  it("should throw error when DATABASE_URL is not provided", async () => {
    const req = new Request("http://localhost/api/v0/health", {
      method: "GET",
    });

    await expect(
      handleRequest(req, {
        environment: "test",
        authenticatedUser: mockUser,
        // No databaseUrl provided, and process.env.DATABASE_URL is cleared
      }),
    ).rejects.toThrow("DATABASE_URL is required");
  });

  it("should use 'unknown' environment when environment is not provided", async () => {
    const req = new Request("http://localhost/api/v0", { method: "GET" });
    const { matched, response } = await handleRequest(req, {
      // environment not provided - should default to "unknown"
      authenticatedUser: mockUser,
      databaseUrl: "postgresql://test:test@localhost:5432/test",
    });

    // Route doesn't exist, but handler should work
    expect(matched).toBe(false);
    expect(response.status).toBe(404);
  });
});
