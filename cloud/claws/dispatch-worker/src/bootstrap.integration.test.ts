/**
 * Integration tests for bootstrap functions using Miniflare.
 *
 * These tests spin up real Workers in Miniflare with service bindings,
 * exercising the actual fetch path that bootstrap.ts uses in production.
 *
 * Architecture:
 * - A "harness" worker wraps bootstrap function logic and exposes it via HTTP
 * - A "mock-cloud" worker simulates the Mirascope Cloud internal API
 * - The harness has MIRASCOPE_CLOUD service binding → mock-cloud
 * - Tests call dispatchFetch on the harness and assert responses
 *
 * Why not @cloudflare/vitest-pool-workers?
 * That package requires vitest 2.x–3.2.x; this project uses vitest 4.x.
 */

import { Miniflare } from "miniflare";
import { afterAll, beforeAll, describe, expect, it } from "vitest";

// -- Mock Cloud Worker script (inline) ------------------------------------
// Simulates the Mirascope Cloud internal API endpoints.
const MOCK_CLOUD_SCRIPT = `
export default {
  async fetch(request) {
    const url = new URL(request.url);

    // GET /api/internal/claws/:clawId/bootstrap
    const bootstrapMatch = url.pathname.match(
      /^\\/api\\/internal\\/claws\\/([\\w-]+)\\/bootstrap$/
    );
    if (bootstrapMatch && request.method === "GET") {
      const clawId = bootstrapMatch[1];
      if (clawId === "unknown-claw") {
        return new Response("claw not found", { status: 404 });
      }
      return Response.json({
        clawId,
        clawSlug: "test-claw",
        organizationId: "org-456",
        organizationSlug: "test-org",
        instanceType: "basic",
        r2: {
          bucketName: "claw-" + clawId,
          accessKeyId: "ak-test",
          secretAccessKey: "sk-test",
        },
        containerEnv: {
          MIRASCOPE_API_KEY: "mk-test",
          ANTHROPIC_API_KEY: "mk-test",
          ANTHROPIC_BASE_URL: "https://router.mirascope.com/v1",
          OPENCLAW_GATEWAY_TOKEN: "gw-tok",
        },
      });
    }

    // GET /api/internal/claws/resolve/:orgSlug/:clawSlug
    const resolveMatch = url.pathname.match(
      /^\\/api\\/internal\\/claws\\/resolve\\/([\\w-]+)\\/([\\w-]+)$/
    );
    if (resolveMatch && request.method === "GET") {
      const orgSlug = resolveMatch[1];
      const clawSlug = resolveMatch[2];
      if (orgSlug === "unknown-org") {
        return new Response("org not found", { status: 404 });
      }
      return Response.json({
        clawId: "resolved-" + clawSlug,
        organizationId: "org-" + orgSlug,
      });
    }

    // POST /api/internal/claws/:clawId/status
    const statusMatch = url.pathname.match(
      /^\\/api\\/internal\\/claws\\/([\\w-]+)\\/status$/
    );
    if (statusMatch && request.method === "POST") {
      const body = await request.json();
      return Response.json({ received: true, clawId: statusMatch[1], ...body });
    }

    return new Response("not found", { status: 404 });
  },
};
`;

// -- Harness Worker script (inline) ---------------------------------------
// Wraps bootstrap-like logic; exposes each function via a simple HTTP API.
// This replicates the exact fetch patterns from src/bootstrap.ts.
const HARNESS_SCRIPT = `
function internalFetch(env, path, init) {
  return env.MIRASCOPE_CLOUD.fetch("https://internal" + path, init);
}

async function fetchBootstrapConfig(clawId, env) {
  const response = await internalFetch(
    env,
    "/api/internal/claws/" + clawId + "/bootstrap",
    { method: "GET", headers: { "Content-Type": "application/json" } },
  );
  if (!response.ok) {
    const body = await response.text().catch(() => "(no body)");
    throw new Error(
      "Bootstrap config fetch failed for claw " + clawId + ": " +
      response.status + " " + response.statusText + " — " + body
    );
  }
  return response.json();
}

async function resolveClawId(orgSlug, clawSlug, env) {
  const response = await internalFetch(
    env,
    "/api/internal/claws/resolve/" + orgSlug + "/" + clawSlug,
    { method: "GET", headers: { "Content-Type": "application/json" } },
  );
  if (!response.ok) {
    const body = await response.text().catch(() => "(no body)");
    throw new Error(
      "Claw resolution failed for " + clawSlug + "." + orgSlug + ": " +
      response.status + " " + response.statusText + " — " + body
    );
  }
  return response.json();
}

async function reportClawStatus(clawId, status, env) {
  try {
    const response = await internalFetch(
      env,
      "/api/internal/claws/" + clawId + "/status",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(status),
      },
    );
    if (!response.ok) {
      return { ok: false, status: response.status };
    }
    return { ok: true, body: await response.json() };
  } catch (err) {
    return { ok: false, error: err.message };
  }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const action = url.pathname.slice(1); // strip leading /

    try {
      if (action === "fetchBootstrapConfig") {
        const clawId = url.searchParams.get("clawId");
        const result = await fetchBootstrapConfig(clawId, env);
        return Response.json({ ok: true, result });
      }

      if (action === "resolveClawId") {
        const orgSlug = url.searchParams.get("orgSlug");
        const clawSlug = url.searchParams.get("clawSlug");
        const result = await resolveClawId(orgSlug, clawSlug, env);
        return Response.json({ ok: true, result });
      }

      if (action === "reportClawStatus") {
        const clawId = url.searchParams.get("clawId");
        const status = await request.json();
        const result = await reportClawStatus(clawId, status, env);
        return Response.json({ ok: true, result });
      }

      return new Response("unknown action: " + action, { status: 400 });
    } catch (err) {
      return Response.json({ ok: false, error: err.message }, { status: 500 });
    }
  },
};
`;

