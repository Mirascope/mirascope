/**
 * OpenTelemetry instrumentation for Google GenAI SDK.
 *
 * Uses the @traceloop/instrumentation-google-generativeai package.
 */

import type { TracerProvider } from "@opentelemetry/api";

import {
  BaseInstrumentation,
  type ContentCaptureMode,
  type Instrumentor,
} from "@/ops/_internal/instrumentation/providers/base";

// Lazy import to avoid requiring the package if not used
let GoogleGenAIInstrumentationClass: (new () => Instrumentor) | null = null;

/* v8 ignore start - requires optional dependency */
async function getGoogleGenAIInstrumentationClass(): Promise<
  new () => Instrumentor
> {
  if (GoogleGenAIInstrumentationClass) {
    return GoogleGenAIInstrumentationClass;
  }

  try {
    // Dynamic import of optional dependency - uses type declaration from types.d.ts
    const { GoogleGenerativeAIInstrumentation } =
      await import("@traceloop/instrumentation-google-generativeai");
    GoogleGenAIInstrumentationClass =
      GoogleGenerativeAIInstrumentation as new () => Instrumentor;
    return GoogleGenAIInstrumentationClass;
  } catch {
    throw new Error(
      "Failed to import @traceloop/instrumentation-google-generativeai. " +
        "Please install it: npm install @traceloop/instrumentation-google-generativeai",
    );
  }
}
/* v8 ignore end */

// Singleton state
let googleGenaiInstance: GoogleGenAIInstrumentationManager | null = null;
let googleGenaiInstrumentorClass: (new () => Instrumentor) | null = null;

/**
 * Manages OpenTelemetry instrumentation lifecycle for the Google GenAI SDK.
 */
class GoogleGenAIInstrumentationManager extends BaseInstrumentation<Instrumentor> {
  static instance(): GoogleGenAIInstrumentationManager {
    if (!googleGenaiInstance) {
      googleGenaiInstance = new GoogleGenAIInstrumentationManager();
    }
    return googleGenaiInstance;
  }

  protected createInstrumentor(): Instrumentor {
    if (!googleGenaiInstrumentorClass) {
      throw new Error(
        "Instrumentor class not loaded. Call instrumentGoogleGenai() instead of using the class directly.",
      );
    }
    return new googleGenaiInstrumentorClass();
  }

  protected configureContentCapture(captureContent: ContentCaptureMode): void {
    // Google GenAI uses ContentCapturingMode enum instead of true/false.
    // Valid values: NO_CONTENT, SPAN_ONLY, EVENT_ONLY, SPAN_AND_EVENT
    if (captureContent === "enabled") {
      this.setEnvVar(
        "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT",
        "SPAN_AND_EVENT",
      );
    } else if (captureContent === "disabled") {
      this.setEnvVar(
        "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT",
        "NO_CONTENT",
      );
    }
  }

  static resetForTesting(): void {
    if (googleGenaiInstance) {
      googleGenaiInstance.uninstrument();
    }
    googleGenaiInstance = null;
    googleGenaiInstrumentorClass = null;
  }
}

/**
 * Enable OpenTelemetry instrumentation for the Google GenAI SDK.
 *
 * Uses the provided tracerProvider or the global OpenTelemetry tracer provider.
 *
 * @param options - Configuration options
 * @param options.tracerProvider - Optional tracer provider to use
 * @param options.captureContent - Controls whether to capture message content in spans
 *
 * @example
 * ```typescript
 * import { ops } from '@mirascope/core';
 *
 * // Configure first
 * ops.configure();
 *
 * // Enable Google GenAI instrumentation
 * await ops.instrumentGoogleGenai();
 *
 * // With content capture enabled
 * await ops.instrumentGoogleGenai({ captureContent: "enabled" });
 * ```
 */
/* v8 ignore start - requires optional dependency */
export async function instrumentGoogleGenai(
  options: {
    tracerProvider?: TracerProvider;
    captureContent?: ContentCaptureMode;
  } = {},
): Promise<void> {
  googleGenaiInstrumentorClass = await getGoogleGenAIInstrumentationClass();
  const manager = GoogleGenAIInstrumentationManager.instance();
  manager.instrument(options);
}
/* v8 ignore end */

/**
 * Disable previously configured Google GenAI instrumentation.
 */
export function uninstrumentGoogleGenai(): void {
  GoogleGenAIInstrumentationManager.instance().uninstrument();
}

/**
 * Return whether Google GenAI instrumentation is currently active.
 */
export function isGoogleGenaiInstrumented(): boolean {
  return GoogleGenAIInstrumentationManager.instance().isInstrumented;
}

/**
 * Reset Google GenAI instrumentation for testing.
 */
export function resetGoogleGenaiInstrumentationForTesting(): void {
  GoogleGenAIInstrumentationManager.resetForTesting();
}
