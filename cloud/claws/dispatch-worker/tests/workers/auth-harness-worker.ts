/**
 * Test harness worker for auth integration tests.
 *
 * Exposes auth functions via HTTP so integration tests can invoke
 * them through a real Miniflare worker runtime with real service bindings.
 *
 * Routes:
 *   POST /auth — run authenticate() on a synthetic request
 *   OPTIONS /preflight — test CORS preflight handling
 *   ANY /{org}/{claw}/* — full auth flow (authenticate + return result)
 */
import type { DispatchEnv } from "../../src/types";

import {
  authenticate,
  clearSessionCache,
  corsHeaders,
  handlePreflight,
  parsePath,
} from "../../src/auth";

export default {
  async fetch(request: Request, env: DispatchEnv): Promise<Response> {
    const url = new URL(request.url);
    const { pathname } = url;

    try {
      // POST /clear-cache — clear session cache between tests
      if (pathname === "/clear-cache" && request.method === "POST") {
        clearSessionCache();
        return Response.json({ ok: true });
      }

      // CORS preflight handling
      const preflight = handlePreflight(request);
      if (preflight) return preflight;

      // Parse path
      const parsed = parsePath(pathname);
      if (!parsed) {
        return Response.json(
          { error: "Invalid path — expected /{org}/{claw}/..." },
          { status: 400 },
        );
      }

      // Run auth
      const result = await authenticate(request, parsed, env);

      const origin = request.headers.get("Origin");
      const cors = corsHeaders(origin);

      if (result.action === "reject") {
        return Response.json(
          { error: result.message },
          { status: result.status, headers: cors },
        );
      }

      // Success: return the auth result + parsed path info
      return Response.json(
        {
          action: "pass-through",
          clawId: result.clawId,
          orgSlug: parsed.orgSlug,
          clawSlug: parsed.clawSlug,
          remainder: parsed.remainder,
        },
        { headers: cors },
      );
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      const origin = request.headers.get("Origin");
      const cors = corsHeaders(origin);
      return Response.json({ error: message }, { status: 500, headers: cors });
    }
  },
};
