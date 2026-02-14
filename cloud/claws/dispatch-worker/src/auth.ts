/**
 * Auth middleware for the dispatch worker.
 *
 * Implements the auth decision matrix from cloud/claws/README.md:
 *
 *   Path                           Auth Method              Validated By
 *   /{org}/{claw}/webhook/*        Platform-specific        Gateway (pass-through)
 *   /{org}/{claw}/*  + Bearer      OPENCLAW_GATEWAY_TOKEN   Gateway (pass-through)
 *   /{org}/{claw}/*  + Cookie      Mirascope session        Dispatch worker → Cloud API
 *   /{org}/{claw}/*  (no auth)     Reject                   Dispatch worker (401)
 *   /_internal/*                   Service binding          Implicit (in-process)
 */

import { Data, Effect } from "effect";

import type { DispatchEnv } from "./types";

import {
  type BootstrapDecodeError,
  type ClawResolutionError,
  resolveClawId,
} from "./bootstrap";

// ---------------------------------------------------------------------------
// Errors
// ---------------------------------------------------------------------------

/** Session cookie validation failed. */
export class InvalidSessionError extends Data.TaggedError(
  "InvalidSessionError",
)<{
  readonly message: string;
}> {}

/** No authentication credentials provided. */
export class UnauthenticatedError extends Data.TaggedError(
  "UnauthenticatedError",
)<{
  readonly message: string;
}> {}

/** JSON decode failed when parsing API response. */
export class ApiDecodeError extends Data.TaggedError("ApiDecodeError")<{
  readonly message: string;
  readonly cause?: unknown;
}> {}

export type AuthError =
  | ClawResolutionError
  | BootstrapDecodeError
  | InvalidSessionError
  | UnauthenticatedError
  | ApiDecodeError;

// ---------------------------------------------------------------------------
// Path parsing
// ---------------------------------------------------------------------------

export interface ParsedPath {
  orgSlug: string;
  clawSlug: string;
  /** The remainder after /{org}/{claw}, e.g. "/webhook/telegram" or "/api/chat" */
  remainder: string;
}

/**
 * Parse /{orgSlug}/{clawSlug}/... from a URL path.
 * Returns null if the path doesn't match the expected pattern.
 */
export function parsePath(pathname: string): ParsedPath | null {
  const match = pathname.match(/^\/([\w-]+)\/([\w-]+)(\/.*)?$/);
  if (!match) return null;
  return {
    orgSlug: match[1],
    clawSlug: match[2],
    remainder: match[3] || "/",
  };
}

// ---------------------------------------------------------------------------
// Session validation cache
// ---------------------------------------------------------------------------

interface CachedSession {
  userId: string;
  clawId: string;
  organizationId: string;
  role: string;
  expiresAt: number;
}

const SESSION_CACHE_TTL_MS = 60_000; // 60 seconds
const sessionCache = new Map<string, CachedSession>();

function getSessionCacheKey(
  sessionId: string,
  orgSlug: string,
  clawSlug: string,
): string {
  return `${sessionId}:${orgSlug}:${clawSlug}`;
}

/**
 * Validate a session cookie via the MIRASCOPE_CLOUD service binding.
 * Results are cached for 60s.
 */
export const validateSession = (
  sessionId: string,
  orgSlug: string,
  clawSlug: string,
  env: DispatchEnv,
): Effect.Effect<CachedSession, InvalidSessionError | ApiDecodeError> =>
  Effect.gen(function* () {
    const cacheKey = getSessionCacheKey(sessionId, orgSlug, clawSlug);
    const cached = sessionCache.get(cacheKey);
    if (cached && cached.expiresAt > Date.now()) {
      return cached;
    }

    const response = yield* Effect.tryPromise({
      try: () =>
        env.MIRASCOPE_CLOUD.fetch(
          "https://internal/api/internal/auth/validate-session",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              sessionId,
              organizationSlug: orgSlug,
              clawSlug,
            }),
          },
        ),
      catch: (cause) =>
        new ApiDecodeError({
          message: "Failed to call validate-session API",
          cause,
        }),
    });

    if (!response.ok) {
      sessionCache.delete(cacheKey);
      return yield* new InvalidSessionError({ message: "Invalid session" });
    }

    const data = yield* Effect.tryPromise({
      try: () =>
        response.json() as Promise<{
          userId: string;
          clawId: string;
          organizationId: string;
          role: string;
        }>,
      catch: (cause) =>
        new ApiDecodeError({
          message: "Failed to decode validate-session response",
          cause,
        }),
    });

    const entry: CachedSession = {
      ...data,
      expiresAt: Date.now() + SESSION_CACHE_TTL_MS,
    };
    sessionCache.set(cacheKey, entry);
    return entry;
  });

// ---------------------------------------------------------------------------
// CORS helpers
// ---------------------------------------------------------------------------

