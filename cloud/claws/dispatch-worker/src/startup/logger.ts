/**
 * Structured logging for the startup script.
 * All log lines are prefixed with [start-openclaw] and timestamped.
 */

export function log(msg: string, data?: Record<string, unknown>): void {
  const ts = new Date().toISOString();
  if (data) {
    console.log(`[start-openclaw ${ts}] ${msg}`, JSON.stringify(data));
  } else {
    console.log(`[start-openclaw ${ts}] ${msg}`);
  }
}

export function logError(msg: string, err: unknown): void {
  const ts = new Date().toISOString();
  const errMsg =
    err instanceof Error
      ? { message: err.message, stack: err.stack }
      : { raw: String(err) };
  console.error(`[start-openclaw ${ts}] ERROR: ${msg}`, JSON.stringify(errMsg));
}
