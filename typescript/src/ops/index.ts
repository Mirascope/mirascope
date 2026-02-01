/**
 * Mirascope ops module for tracing, versioning, and observability.
 */

// Configuration
export { configure, tracerContext } from "@/ops/_internal/configuration";
export type { ConfigureOptions } from "@/ops/_internal/configuration";

// Exceptions
export { ClosureComputationError } from "@/ops/exceptions";

// Sessions
export {
  SESSION_HEADER_NAME,
  session,
  currentSession,
  extractSessionId,
} from "@/ops/_internal/session";
export type { SessionContext } from "@/ops/_internal/session";
