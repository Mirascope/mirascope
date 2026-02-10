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

import type { DispatchEnv } from "./types";

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
  // Match /{orgSlug}/{clawSlug} with optional remainder
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
export async function validateSession(
  sessionId: string,
  orgSlug: string,
  clawSlug: string,
  env: DispatchEnv,
): Promise<CachedSession | null> {
  const cacheKey = getSessionCacheKey(sessionId, orgSlug, clawSlug);
  const cached = sessionCache.get(cacheKey);
  if (cached && cached.expiresAt > Date.now()) {
    return cached;
  }

  const response = await env.MIRASCOPE_CLOUD.fetch(
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
  );

  if (!response.ok) {
    sessionCache.delete(cacheKey);
    return null;
  }

  const data = (await response.json()) as {
    userId: string;
    clawId: string;
    organizationId: string;
    role: string;
  };

  const entry: CachedSession = {
    ...data,
    expiresAt: Date.now() + SESSION_CACHE_TTL_MS,
  };
  sessionCache.set(cacheKey, entry);
  return entry;
}

// ---------------------------------------------------------------------------
// CORS helpers
// ---------------------------------------------------------------------------

const ALLOWED_ORIGIN = "https://mirascope.com";

export function corsHeaders(origin: string | null): Record<string, string> {
  if (origin !== ALLOWED_ORIGIN) return {};
  return {
    "Access-Control-Allow-Origin": ALLOWED_ORIGIN,
    "Access-Control-Allow-Credentials": "true",
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Authorization, Content-Type",
  };
}

/**
 * Handle an OPTIONS preflight request.
 */
export function handlePreflight(request: Request): Response | null {
  const origin = request.headers.get("Origin");
  if (request.method !== "OPTIONS" || !origin) return null;

  const headers = corsHeaders(origin);
  if (Object.keys(headers).length === 0) {
    return new Response(null, { status: 403 });
  }

  return new Response(null, { status: 204, headers });
}

// ---------------------------------------------------------------------------
// Auth decision
// ---------------------------------------------------------------------------

export type AuthResult =
  | { action: "pass-through"; clawId: string }
  | { action: "reject"; status: number; message: string };

/**
 * Apply the auth decision matrix for an external (path-based) request.
 *
 * Assumes the path has already been parsed and orgSlug+clawSlug resolved to clawId.
 * This function decides whether the request should be proxied or rejected.
 */
export async function authenticate(
  request: Request,
  parsed: ParsedPath,
  env: DispatchEnv,
): Promise<AuthResult> {
  // Resolve clawId from slugs
  let clawId: string;
  try {
    const resolved = await resolveClawIdFromSlugs(
      parsed.orgSlug,
      parsed.clawSlug,
      env,
    );
    clawId = resolved.clawId;
  } catch {
    return { action: "reject", status: 404, message: "Claw not found" };
  }

  // Webhook paths: pass through without auth
  if (parsed.remainder.startsWith("/webhook/")) {
    return { action: "pass-through", clawId };
  }

  // Bearer token: pass through (gateway validates)
  const authHeader = request.headers.get("Authorization");
  if (authHeader?.startsWith("Bearer ")) {
    return { action: "pass-through", clawId };
  }

  // Session cookie: validate via Cloud API
  const sessionId = extractSessionCookie(request);
  if (sessionId) {
    const session = await validateSession(
      sessionId,
      parsed.orgSlug,
      parsed.clawSlug,
      env,
    );
    if (session) {
      return { action: "pass-through", clawId: session.clawId };
    }
    return { action: "reject", status: 401, message: "Invalid session" };
  }

  // No auth: reject
  return { action: "reject", status: 401, message: "Authentication required" };
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function extractSessionCookie(request: Request): string | null {
  const cookies = request.headers.get("Cookie") || "";
  const match = cookies.match(/(?:^|;\s*)session=([^;]+)/);
  return match ? match[1] : null;
}

async function resolveClawIdFromSlugs(
  orgSlug: string,
  clawSlug: string,
  env: DispatchEnv,
): Promise<{ clawId: string; organizationId: string }> {
  const response = await env.MIRASCOPE_CLOUD.fetch(
    `https://internal/api/internal/claws/resolve/${orgSlug}/${clawSlug}`,
    {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    },
  );

  if (!response.ok) {
    throw new Error(`Resolution failed: ${response.status}`);
  }

  return (await response.json()) as { clawId: string; organizationId: string };
}

/** Clear the session cache (for testing). */
export function clearSessionCache(): void {
  sessionCache.clear();
}
