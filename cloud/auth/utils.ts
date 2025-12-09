import { Effect } from "effect";
import { DatabaseService } from "@/db";
import type { PublicUser } from "@/db/schema";

function isSecure(): boolean {
  return (
    process.env.ENVIRONMENT === "production" ||
    (process.env.SITE_URL?.startsWith("https://") ?? false)
  );
}

function getCookieValue(request: Request, name: string): string | null {
  const cookieHeader = request.headers.get("Cookie");
  if (!cookieHeader) return null;

  const cookies = cookieHeader.split(";");
  for (const cookie of cookies) {
    const [cookieName, value] = cookie.trim().split("=");
    if (cookieName === name) {
      return value || null;
    }
  }
  return null;
}

export function getSessionIdFromCookie(request: Request): string | null {
  return getCookieValue(request, "session");
}

export function getOAuthStateFromCookie(request: Request): string | null {
  return getCookieValue(request, "oauth_state");
}

export function setSessionCookie(sessionId: string): string {
  const maxAge = 7 * 24 * 60 * 60; // 7 days in seconds

  const cookieParts = [
    `session=${sessionId}`,
    "HttpOnly",
    ...(isSecure() ? ["Secure"] : []),
    "SameSite=Lax",
    `Max-Age=${maxAge}`,
    "Path=/",
  ];

  return cookieParts.join("; ");
}

export function clearSessionCookie(): string {
  const cookieParts = [
    "session=;",
    "Expires=Thu, 01 Jan 1970 00:00:00 GMT",
    "HttpOnly",
    ...(isSecure() ? ["Secure"] : []),
    "SameSite=Lax",
    "Path=/",
  ];

  return cookieParts.join("; ");
}

export function setOAuthStateCookie(state: string): string {
  const cookieParts = [
    `oauth_state=${state}`,
    "HttpOnly",
    ...(isSecure() ? ["Secure"] : []),
    "SameSite=Lax",
    "Max-Age=600", // 10 minutes
    "Path=/",
  ];

  return cookieParts.join("; ");
}

export function clearOAuthStateCookie(): string {
  const cookieParts = [
    "oauth_state=;",
    "Expires=Thu, 01 Jan 1970 00:00:00 GMT",
    "HttpOnly",
    ...(isSecure() ? ["Secure"] : []),
    "SameSite=Lax",
    "Path=/",
  ];

  return cookieParts.join("; ");
}

export const getAuthenticatedUser = (
  request: Request,
): Effect.Effect<PublicUser | null, never, DatabaseService> =>
  Effect.gen(function* () {
    const sessionId = getSessionIdFromCookie(request);
    if (!sessionId) {
      return null;
    }

    const db = yield* DatabaseService;
    return yield* db.sessions
      .findUserBySessionId(sessionId)
      .pipe(Effect.catchAll(() => Effect.succeed(null)));
  });
