/**
 * Provider SDK instrumentation module.
 *
 * Provides OpenTelemetry instrumentation for native provider SDKs
 * (OpenAI, Anthropic, Google GenAI) using official OTel packages.
 */

// Base types
export {
  type ContentCaptureMode,
  type Instrumentor,
  BaseInstrumentation,
  OTEL_SEMCONV_STABILITY_OPT_IN,
  OTEL_SEMCONV_STABILITY_VALUE,
} from "@/ops/_internal/instrumentation/providers/base";

// OpenAI
export {
  instrumentOpenai,
  uninstrumentOpenai,
  isOpenaiInstrumented,
  resetOpenaiInstrumentationForTesting,
} from "@/ops/_internal/instrumentation/providers/openai";

// Anthropic
export {
  instrumentAnthropic,
  uninstrumentAnthropic,
  isAnthropicInstrumented,
  resetAnthropicInstrumentationForTesting,
} from "@/ops/_internal/instrumentation/providers/anthropic";

// Google GenAI
export {
  instrumentGoogleGenai,
  uninstrumentGoogleGenai,
  isGoogleGenaiInstrumented,
  resetGoogleGenaiInstrumentationForTesting,
} from "@/ops/_internal/instrumentation/providers/google-genai";
