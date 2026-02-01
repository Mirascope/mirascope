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

// Tracing
export { trace } from "@/ops/_internal/tracing";
export type { TracedFunction } from "@/ops/_internal/tracing";

// Traced Calls
export { traceCall } from "@/ops/_internal/traced-calls";
export type { TracedCall } from "@/ops/_internal/traced-calls";

// Trace Result
export { createTrace } from "@/ops/_internal/traced-functions";
export type { Trace, AnnotateOptions } from "@/ops/_internal/traced-functions";

// Exporters
export { MirascopeOTLPExporter } from "@/ops/_internal/exporters";

// LLM Instrumentation
export {
  instrumentLlm,
  uninstrumentLlm,
  isLlmInstrumented,
} from "@/ops/_internal/instrumentation";
