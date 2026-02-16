/**
 * Server-side WebSocket proxy for the OpenClaw gateway.
 *
 * Handles the `/api/ws/claws/:orgSlug/:clawSlug` endpoint:
 * 1. Authenticates the user via session cookie
 * 2. Resolves the claw and verifies membership
 * 3. Decrypts claw secrets to obtain the gateway token
 * 4. Opens a WebSocket to the upstream gateway
 * 5. Performs the OpenClaw connect handshake (challenge → auth)
 * 6. Relays JSON-RPC messages bidirectionally between browser and gateway
 *
 * The browser never sees the gateway token.
 */
import { and, eq } from "drizzle-orm";
import { Effect, Layer } from "effect";

import { getSessionIdFromCookie } from "@/auth/utils";
import { decryptSecrets } from "@/claws/crypto";
import { DrizzleORM } from "@/db/client";
import { Database } from "@/db/database";
import { claws, organizations, organizationMemberships } from "@/db/schema";
import { DatabaseError, NotFoundError, UnauthorizedError } from "@/errors";
import { settingsLayer } from "@/server-entry";
import { Settings } from "@/settings";

// ---------------------------------------------------------------------------
// Path parsing
// ---------------------------------------------------------------------------

function parseWsPath(pathname: string): {
  orgSlug: string;
  clawSlug: string;
} | null {
  // Expected: /api/ws/claws/:orgSlug/:clawSlug
  const match = pathname.match(/^\/api\/ws\/claws\/([^/]+)\/([^/]+)$/);
  if (!match) return null;
  return { orgSlug: match[1], clawSlug: match[2] };
}

// ---------------------------------------------------------------------------
// Core handler
// ---------------------------------------------------------------------------

/**
 * Handle a WebSocket upgrade request for claw chat.
 *
 * Called from server-entry.ts when:
 *   - `Upgrade: websocket` header is present
 *   - pathname starts with `/api/ws/claws/`
 */
export async function handleClawsWebSocket(
  request: Request,
  url: URL,
): Promise<Response> {
  const handler = Effect.gen(function* () {
    const settings = yield* Settings;

    // 1. Parse path
    const parsed = parseWsPath(url.pathname);
    if (!parsed) {
      return new Response("Invalid WebSocket path", { status: 400 });
    }
    const { orgSlug, clawSlug } = parsed;

    // 2. Authenticate via session cookie
    const db = yield* Database;
    const sessionId = getSessionIdFromCookie(request);
    if (!sessionId) {
      return new Response("Authentication required", { status: 401 });
    }

    const user = yield* db.sessions
      .findUserBySessionId(sessionId)
      .pipe(
        Effect.catchAll(() =>
          Effect.fail(new UnauthorizedError({ message: "Invalid session" })),
        ),
      );

    // 3. Resolve claw by org slug + claw slug
    const client = yield* DrizzleORM;

    const [claw] = yield* client
      .select({
        clawId: claws.id,
        organizationId: claws.organizationId,
        secretsEncrypted: claws.secretsEncrypted,
        secretsKeyId: claws.secretsKeyId,
      })
      .from(claws)
      .innerJoin(organizations, eq(claws.organizationId, organizations.id))
      .where(and(eq(organizations.slug, orgSlug), eq(claws.slug, clawSlug)))
      .limit(1)
      .pipe(
        Effect.mapError(
          (e) =>
            new DatabaseError({
              message: "Failed to resolve claw",
              cause: e,
            }),
        ),
      );

    if (!claw) {
      return yield* Effect.fail(
        new NotFoundError({
          message: `Claw ${clawSlug} not found in organization ${orgSlug}`,
          resource: "claw",
        }),
      );
    }

    // 4. Verify user has access (is org member)
    const [membership] = yield* client
      .select({ memberId: organizationMemberships.memberId })
      .from(organizationMemberships)
      .where(
        and(
          eq(organizationMemberships.memberId, user.id),
          eq(organizationMemberships.organizationId, claw.organizationId),
        ),
      )
      .limit(1)
      .pipe(
        Effect.mapError(
          (e) =>
            new DatabaseError({
              message: "Failed to verify membership",
              cause: e,
            }),
        ),
      );

    if (!membership) {
      return new Response("Not a member of this organization", {
        status: 403,
      });
    }

    // 5. Decrypt claw secrets to get gateway token
    const secrets =
      claw.secretsEncrypted && claw.secretsKeyId
        ? yield* decryptSecrets(claw.secretsEncrypted, claw.secretsKeyId)
        : {};

    const gatewayToken = secrets.OPENCLAW_GATEWAY_TOKEN as string | undefined;
    if (!gatewayToken) {
      return new Response("Gateway token not configured for this claw", {
        status: 503,
      });
    }

    // 6. Determine upstream gateway URL
    // Route through the dispatch worker which handles container lifecycle.
    // The dispatch worker authenticates via session cookie (forwarded from
    // the original request), then proxies to the container gateway.
    const dispatchBaseUrl =
      settings.openclawGatewayWsUrl ??
      settings.cloudflare.dispatchWorkerBaseUrl;
    const upstreamUrl = `${dispatchBaseUrl.replace(/\/$/, "")}/${orgSlug}/${clawSlug}`;

    // Forward the session cookie for dispatch worker auth.
    // The gateway token is only used for the connect handshake with the
    // gateway inside the container — it never leaves as a credential.
    const cookieHeader = request.headers.get("Cookie");

    // 7. Connect to upstream gateway, perform handshake, and relay
    return yield* Effect.tryPromise({
      try: () => connectAndRelay(upstreamUrl, gatewayToken, cookieHeader),
      catch: (cause) =>
        new DatabaseError({
          message: `Failed to connect to gateway: ${cause instanceof Error ? cause.message : String(cause)}`,
          cause,
        }),
    });
  }).pipe(
    Effect.catchAll((error) => {
      console.error("[ws-proxy] Error:", error);
      const status =
        typeof error === "object" &&
        error !== null &&
        error.constructor &&
        "status" in error.constructor
          ? (error.constructor as { status: number }).status
          : 500;
      const message =
        error instanceof Error ? error.message : "Internal server error";
      return Effect.succeed(new Response(message, { status }));
    }),
    Effect.catchAllDefect((defect) => {
      console.error("[ws-proxy] Defect:", defect);
      return Effect.succeed(
        new Response("Internal server error", { status: 500 }),
      );
    }),
    Effect.provide(
      Layer.unwrapEffect(
        Effect.gen(function* () {
          const settings = yield* Settings;
          return Layer.mergeAll(
            Layer.succeed(Settings, settings),
            Database.Live({
              database: { connectionString: settings.databaseUrl },
              payments: settings.stripe,
            }),
          );
        }).pipe(Effect.provide(settingsLayer)),
      ),
    ),
  );

  return Effect.runPromise(handler);
}

