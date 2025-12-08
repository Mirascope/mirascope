/**
 * Check if secure cookies should be used based on environment
 */
function isSecure(): boolean {
  return (
    process.env.ENVIRONMENT === "production" ||
    (process.env.SITE_URL?.startsWith("https://") ?? false)
  );
}

/**
 * Extract a cookie value from a request by name
 */
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

/**
 * Extract session ID from request cookie
 */
export function getSessionIdFromCookie(request: Request): string | null {
  return getCookieValue(request, "session");
}

/**
 * Extract OAuth state from request cookie
 */
export function getOAuthStateFromCookie(request: Request): string | null {
  return getCookieValue(request, "oauth_state");
}

/**
 * Generate cookie header value for setting a session
 */
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

/**
 * Generate cookie header value for clearing a session
 */
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

/**
 * Generate cookie header value for OAuth state
 */
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

/**
 * Generate cookie header value for clearing OAuth state
 */
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
