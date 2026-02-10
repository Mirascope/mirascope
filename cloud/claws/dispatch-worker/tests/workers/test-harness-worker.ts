import { Effect, Exit } from "effect";

import type { DispatchEnv } from "../../src/types";

/**
 * Test harness worker for integration tests.
 *
 * Exposes bootstrap functions via HTTP so integration tests can invoke
 * them through a real Miniflare worker runtime with real service bindings.
 *
 * Routes:
 *   GET  /bootstrap/:clawId       → fetchBootstrapConfig
 *   GET  /resolve/:orgSlug/:claw  → resolveClawId
 *   POST /status/:clawId          → reportClawStatus
 */
import {
  fetchBootstrapConfig,
  resolveClawId,
  reportClawStatus,
} from "../../src/bootstrap";

/** Extract a human-readable message from an Effect exit failure. */
function exitErrorMessage(exit: Exit.Exit<unknown, unknown>): string {
  if (Exit.isFailure(exit) && exit.cause._tag === "Fail") {
    const err = exit.cause.error;
    if (typeof err === "object" && err !== null) {
      // Include all fields for test assertions (e.g. statusCode, message)
      return JSON.stringify(err);
    }
    return String(err);
  }
  return "Unknown error";
}

export default {
  async fetch(request: Request, env: DispatchEnv): Promise<Response> {
    const url = new URL(request.url);
    const { pathname } = url;

    // GET /bootstrap/:clawId
    const bootstrapMatch = pathname.match(/^\/bootstrap\/([\w-]+)$/);
    if (bootstrapMatch) {
      const exit = await Effect.runPromiseExit(
        fetchBootstrapConfig(bootstrapMatch[1], env),
      );
      if (Exit.isSuccess(exit)) {
        return Response.json(exit.value);
      }
      return Response.json({ error: exitErrorMessage(exit) }, { status: 500 });
    }

    // GET /resolve/:orgSlug/:clawSlug
    const resolveMatch = pathname.match(/^\/resolve\/([\w-]+)\/([\w-]+)$/);
    if (resolveMatch) {
      const exit = await Effect.runPromiseExit(
        resolveClawId(resolveMatch[1], resolveMatch[2], env),
      );
      if (Exit.isSuccess(exit)) {
        return Response.json(exit.value);
      }
      return Response.json({ error: exitErrorMessage(exit) }, { status: 500 });
    }

    // POST /status/:clawId
    const statusMatch = pathname.match(/^\/status\/([\w-]+)$/);
    if (statusMatch && request.method === "POST") {
      const body = await request.json();
      await Effect.runPromise(
        reportClawStatus(
          statusMatch[1],
          body as { status: string; errorMessage?: string; startedAt?: string },
          env,
        ),
      );
      return Response.json({ ok: true });
    }

    return new Response("unknown route", { status: 404 });
  },
};
