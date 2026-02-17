import { Hono } from "hono";
import { describe, it, expect } from "vitest";

import { authMiddleware } from "../src/middleware/auth.js";

function createTestApp(token: string) {
  const app = new Hono();
  app.use("*", authMiddleware(token));
  app.get("/test", (c) => c.json({ ok: true }));
  return app;
}

describe("authMiddleware", () => {
  const token = "test-secret-token";
  const app = createTestApp(token);

  it("rejects requests without Authorization header", async () => {
    const res = await app.request("/test");
    expect(res.status).toBe(401);
    const body = (await res.json()) as { error: string };
    expect(body.error).toContain("Missing");
  });

  it("rejects requests with wrong scheme", async () => {
    const res = await app.request("/test", {
      headers: { Authorization: "Basic abc123" },
    });
    expect(res.status).toBe(401);
  });

  it("rejects requests with invalid token", async () => {
    const res = await app.request("/test", {
      headers: { Authorization: "Bearer wrong-token" },
    });
    expect(res.status).toBe(403);
  });

  it("allows requests with valid token", async () => {
    const res = await app.request("/test", {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(res.status).toBe(200);
    const body = (await res.json()) as { ok: boolean };
    expect(body.ok).toBe(true);
  });

  it("rejects empty bearer token", async () => {
    const res = await app.request("/test", {
      headers: { Authorization: "Bearer " },
    });
    // Empty token after split won't match
    expect(res.status).toBe(401);
  });
});
