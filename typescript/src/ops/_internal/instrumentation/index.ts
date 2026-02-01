/**
 * LLM instrumentation module.
 *
 * Provides OpenTelemetry GenAI semantic convention instrumentation
 * for the Mirascope LLM Model class and native provider SDKs.
 */

// Mirascope Model instrumentation
export {
  instrumentLlm,
  uninstrumentLlm,
  isLlmInstrumented,
  resetInstrumentationState,
} from "@/ops/_internal/instrumentation/llm";

// Provider SDK instrumentation
export {
  // Types
  type ContentCaptureMode,
  // OpenAI
  instrumentOpenai,
  uninstrumentOpenai,
  isOpenaiInstrumented,
  // Anthropic
  instrumentAnthropic,
  uninstrumentAnthropic,
  isAnthropicInstrumented,
  // Google GenAI
  instrumentGoogleGenai,
  uninstrumentGoogleGenai,
  isGoogleGenaiInstrumented,
} from "@/ops/_internal/instrumentation/providers";

// Common utilities (for advanced use cases)
export {
  GenAIAttributes,
  startModelSpan,
  attachResponse,
  recordException,
  recordDroppedParams,
  withSpanContext,
  type SpanContext,
  type StartModelSpanOptions,
} from "@/ops/_internal/instrumentation/common";

// Model wrappers (for advanced use cases)
export {
  wrapModelCall,
  unwrapModelCall,
  wrapModelStream,
  unwrapModelStream,
  wrapModelContextCall,
  unwrapModelContextCall,
  wrapModelContextStream,
  unwrapModelContextStream,
  wrapModelResume,
  unwrapModelResume,
  wrapModelResumeStream,
  unwrapModelResumeStream,
  wrapModelContextResume,
  unwrapModelContextResume,
  wrapModelContextResumeStream,
  unwrapModelContextResumeStream,
  wrapAllModelMethods,
  unwrapAllModelMethods,
  isModelInstrumented,
} from "@/ops/_internal/instrumentation/model";
