/**
 * Integration tests for bootstrap functions via real Miniflare service bindings.
 *
 * These tests spin up a Miniflare instance with:
 * - A test harness worker (main) that exposes bootstrap functions via HTTP
 * - A mock cloud worker bound as MIRASCOPE_CLOUD via function service binding
 *
 * This validates that service binding fetch calls work end-to-end through
 * the Workers runtime, unlike unit tests which mock the binding entirely.
 */
import * as esbuild from "esbuild";
import { Miniflare } from "miniflare";
import path from "node:path";
import { afterAll, beforeAll, describe, expect, it } from "vitest";

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
    path.join(base, "workers/test-harness-worker.ts"),
  );

  mf = new Miniflare({
    modules: true,
    script: harnessScript,
    compatibilityDate: "2025-05-06",
    compatibilityFlags: ["nodejs_compat"],

    // Use function-based service binding so the URL is properly forwarded
    // (named worker bindings in Miniflare forward the original request URL)
    serviceBindings: {
      MIRASCOPE_CLOUD: mockCloudWorker.fetch,
    },
  });

  await mf.ready;
});

afterAll(async () => {
  await mf?.dispose();
});

// ---------------------------------------------------------------------------
// fetchBootstrapConfig
// ---------------------------------------------------------------------------

describe("fetchBootstrapConfig (integration)", () => {
  it("fetches config via real service binding", async () => {
    const res = await mf.dispatchFetch("http://test/bootstrap/claw-123");
    expect(res.ok).toBe(true);

    const config = (await res.json()) as Record<string, unknown>;
    expect(config.clawId).toBe("claw-123");
    expect(config.clawSlug).toBe("test-claw");
    expect(config.organizationId).toBe("org-456");
    expect((config.r2 as any).bucketName).toBe("claw-claw-123");
  });

  it("returns error for nonexistent claw", async () => {
    const res = await mf.dispatchFetch("http://test/bootstrap/nonexistent");
    expect(res.status).toBe(500);

    const body = (await res.json()) as { error: string };
    expect(body.error).toContain("404");
    expect(body.error).toContain("nonexistent");
  });
});

// ---------------------------------------------------------------------------
// resolveClawId
// ---------------------------------------------------------------------------

describe("resolveClawId (integration)", () => {
  it("resolves slugs to clawId via service binding", async () => {
    const res = await mf.dispatchFetch("http://test/resolve/test-org/my-claw");
    expect(res.ok).toBe(true);

    const result = (await res.json()) as Record<string, string>;
    expect(result.clawId).toBe("resolved-my-claw");
    expect(result.organizationId).toBe("org-test-org");
  });

  it("returns error for unknown org", async () => {
    const res = await mf.dispatchFetch(
      "http://test/resolve/unknown-org/some-claw",
    );
    expect(res.status).toBe(500);

    const body = (await res.json()) as { error: string };
    expect(body.error).toContain("404");
  });
});

// ---------------------------------------------------------------------------
// reportClawStatus
// ---------------------------------------------------------------------------

describe("reportClawStatus (integration)", () => {
  it("posts status via service binding without throwing", async () => {
    const res = await mf.dispatchFetch("http://test/status/claw-123", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        status: "active",
        startedAt: "2025-01-01T00:00:00Z",
      }),
    });
    expect(res.ok).toBe(true);

    const body = (await res.json()) as { ok: boolean };
    expect(body.ok).toBe(true);
  });
});