function isAllowedOrigin(origin: string, siteUrl: string): boolean {
  try {
    const allowed = new URL(siteUrl);
    const incoming = new URL(origin);
    // The URL API automatically normalizes default ports in .origin
    // https://example.com:443 -> https://example.com
    // http://example.com:80 -> http://example.com
    return incoming.origin === allowed.origin;
  } catch {
    return false;
  }
}

export function corsHeaders(
  origin: string | null,
  env: DispatchEnv,
  includePreflightHeaders = false,
  requestedHeaders?: string | null,
): Record<string, string> {
  if (!origin || !isAllowedOrigin(origin, env.SITE_URL)) return {};

  const headers: Record<string, string> = {
    "Access-Control-Allow-Origin": origin,
    "Access-Control-Allow-Credentials": "true",
    Vary: "Origin",
  };

  if (includePreflightHeaders) {
    headers["Access-Control-Allow-Methods"] =
      "GET, POST, PUT, PATCH, DELETE, OPTIONS";

    // Echo back requested headers (trust the browser to know what it needs).
    // The gateway performs actual header validation on the real request.
    headers["Access-Control-Allow-Headers"] =
      requestedHeaders || "Authorization, Content-Type";

    // Cache preflight for 24 hours
    headers["Access-Control-Max-Age"] = "86400";
  }

  return headers;
}

/**
 * Handle an OPTIONS preflight request.
 */
export function handlePreflight(
  request: Request,
  env: DispatchEnv,
): Response | null {
  // Only handle OPTIONS requests
  if (request.method !== "OPTIONS") return null;

  const origin = request.headers.get("Origin");

  // OPTIONS without Origin = non-CORS request (e.g., curl, health checks, monitoring)
  // Return 204 without CORS headers (standard for non-CORS OPTIONS)
  if (!origin) {
    // Non-CORS OPTIONS request (curl, health checks, monitoring)
    return new Response(null, { status: 204 });
  }

  // Check if origin is allowed
  const requestedHeaders = request.headers.get(
    "Access-Control-Request-Headers",
  );
  const headers = corsHeaders(origin, env, true, requestedHeaders);

  if (Object.keys(headers).length === 0) {
    // Origin not allowed — return 403 WITHOUT CORS headers.
    // This ensures the browser blocks the response (correct security behavior).
    return new Response(null, { status: 403 });
  }

  return new Response(null, { status: 204, headers });
}

// ---------------------------------------------------------------------------
// Auth decision
// ---------------------------------------------------------------------------

export interface AuthSuccess {
  readonly clawId: string;
}

/**
 * Apply the auth decision matrix for an external (path-based) request.
 *
 * Resolves org+claw slugs to clawId, then decides whether the request
 * should be proxied or rejected based on auth credentials.
 */
export const authenticate = (
  request: Request,
  parsed: ParsedPath,
  env: DispatchEnv,
): Effect.Effect<AuthSuccess, AuthError> =>
  Effect.gen(function* () {
    // Resolve clawId from slugs (uses bootstrap.resolveClawId)
    const { clawId } = yield* resolveClawId(
      parsed.orgSlug,
      parsed.clawSlug,
      env,
    );

    // Webhook paths: pass through without auth
    if (parsed.remainder.startsWith("/webhook/")) {
      return { clawId };
    }

    // WebSocket upgrade: session cookie OR Bearer token (proxy may convert cookie → Bearer)
    if (request.headers.get("Upgrade")?.toLowerCase() === "websocket") {
      const sessionId = extractSessionCookie(request);
      if (sessionId) {
        yield* validateSession(sessionId, parsed.orgSlug, parsed.clawSlug, env);
        return { clawId };
      }
      // Fall through to Bearer — the main app proxy forwards session as Authorization header
      const authHeader = request.headers.get("Authorization");
      if (authHeader?.startsWith("Bearer ")) {
        return { clawId };
      }
      return yield* new UnauthenticatedError({
        message: "WebSocket upgrade requires session authentication",
      });
    }

    // Bearer token: pass through (gateway validates)
    const authHeader = request.headers.get("Authorization");
    if (authHeader?.startsWith("Bearer ")) {
      return { clawId };
    }

    // Session cookie: validate via Cloud API
    const sessionId = extractSessionCookie(request);
    if (sessionId) {
      const session = yield* validateSession(
        sessionId,
        parsed.orgSlug,
        parsed.clawSlug,
        env,
      );
      return { clawId: session.clawId };
    }

    // No auth: reject
    return yield* new UnauthenticatedError({
      message: "Authentication required",
    });
  });

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function extractSessionCookie(request: Request): string | null {
  const cookies = request.headers.get("Cookie") || "";
  const match = cookies.match(/(?:^|;\s*)session=([^;]+)/);
  return match ? match[1] : null;
}

/** Clear the session cache (for testing). */
export function clearSessionCache(): void {
  sessionCache.clear();
}
