/**
 * Bearer token authentication middleware.
 */
import type { Context, Next } from "hono";

export function authMiddleware(expectedToken: string) {
  return async (c: Context, next: Next) => {
    const authHeader = c.req.header("Authorization");

    if (!authHeader) {
      return c.json({ error: "Missing Authorization header" }, 401);
    }

    const [scheme, token] = authHeader.split(" ", 2);
    if (scheme !== "Bearer" || !token) {
      return c.json(
        { error: "Invalid Authorization format. Expected: Bearer <token>" },
        401,
      );
    }

    // Constant-time comparison to prevent timing attacks
    if (!timingSafeEqual(token, expectedToken)) {
      return c.json({ error: "Invalid token" }, 403);
    }

    await next();
  };
}

function timingSafeEqual(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  const encoder = new TextEncoder();
  const bufA = encoder.encode(a);
  const bufB = encoder.encode(b);
  let result = 0;
  for (let i = 0; i < bufA.length; i++) {
    result |= bufA[i]! ^ bufB[i]!;
  }
  return result === 0;
}
