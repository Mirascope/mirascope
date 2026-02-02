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

// Tracing (unified API - handles both functions and calls)
export { trace } from "@/ops/_internal/tracing";
export type {
  TracedFunction,
  TracedCall,
  CallLike,
} from "@/ops/_internal/tracing";

/**
 * @deprecated Use `trace()` instead, which now handles both functions and calls.
 * @example
 * // Old usage:
 * const tracedCall = traceCall(myCall, options);
 * // New unified usage:
 * const tracedCall = trace(myCall, options);
 */
export { traceCall } from "@/ops/_internal/traced-calls";

// Trace Result
export { createTrace } from "@/ops/_internal/traced-functions";
export type { Trace, AnnotateOptions } from "@/ops/_internal/traced-functions";

// Versioning (unified API - handles both functions and calls)
export { version } from "@/ops/_internal/versioning";
export type {
  VersionedFunction,
  VersionedCall,
} from "@/ops/_internal/versioning";
export type {
  ClosureMetadata,
  VersionInfo,
  VersionedResult,
} from "@/ops/_internal/versioned-functions";

/**
 * @deprecated Use `version()` instead, which now handles both functions and calls.
 * @example
 * // Old usage:
 * const versionedCall = versionCall(myCall, options);
 * // New unified usage:
 * const versionedCall = version(myCall, options);
 */
export { versionCall } from "@/ops/_internal/versioned-calls";

// Exporters
export { MirascopeOTLPExporter } from "@/ops/_internal/exporters";

// LLM Instrumentation (Mirascope Model class)
export {
  instrumentLlm,
  uninstrumentLlm,
  isLlmInstrumented,
} from "@/ops/_internal/instrumentation";

// Provider SDK Instrumentation
export type { ContentCaptureMode } from "@/ops/_internal/instrumentation";

// OpenAI SDK Instrumentation
export {
  instrumentOpenai,
  uninstrumentOpenai,
  isOpenaiInstrumented,
} from "@/ops/_internal/instrumentation";

// Anthropic SDK Instrumentation
export {
  instrumentAnthropic,
  uninstrumentAnthropic,
  isAnthropicInstrumented,
} from "@/ops/_internal/instrumentation";

// Google GenAI SDK Instrumentation
export {
  instrumentGoogleGenai,
  uninstrumentGoogleGenai,
  isGoogleGenaiInstrumented,
} from "@/ops/_internal/instrumentation";