let mf: Miniflare;

beforeAll(async () => {
  mf = new Miniflare({
    workers: [
      {
        name: "harness",
        modules: true,
        script: HARNESS_SCRIPT,
        compatibilityDate: "2025-05-06",
        serviceBindings: { MIRASCOPE_CLOUD: "mock-cloud" },
      },
      {
        name: "mock-cloud",
        modules: true,
        script: MOCK_CLOUD_SCRIPT,
        compatibilityDate: "2025-05-06",
      },
    ],
  });
});

afterAll(async () => {
  await mf?.dispose();
});

// =========================================================================
// fetchBootstrapConfig
// =========================================================================

describe("fetchBootstrapConfig (integration)", () => {
  it("fetches config via real service binding", async () => {
    const res = await mf.dispatchFetch(
      "http://harness.local/fetchBootstrapConfig?clawId=claw-123",
    );
    const data = (await res.json()) as {
      ok: boolean;
      result: { clawId: string; r2: { bucketName: string } };
    };

    expect(data.ok).toBe(true);
    expect(data.result.clawId).toBe("claw-123");
    expect(data.result.r2.bucketName).toBe("claw-claw-123");
  });

  it("returns all expected config fields", async () => {
    const res = await mf.dispatchFetch(
      "http://harness.local/fetchBootstrapConfig?clawId=test-abc",
    );
    const data = (await res.json()) as {
      ok: boolean;
      result: {
        clawId: string;
        clawSlug: string;
        organizationId: string;
        organizationSlug: string;
        instanceType: string;
        containerEnv: Record<string, string>;
      };
    };

    expect(data.ok).toBe(true);
    expect(data.result).toMatchObject({
      clawId: "test-abc",
      clawSlug: "test-claw",
      organizationId: "org-456",
      organizationSlug: "test-org",
      instanceType: "basic",
    });
    expect(data.result.containerEnv).toHaveProperty("MIRASCOPE_API_KEY");
    expect(data.result.containerEnv).toHaveProperty("OPENCLAW_GATEWAY_TOKEN");
  });

  it("throws on unknown claw (404)", async () => {
    const res = await mf.dispatchFetch(
      "http://harness.local/fetchBootstrapConfig?clawId=unknown-claw",
    );
    const data = (await res.json()) as { ok: boolean; error: string };

    expect(res.status).toBe(500);
    expect(data.ok).toBe(false);
    expect(data.error).toContain("404");
    expect(data.error).toContain("unknown-claw");
  });
});

// =========================================================================
// resolveClawId
// =========================================================================

describe("resolveClawId (integration)", () => {
  it("resolves slugs to clawId via real service binding", async () => {
    const res = await mf.dispatchFetch(
      "http://harness.local/resolveClawId?orgSlug=test-org&clawSlug=my-claw",
    );
    const data = (await res.json()) as {
      ok: boolean;
      result: { clawId: string; organizationId: string };
    };

    expect(data.ok).toBe(true);
    expect(data.result.clawId).toBe("resolved-my-claw");
    expect(data.result.organizationId).toBe("org-test-org");
  });

  it("throws on unknown org (404)", async () => {
    const res = await mf.dispatchFetch(
      "http://harness.local/resolveClawId?orgSlug=unknown-org&clawSlug=test",
    );
    const data = (await res.json()) as { ok: boolean; error: string };

    expect(res.status).toBe(500);
    expect(data.ok).toBe(false);
    expect(data.error).toContain("404");
  });
});

// =========================================================================
// reportClawStatus
// =========================================================================

describe("reportClawStatus (integration)", () => {
  it("posts status via real service binding", async () => {
    const res = await mf.dispatchFetch(
      "http://harness.local/reportClawStatus?clawId=claw-123",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          status: "active",
          startedAt: "2025-01-01T00:00:00Z",
        }),
      },
    );
    const data = (await res.json()) as {
      ok: boolean;
      result: {
        ok: boolean;
        body: { received: boolean; clawId: string; status: string };
      };
    };

    expect(data.ok).toBe(true);
    expect(data.result.ok).toBe(true);
    expect(data.result.body.received).toBe(true);
    expect(data.result.body.clawId).toBe("claw-123");
    expect(data.result.body.status).toBe("active");
  });

  it("reports error status with errorMessage", async () => {
    const res = await mf.dispatchFetch(
      "http://harness.local/reportClawStatus?clawId=claw-456",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          status: "error",
          errorMessage: "Gateway crashed",
        }),
      },
    );
    const data = (await res.json()) as {
      ok: boolean;
      result: {
        ok: boolean;
        body: { status: string; errorMessage: string };
      };
    };

    expect(data.ok).toBe(true);
    expect(data.result.body.status).toBe("error");
    expect(data.result.body.errorMessage).toBe("Gateway crashed");
  });
});
