/**
 * OpenTelemetry instrumentation for OpenAI SDK.
 *
 * Uses the official @opentelemetry/instrumentation-openai package.
 */

import type { TracerProvider } from "@opentelemetry/api";

import {
  BaseInstrumentation,
  type ContentCaptureMode,
  type Instrumentor,
} from "@/ops/_internal/instrumentation/providers/base";

// Lazy import to avoid requiring the package if not used
let OpenAIInstrumentationClass: (new () => Instrumentor) | null = null;

/* v8 ignore start - requires optional dependency */
async function getOpenAIInstrumentationClass(): Promise<
  new () => Instrumentor
> {
  if (OpenAIInstrumentationClass) {
    return OpenAIInstrumentationClass;
  }

  try {
    // Dynamic import of optional dependency - uses type declaration from types.d.ts
    const { OpenAIInstrumentation } =
      await import("@opentelemetry/instrumentation-openai");
    OpenAIInstrumentationClass =
      OpenAIInstrumentation as new () => Instrumentor;
    return OpenAIInstrumentationClass;
  } catch {
    throw new Error(
      "Failed to import @opentelemetry/instrumentation-openai. " +
        "Please install it: npm install @opentelemetry/instrumentation-openai",
    );
  }
}
/* v8 ignore end */

// Singleton state
let openaiInstance: OpenAIInstrumentationManager | null = null;
let openaiInstrumentorClass: (new () => Instrumentor) | null = null;

/**
 * Manages OpenTelemetry instrumentation lifecycle for the OpenAI SDK.
 */
class OpenAIInstrumentationManager extends BaseInstrumentation<Instrumentor> {
  static instance(): OpenAIInstrumentationManager {
    if (!openaiInstance) {
      openaiInstance = new OpenAIInstrumentationManager();
    }
    return openaiInstance;
  }

  protected createInstrumentor(): Instrumentor {
    if (!openaiInstrumentorClass) {
      throw new Error(
        "Instrumentor class not loaded. Call instrumentOpenai() instead of using the class directly.",
      );
    }
    return new openaiInstrumentorClass();
  }

  protected configureContentCapture(captureContent: ContentCaptureMode): void {
    if (captureContent === "enabled") {
      this.setEnvVar(
        "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT",
        "true",
      );
    } else if (captureContent === "disabled") {
      this.setEnvVar(
        "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT",
        "false",
      );
    }
  }

  static resetForTesting(): void {
    if (openaiInstance) {
      openaiInstance.uninstrument();
    }
    openaiInstance = null;
    openaiInstrumentorClass = null;
  }
}

/**
 * Enable OpenTelemetry instrumentation for the OpenAI SDK.
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
 * // Enable OpenAI instrumentation
 * await ops.instrumentOpenai();
 *
 * // With content capture enabled
 * await ops.instrumentOpenai({ captureContent: "enabled" });
 * ```
 */
/* v8 ignore start - requires optional dependency */
export async function instrumentOpenai(
  options: {
    tracerProvider?: TracerProvider;
    captureContent?: ContentCaptureMode;
  } = {},
): Promise<void> {
  openaiInstrumentorClass = await getOpenAIInstrumentationClass();
  const manager = OpenAIInstrumentationManager.instance();
  manager.instrument(options);
}
/* v8 ignore end */

/**
 * Disable previously configured OpenAI instrumentation.
 */
export function uninstrumentOpenai(): void {
  OpenAIInstrumentationManager.instance().uninstrument();
}

/**
 * Return whether OpenAI instrumentation is currently active.
 */
export function isOpenaiInstrumented(): boolean {
  return OpenAIInstrumentationManager.instance().isInstrumented;
}

/**
 * Reset OpenAI instrumentation for testing.
 */
export function resetOpenaiInstrumentationForTesting(): void {
  OpenAIInstrumentationManager.resetForTesting();
}
