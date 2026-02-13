/**
 * Claw Dispatch Worker
 *
 * Routes incoming requests to per-claw Cloudflare Sandbox containers.
 *
 * Two routing modes:
 * 1. Internal (/_internal/*) — clawId from Host header (service binding traffic)
 * 2. External (/{orgSlug}/{clawSlug}/*) — path-based routing with auth
 *
 * For external requests:
 *    a. Parse org + claw slugs from URL path
 *    b. Authenticate (webhooks pass-through, Bearer pass-through, session cookie validated)
 *    c. Resolve slugs → clawId via Cloud internal API
 *    d. Fetch bootstrap config, start gateway, proxy HTTP/WS
 *
 * See cloud/claws/README.md for the full architecture.
 */

import { getSandbox, Sandbox } from "@cloudflare/sandbox";
import { Effect } from "effect";
import { Hono } from "hono";

import type { AppEnv, SandboxProcessStatus } from "./types";

import { handlePreflight, parsePath } from "./auth";
import { resolveClawId } from "./bootstrap";
import { handleProxy, runAuth } from "./handler";
import { internal } from "./internal";
import { findGatewayProcess } from "./proxy";
import { validateEnv } from "./settings";
import { PROCESS_TO_HEALTH_STATUS } from "./types";
import { extractClawId } from "./utils";

export { Sandbox };

// Main app
const app = new Hono<AppEnv>();

// Validate env bindings on every request (fail fast with clear errors)
app.use("*", async (c, next) => {
  validateEnv(c.env);
  await next();
});

// ---------------------------------------------------------------------------
// Internal routes: /_internal/* — Host-based clawId extraction (service binding traffic)
// ---------------------------------------------------------------------------
app.use("/_internal/*", async (c, next) => {
  // Prefer explicit X-Claw-Id header (CF may clobber Host on custom domains)
  const explicitClawId = c.req.header("X-Claw-Id");
  const host = c.req.header("Host") || "";
  const clawId = explicitClawId || extractClawId(host);

  if (!clawId) {
    return c.json(
      { error: "Invalid host header — cannot determine clawId", host },
      400,
    );
  }

  console.log(`[REQ] ${c.req.method} ${c.req.path} clawId=${clawId}`);

  const sandbox = getSandbox(c.env.Sandbox, clawId, { keepAlive: true });
  c.set("sandbox", sandbox);
  c.set("clawId", clawId);

  await next();
});

app.route("/_internal", internal);

// ---------------------------------------------------------------------------
// Health check endpoint — bypasses auth, does not start container
// ---------------------------------------------------------------------------
app.get("/:orgSlug/:clawSlug/_health", async (c) => {
  const { orgSlug, clawSlug } = c.req.param();

  // Resolve claw slugs → clawId (does NOT start a container)
  const resolveResult = await Effect.runPromiseExit(
    resolveClawId(orgSlug, clawSlug, c.env),
  );

  if (resolveResult._tag === "Failure") {
    return c.json({ status: "not_found" }, 404);
  }

  const { clawId } = resolveResult.value;

  // Check gateway process state without triggering startup
  try {
    const sandbox = getSandbox(c.env.Sandbox, clawId, { keepAlive: true });
    const process = await findGatewayProcess(sandbox);

    if (process !== null) {
      const status =
        PROCESS_TO_HEALTH_STATUS[process.status as SandboxProcessStatus] ??
        "stopped";
      return c.json({ clawId, status, rawStatus: process.status });
    }
  } catch (err) {
    console.log("[health] Could not check sandbox state:", err);
  }

  return c.json({ status: "stopped", clawId });
});

// ---------------------------------------------------------------------------
// External routes: /{orgSlug}/{clawSlug}/* — path-based routing with auth
// ---------------------------------------------------------------------------
app.all("*", async (c) => {
  const preflight = handlePreflight(c.req.raw, c.env);
  if (preflight) return preflight;

  const parsed = parsePath(c.req.path);
  if (!parsed) {
    return c.json({ error: "Invalid path — expected /{org}/{claw}/..." }, 400);
  }

  const auth = await runAuth(c.req.raw, parsed, c.env);
  if (auth instanceof Response) return auth;

  return handleProxy(c, auth, parsed);
});

export default {
  fetch: app.fetch,
};
