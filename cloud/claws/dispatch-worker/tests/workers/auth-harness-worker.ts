/**
 * Test harness worker for auth integration tests.
 *
 * Exposes auth functions via HTTP so integration tests can invoke
 * them through a real Miniflare worker runtime with real service bindings.
 *
 * Routes:
 *   POST /clear-cache — clear session cache
 *   OPTIONS /preflight — test CORS preflight handling
 *   ANY /{org}/{claw}/* — full auth flow (authenticate + return result)
 */
import { Effect, Exit } from "effect";

import type { DispatchEnv } from "../../src/types";

import {
  type AuthError,
  authenticate,
  clearSessionCache,
  corsHeaders,
  handlePreflight,
  parsePath,
} from "../../src/auth";

function authErrorToResponse(
  error: AuthError,
  origin: string | null,
  env: DispatchEnv,
): Response {
  const cors = corsHeaders(origin, env);

  switch (error._tag) {
    case "ClawResolutionError":
      return Response.json(
        { error: "Claw not found" },
        { status: 404, headers: cors },
      );
    case "InvalidSessionError":
      return Response.json(
        { error: error.message },
        { status: 401, headers: cors },
      );
    case "UnauthenticatedError":
      return Response.json(
        { error: error.message },
        { status: 401, headers: cors },
      );
    case "ApiDecodeError":
    case "BootstrapDecodeError":
      return Response.json(
        { error: "Internal error" },
        { status: 502, headers: cors },
      );
  }
}

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
      const preflight = handlePreflight(request, env);
      if (preflight) return preflight;

      // Parse path
      const parsed = parsePath(pathname);
      if (!parsed) {
        return Response.json(
          { error: "Invalid path — expected /{org}/{claw}/..." },
          { status: 400 },
        );
      }

      // Run auth via Effect
      const origin = request.headers.get("Origin");
      const exit = await Effect.runPromiseExit(
        authenticate(request, parsed, env),
      );

      if (Exit.isFailure(exit)) {
        const cause = exit.cause;
        if (cause._tag === "Fail") {
          return authErrorToResponse(cause.error, origin, env);
        }
        // Unexpected defect
        console.error("[auth-harness] Unexpected defect:", cause);
        return Response.json({ error: "Internal error" }, { status: 500 });
      }

      const cors = corsHeaders(origin, env);

      // Success: return the auth result + parsed path info
      return Response.json(
        {
          action: "pass-through",
          clawId: exit.value.clawId,
          orgSlug: parsed.orgSlug,
          clawSlug: parsed.clawSlug,
          remainder: parsed.remainder,
        },
        { headers: cors },
      );
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      const origin = request.headers.get("Origin");
      const cors = corsHeaders(origin, env);
      return Response.json({ error: message }, { status: 500, headers: cors });
    }
  },
};
