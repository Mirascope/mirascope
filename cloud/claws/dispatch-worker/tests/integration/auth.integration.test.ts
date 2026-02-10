/**
 * Integration tests for auth middleware via real Miniflare service bindings.
 *
 * Tests the auth decision matrix from DESIGN.md:
 *   /{org}/{claw}/webhook/*   → pass-through (no auth)
 *   /{org}/{claw}/* + Bearer  → pass-through (gateway validates)
 *   /{org}/{claw}/* + Cookie  → validate session via Cloud API
 *   /{org}/{claw}/* (no auth) → 401
 *   CORS preflight (OPTIONS)  → 204 with CORS headers
 */
import * as esbuild from "esbuild";
import { Miniflare } from "miniflare";
import path from "node:path";
import { afterAll, beforeAll, beforeEach, describe, expect, it } from "vitest";

import mockCloudWorker from "../workers/mock-cloud-worker";

let mf: Miniflare;

async function bundleWorker(entryPoint: string): Promise<string> {
  const result = await esbuild.build({
    entryPoints: [entryPoint],
    bundle: true,
    format: "esm",
    target: "esnext",
    write: false,
    conditions: ["workerd", "worker", "browser"],
    external: ["cloudflare:*", "node:*"],
  });
  return result.outputFiles[0].text;
}

beforeAll(async () => {
  const base = path.resolve(import.meta.dirname, "..");
  const harnessScript = await bundleWorker(
    path.join(base, "workers/auth-harness-worker.ts"),
  );

  mf = new Miniflare({
    modules: true,
    script: harnessScript,
    compatibilityDate: "2025-05-06",
    compatibilityFlags: ["nodejs_compat"],
    serviceBindings: {
      MIRASCOPE_CLOUD: mockCloudWorker.fetch,
    },
  });

  await mf.ready;
});

afterAll(async () => {
  await mf?.dispose();
});

beforeEach(async () => {
  // Clear session cache between tests
  await mf.dispatchFetch("http://test/clear-cache", { method: "POST" });
});

// ---------------------------------------------------------------------------
// Webhook pass-through (no auth required)
// ---------------------------------------------------------------------------

describe("webhook pass-through", () => {
  it("passes through webhook requests without auth", async () => {
    const res = await mf.dispatchFetch(
      "http://test/test-org/my-claw/webhook/telegram",
    );
    expect(res.ok).toBe(true);

    const body = (await res.json()) as any;
    expect(body.action).toBe("pass-through");
    expect(body.clawId).toBe("resolved-my-claw");
    expect(body.remainder).toBe("/webhook/telegram");
  });

  it("passes through webhook POST without auth", async () => {
    const res = await mf.dispatchFetch(
      "http://test/test-org/my-claw/webhook/slack",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ event: "message" }),
      },
    );
    expect(res.ok).toBe(true);

    const body = (await res.json()) as any;
    expect(body.action).toBe("pass-through");
    expect(body.remainder).toBe("/webhook/slack");
  });
});

// ---------------------------------------------------------------------------
// Bearer token pass-through
// ---------------------------------------------------------------------------

describe("Bearer token pass-through", () => {
  it("passes through requests with Bearer token", async () => {
    const res = await mf.dispatchFetch(
      "http://test/test-org/my-claw/api/chat",
      {
        headers: { Authorization: "Bearer gw-tok-12345" },
      },
    );
    expect(res.ok).toBe(true);

    const body = (await res.json()) as any;
    expect(body.action).toBe("pass-through");
    expect(body.clawId).toBe("resolved-my-claw");
    expect(body.remainder).toBe("/api/chat");
  });

  it("does not validate the Bearer token itself", async () => {
    // Even an invalid token should pass through — gateway validates
    const res = await mf.dispatchFetch(
      "http://test/test-org/my-claw/api/chat",
      {
        headers: { Authorization: "Bearer totally-invalid-token" },
      },
    );
    expect(res.ok).toBe(true);

    const body = (await res.json()) as any;
    expect(body.action).toBe("pass-through");
  });
});

// ---------------------------------------------------------------------------
// Session cookie validation
// ---------------------------------------------------------------------------

describe("session cookie validation", () => {
  it("allows requests with a valid session cookie", async () => {
    const res = await mf.dispatchFetch(
      "http://test/test-org/my-claw/api/chat",
      {
        headers: { Cookie: "session=valid-sess-123" },
      },
    );
    expect(res.ok).toBe(true);

    const body = (await res.json()) as any;
    expect(body.action).toBe("pass-through");
    expect(body.clawId).toBe("resolved-my-claw");
  });

  it("rejects requests with an invalid session cookie", async () => {
    const res = await mf.dispatchFetch(
      "http://test/test-org/my-claw/api/chat",
      {
        headers: { Cookie: "session=invalid-sess-456" },
      },
    );
    expect(res.status).toBe(401);

    const body = (await res.json()) as any;
    expect(body.error).toBe("Invalid session");
  });

  it("rejects requests with a forbidden session cookie", async () => {
    const res = await mf.dispatchFetch(
      "http://test/test-org/my-claw/api/chat",
      {
        headers: { Cookie: "session=forbidden-sess-789" },
      },
    );
    // forbidden- sessions return 403 from mock, but auth.ts treats any non-ok as invalid
    expect(res.status).toBe(401);
  });
});

