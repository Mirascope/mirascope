/**
 * Session context helpers for grouping traces.
 */

import { randomUUID } from "node:crypto";

import type { Jsonable } from "@/ops/_internal/types";

import {
  getCurrentContext,
  opsContextStorage,
} from "@/ops/_internal/async-context";

/**
 * HTTP header name for session ID propagation.
 */
export const SESSION_HEADER_NAME = "Mirascope-Session-Id";

/**
 * Represents a session context for grouping related spans.
 */
export interface SessionContext {
  /** Unique identifier for the session. */
  readonly id: string;
  /** Optional JSON-serializable metadata associated with the session. */
  readonly attributes?: Record<string, Jsonable>;
}

/**
 * Options for creating a session.
 */
export interface SessionOptions {
  /** Unique identifier for the session. If not provided, a UUID will be generated. */
  id?: string;
  /** Optional dictionary of JSON-serializable attributes to attach to the session. */
  attributes?: Record<string, Jsonable>;
}

/**
 * Run a function within a session context.
 *
 * Sessions are used to group related traces together. The session ID and
 * optional attributes are automatically propagated to all spans created
 * within the session context and are included in outgoing HTTP requests.
 *
 * @param options - Session configuration options.
 * @param fn - Function to execute within the session context.
 * @returns The result of the function.
 *
 * @example
 * ```typescript
 * // With explicit ID
 * const result = await session({ id: "user-123" }, async () => {
 *   console.log(currentSession()?.id); // "user-123"
 *   return await fetchData();
 * });
 *
 * // With auto-generated ID
 * await session({}, async () => {
 *   console.log(currentSession()?.id); // Auto-generated UUID
 * });
 *
 * // Nested sessions override parent session
 * await session({ id: "1" }, async () => {
 *   // Session ID: 1
 *   await session({ id: "2" }, async () => {
 *     // Session ID: 2
 *   });
 *   // Session ID: 1
 * });
 * ```
 */
export async function session<T>(
  options: SessionOptions,
  fn: () => T | Promise<T>,
): Promise<T> {
  const sessionCtx: SessionContext = {
    id: options.id ?? randomUUID(),
    attributes: options.attributes,
  };

  const currentContext = getCurrentContext() ?? {};
  const newContext = {
    ...currentContext,
    sessionId: sessionCtx.id,
    sessionAttributes: sessionCtx.attributes,
  };

  return opsContextStorage.run(newContext, () => fn());
}

/**
 * Get the current session context if one is active.
 *
 * @returns The active SessionContext or null if no session is active.
 *
 * @example
 * ```typescript
 * await session({ id: "user-123" }, async () => {
 *   const ctx = currentSession();
 *   console.log(ctx?.id); // "user-123"
 * });
 *
 * const ctx = currentSession();
 * console.log(ctx); // null
 * ```
 */
export function currentSession(): SessionContext | null {
  const ctx = getCurrentContext();
  if (!ctx?.sessionId) return null;
  return {
    id: ctx.sessionId,
    attributes: ctx.sessionAttributes,
  };
}

/**
 * Extract session ID from carrier headers.
 *
 * Performs case-insensitive header name matching and handles both string
 * and array header values.
 *
 * @param headers - Dictionary of HTTP headers or similar carrier data.
 * @returns The extracted session ID or null if not present.
 *
 * @example
 * ```typescript
 * const headers = { "mirascope-session-id": "session-123" };
 * const sessionId = extractSessionId(headers);
 * console.log(sessionId); // "session-123"
 * ```
 */
export function extractSessionId(
  headers: Record<string, string | string[] | undefined>,
): string | null {
  const normalizedHeaders: Record<string, string | string[] | undefined> = {};
  for (const [key, value] of Object.entries(headers)) {
    normalizedHeaders[key.toLowerCase()] = value;
  }

  const headerNameLower = SESSION_HEADER_NAME.toLowerCase();

  if (!(headerNameLower in normalizedHeaders)) {
    return null;
  }

  const value = normalizedHeaders[headerNameLower];

  if (Array.isArray(value)) {
    if (value.length > 0) {
      return value[0] ?? null;
    }
    return null;
  }

  return value ?? null;
}
