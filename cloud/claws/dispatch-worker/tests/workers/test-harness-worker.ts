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

export default {
  async fetch(request: Request, env: DispatchEnv): Promise<Response> {
    const url = new URL(request.url);
    const { pathname } = url;

    try {
      // GET /bootstrap/:clawId
      const bootstrapMatch = pathname.match(/^\/bootstrap\/([\w-]+)$/);
      if (bootstrapMatch) {
        const config = await fetchBootstrapConfig(bootstrapMatch[1], env);
        return Response.json(config);
      }

      // GET /resolve/:orgSlug/:clawSlug
      const resolveMatch = pathname.match(/^\/resolve\/([\w-]+)\/([\w-]+)$/);
      if (resolveMatch) {
        const result = await resolveClawId(
          resolveMatch[1],
          resolveMatch[2],
          env,
        );
        return Response.json(result);
      }

      // POST /status/:clawId
      const statusMatch = pathname.match(/^\/status\/([\w-]+)$/);
      if (statusMatch && request.method === "POST") {
        const body = await request.json();
        await reportClawStatus(statusMatch[1], body as any, env);
        return Response.json({ ok: true });
      }

      return new Response("unknown route", { status: 404 });
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      return Response.json({ error: message }, { status: 500 });
    }
  },
};
