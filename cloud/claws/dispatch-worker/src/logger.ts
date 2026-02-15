/**
 * Structured logging for the dispatch worker.
 *
 * Provides per-request loggers with:
 * - Claw ID prefix (first 8 chars) for request correlation
 * - Consistent stage tags: req, auth, config, gateway, r2, http, ws
 * - Debug level gated by the DEBUG env var
 * - Token/secret redaction utility
 */

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

/** Log stage tags used across the dispatch worker. */
export type LogTag =
  | "req"
  | "auth"
  | "config"
  | "gateway"
  | "r2"
  | "http"
  | "ws"
  | "internal"
  | "cors"
  | "terminal";

export interface Logger {
  /** Always logged. Use for request lifecycle events, errors, state changes. */
  info(tag: LogTag, msg: string, ...args: unknown[]): void;
  /** Always logged. Use for errors and failures. */
  error(tag: LogTag, msg: string, ...args: unknown[]): void;
  /** Only logged when debug=true. Use for payloads, detailed state, timing. */
  debug(tag: LogTag, msg: string, ...args: unknown[]): void;
}

// ---------------------------------------------------------------------------
// Factory
// ---------------------------------------------------------------------------

export interface LoggerOptions {
  clawId?: string;
  debug?: boolean;
}

/**
 * Create a logger scoped to a specific request/claw.
 *
 * The clawId prefix lets you grep CF logs for a specific claw's activity
 * even when multiple claws are being served concurrently.
 */
export function createLogger(opts: LoggerOptions = {}): Logger {
  const prefix = opts.clawId ? `[${opts.clawId.slice(0, 8)}]` : "[------]";
  const isDebug = opts.debug ?? false;

  return {
    info(tag, msg, ...args) {
      console.log(`${prefix} [${tag}] ${msg}`, ...args);
    },
    error(tag, msg, ...args) {
      console.error(`${prefix} [${tag}] ${msg}`, ...args);
    },
    debug(tag, msg, ...args) {
      if (isDebug) {
        console.log(`${prefix} [${tag}:debug] ${msg}`, ...args);
      }
    },
  };
}

// ---------------------------------------------------------------------------
// Redaction
// ---------------------------------------------------------------------------

/**
 * Redact sensitive query parameters from a URL for logging.
 * Replaces the value of `token` params with `***`.
 */
export function redactUrl(url: URL): string {
  if (!url.searchParams.has("token")) return url.toString();
  const redacted = new URL(url.toString());
  redacted.searchParams.set("token", "***");
  return redacted.toString();
}

/**
 * Summarize env var keys for logging (never log values).
 */
export function summarizeEnvKeys(env: Record<string, string>): string {
  const keys = Object.keys(env);
  return `${keys.length} keys: [${keys.join(", ")}]`;
}