// ---------------------------------------------------------------------------
// Unauthenticated requests → 401
// ---------------------------------------------------------------------------

describe("unauthenticated requests", () => {
  it("rejects requests with no auth", async () => {
    const res = await mf.dispatchFetch("http://test/test-org/my-claw/api/chat");
    expect(res.status).toBe(401);

    const body = (await res.json()) as any;
    expect(body.error).toBe("Authentication required");
  });

  it("rejects requests to root path with no auth", async () => {
    const res = await mf.dispatchFetch("http://test/test-org/my-claw/");
    expect(res.status).toBe(401);
  });
});

// ---------------------------------------------------------------------------
// Unknown org/claw → 404
// ---------------------------------------------------------------------------

describe("unknown org/claw resolution", () => {
  it("returns 404 for unknown org", async () => {
    const res = await mf.dispatchFetch(
      "http://test/unknown-org/my-claw/api/chat",
      {
        headers: { Authorization: "Bearer some-token" },
      },
    );
    expect(res.status).toBe(404);

    const body = (await res.json()) as any;
    expect(body.error).toBe("Claw not found");
  });
});

// ---------------------------------------------------------------------------
// CORS preflight
// ---------------------------------------------------------------------------

describe("CORS preflight", () => {
  it("returns 204 with CORS headers for valid origin", async () => {
    const res = await mf.dispatchFetch(
      "http://test/test-org/my-claw/api/chat",
      {
        method: "OPTIONS",
        headers: {
          Origin: "https://mirascope.com",
          "Access-Control-Request-Method": "POST",
        },
      },
    );
    expect(res.status).toBe(204);
    expect(res.headers.get("Access-Control-Allow-Origin")).toBe(
      "https://mirascope.com",
    );
    expect(res.headers.get("Access-Control-Allow-Credentials")).toBe("true");
    expect(res.headers.get("Access-Control-Allow-Methods")).toContain("POST");
  });

  it("returns 403 for invalid origin", async () => {
    const res = await mf.dispatchFetch(
      "http://test/test-org/my-claw/api/chat",
      {
        method: "OPTIONS",
        headers: {
          Origin: "https://evil.com",
          "Access-Control-Request-Method": "POST",
        },
      },
    );
    expect(res.status).toBe(403);
  });

  it("does not intercept non-OPTIONS requests as preflight", async () => {
    const res = await mf.dispatchFetch(
      "http://test/test-org/my-claw/api/chat",
      {
        method: "GET",
        headers: {
          Origin: "https://mirascope.com",
          Authorization: "Bearer some-token",
        },
      },
    );
    // Should go through normal auth flow, not preflight
    expect(res.ok).toBe(true);
    const body = (await res.json()) as any;
    expect(body.action).toBe("pass-through");
    // Should include CORS headers on the response
    expect(res.headers.get("Access-Control-Allow-Origin")).toBe(
      "https://mirascope.com",
    );
  });
});

// ---------------------------------------------------------------------------
// Invalid paths
// ---------------------------------------------------------------------------

describe("invalid paths", () => {
  it("rejects paths with no org/claw", async () => {
    const res = await mf.dispatchFetch("http://test/");
    expect(res.status).toBe(400);
  });

  it("rejects single-segment paths", async () => {
    const res = await mf.dispatchFetch("http://test/just-one");
    expect(res.status).toBe(400);
  });
});

// ---------------------------------------------------------------------------
// Path parsing
// ---------------------------------------------------------------------------

describe("path parsing", () => {
  it("extracts org, claw, and remainder correctly", async () => {
    const res = await mf.dispatchFetch(
      "http://test/acme/support-bot/api/mcp/session",
      {
        headers: { Authorization: "Bearer tok" },
      },
    );
    expect(res.ok).toBe(true);

    const body = (await res.json()) as any;
    expect(body.orgSlug).toBe("acme");
    expect(body.clawSlug).toBe("support-bot");
    expect(body.remainder).toBe("/api/mcp/session");
  });

  it("handles root remainder (just /{org}/{claw})", async () => {
    const res = await mf.dispatchFetch("http://test/acme/support-bot", {
      headers: { Authorization: "Bearer tok" },
    });
    expect(res.ok).toBe(true);

    const body = (await res.json()) as any;
    expect(body.remainder).toBe("/");
  });
});