// ---------------------------------------------------------------------------
// Upstream connection + handshake + relay
// ---------------------------------------------------------------------------

/**
 * Open upstream WS, perform connect handshake, then create a WebSocketPair
 * for the browser and relay messages bidirectionally.
 */
async function connectAndRelay(
  gatewayBaseUrl: string,
  gatewayToken: string,
  cookieHeader: string | null,
): Promise<Response> {
  // Create WebSocket pair for browser ↔ proxy
  const [clientWs, serverWs] = Object.values(new WebSocketPair());

  // Connect to upstream via fetch + Upgrade
  // Routes through the dispatch worker which authenticates via session cookie.
  // The gateway token is used later for the connect handshake with the gateway.
  const headers: Record<string, string> = { Upgrade: "websocket" };
  if (cookieHeader) {
    headers.Cookie = cookieHeader;
  }
  const upstreamResponse = await fetch(gatewayBaseUrl, { headers });

  const upstreamWs = (upstreamResponse as unknown as { webSocket?: WebSocket })
    .webSocket;
  if (!upstreamWs) {
    console.error(
      "[ws-proxy] Upstream response status:",
      upstreamResponse.status,
      "headers:",
      Object.fromEntries(upstreamResponse.headers.entries()),
    );
    throw new Error("Upstream did not return a WebSocket");
  }

  upstreamWs.accept();
  serverWs.accept();

  // Perform connect handshake with upstream gateway
  // Wait for challenge, then send auth
  const handshakePromise = new Promise<void>((resolve, reject) => {
    const timeout = setTimeout(() => {
      reject(new Error("Gateway handshake timed out"));
    }, 10_000);

    const onMessage = (event: MessageEvent) => {
      try {
        const msg = JSON.parse(event.data as string);

        if (msg.type === "event" && msg.event === "connect.challenge") {
          // Respond with connect request including auth token
          upstreamWs.send(
            JSON.stringify({
              type: "req",
              id: "__connect",
              method: "connect",
              params: {
                minProtocol: 3,
                maxProtocol: 3,
                auth: { token: gatewayToken },
                client: {
                  id: "openclaw-control-ui",
                  version: "dev",
                  platform: "server",
                  mode: "webchat",
                },
                role: "operator",
                scopes: [
                  "operator.admin",
                  "operator.approvals",
                  "operator.pairing",
                ],
                caps: [],
              },
            }),
          );
        } else if (msg.type === "res" && msg.id === "__connect") {
          clearTimeout(timeout);
          upstreamWs.removeEventListener("message", onMessage);

          if (msg.ok) {
            resolve();
          } else {
            reject(
              new Error(
                `Gateway connect failed: ${JSON.stringify(msg.error ?? msg.payload)}`,
              ),
            );
          }
        }
      } catch (e) {
        clearTimeout(timeout);
        reject(e);
      }
    };

    upstreamWs.addEventListener("message", onMessage);
  });

  await handshakePromise;

  // Signal browser that proxy is ready for messages
  serverWs.send(JSON.stringify({ type: "proxy.ready" }));

  // Set up bidirectional relay (browser ↔ gateway)
  // Relay: browser → gateway
  serverWs.addEventListener("message", (event) => {
    if (upstreamWs.readyState === WebSocket.OPEN) {
      upstreamWs.send(event.data);
    }
  });

  // Relay: gateway → browser
  upstreamWs.addEventListener("message", (event) => {
    if (serverWs.readyState === WebSocket.OPEN) {
      serverWs.send(event.data);
    }
  });

  // Close propagation
  serverWs.addEventListener("close", (event) => {
    const safeCode =
      event.code < 1000 || [1004, 1005, 1006, 1015].includes(event.code)
        ? 1001
        : event.code;
    upstreamWs.close(safeCode, event.reason);
  });
  upstreamWs.addEventListener("close", (event) => {
    let reason = event.reason;
    if (new TextEncoder().encode(reason).length > 123) {
      // Truncate by bytes, not characters
      const encoder = new TextEncoder();
      const decoder = new TextDecoder();
      const bytes = encoder.encode(reason);
      reason = decoder.decode(bytes.slice(0, 120)) + "...";
    }
    const safeCode =
      event.code < 1000 || [1004, 1005, 1006, 1015].includes(event.code)
        ? 1001
        : event.code;
    serverWs.close(safeCode, reason);
  });

  // Error propagation
  serverWs.addEventListener("error", () => {
    upstreamWs.close(1011, "Client error");
  });
  upstreamWs.addEventListener("error", () => {
    serverWs.close(1011, "Gateway error");
  });

  return new Response(null, { status: 101, webSocket: clientWs });
}
