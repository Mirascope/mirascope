/**
 * Mirascope ops module for tracing, versioning, and observability.
 */

// Configuration
export { configure, tracerContext } from "@/ops/_internal/configuration";
export type { ConfigureOptions } from "@/ops/_internal/configuration";

// Exceptions
export { ClosureComputationError } from "@/ops/exceptions";

// Types
export type {
  Jsonable,
  TraceOptions,
  VersionOptions,
  PropagatorFormat,
} from "@/ops/_internal/types";

// Sessions
export {
  SESSION_HEADER_NAME,
  session,
  currentSession,
  extractSessionId,
} from "@/ops/_internal/session";
export type { SessionContext } from "@/ops/_internal/session";

// Spans
export { Span, span } from "@/ops/_internal/spans";

// Context Propagation
export {
  ContextPropagator,
  getPropagator,
  resetPropagator,
  extractContext,
  injectContext,
  propagatedContext,
} from "@/ops/_internal/propagation";
