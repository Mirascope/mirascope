/**
 * Mock Mirascope Cloud worker for integration tests.
 *
 * Simulates the internal API endpoints that the dispatch worker
 * calls via the MIRASCOPE_CLOUD service binding.
 */
export default {
  async fetch(request: Request): Promise<Response> {
    const url = new URL(request.url);
    const { pathname } = url;

    // POST /api/internal/claws/:clawId/status
    const statusMatch = pathname.match(
      /^\/api\/internal\/claws\/([\w-]+)\/status$/,
    );
    if (statusMatch && request.method === "POST") {
      const body = await request.json();
      return Response.json({ ok: true, received: body });
    }

    // GET /api/internal/claws/resolve/:orgSlug/:clawSlug
    const resolveMatch = pathname.match(
      /^\/api\/internal\/claws\/resolve\/([\w-]+)\/([\w-]+)$/,
    );
    if (resolveMatch) {
      const [, orgSlug, clawSlug] = resolveMatch;
      if (orgSlug === "unknown-org") {
        return new Response("organization not found", { status: 404 });
      }
      return Response.json({
        clawId: `resolved-${clawSlug}`,
        organizationId: `org-${orgSlug}`,
      });
    }

    // GET /api/internal/claws/:clawId/bootstrap
    const bootstrapMatch = pathname.match(
      /^\/api\/internal\/claws\/([\w-]+)\/bootstrap$/,
    );
    if (bootstrapMatch) {
      const [, clawId] = bootstrapMatch;
      if (clawId === "nonexistent") {
        return new Response("claw not found", { status: 404 });
      }
      return Response.json({
        clawId,
        clawSlug: "test-claw",
        organizationId: "org-456",
        organizationSlug: "test-org",
        instanceType: "basic",
        r2: {
          bucketName: `claw-${clawId}`,
          accessKeyId: "ak-test",
          secretAccessKey: "sk-test",
        },
        containerEnv: {
          MIRASCOPE_API_KEY: "mk-test",
          OPENCLAW_GATEWAY_TOKEN: "gw-tok",
        },
      });
    }

    // POST /api/internal/auth/validate-session
    if (
      pathname === "/api/internal/auth/validate-session" &&
      request.method === "POST"
    ) {
      const body = (await request.json()) as {
        sessionId: string;
        organizationSlug: string;
        clawSlug: string;
      };

      // Simulate valid sessions: session IDs starting with "valid-"
      if (body.sessionId.startsWith("valid-")) {
        return Response.json({
          userId: `user-${body.sessionId}`,
          clawId: `resolved-${body.clawSlug}`,
          organizationId: `org-${body.organizationSlug}`,
          role: "DEVELOPER",
        });
      }

      // Simulate forbidden: session IDs starting with "forbidden-"
      if (body.sessionId.startsWith("forbidden-")) {
        return Response.json(
          { error: "Insufficient permissions" },
          { status: 403 },
        );
      }

      // All other sessions are invalid
      return Response.json({ error: "Invalid session" }, { status: 401 });
    }

    return new Response("not found", { status: 404 });
  },
};
