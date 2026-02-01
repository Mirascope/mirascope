/**
 * OpenTelemetry instrumentation for Anthropic SDK.
 *
 * Uses the @traceloop/instrumentation-anthropic package.
 */

import type { TracerProvider } from "@opentelemetry/api";

import {
  BaseInstrumentation,
  type ContentCaptureMode,
  type Instrumentor,
} from "@/ops/_internal/instrumentation/providers/base";

// Lazy import to avoid requiring the package if not used
let AnthropicInstrumentationClass: (new () => Instrumentor) | null = null;

/* v8 ignore start - requires optional dependency */
async function getAnthropicInstrumentationClass(): Promise<
  new () => Instrumentor
> {
  if (AnthropicInstrumentationClass) {
    return AnthropicInstrumentationClass;
  }

  try {
    // Dynamic import of optional dependency - uses type declaration from types.d.ts
    const { AnthropicInstrumentation } =
      await import("@traceloop/instrumentation-anthropic");
    AnthropicInstrumentationClass =
      AnthropicInstrumentation as new () => Instrumentor;
    return AnthropicInstrumentationClass;
  } catch {
    throw new Error(
      "Failed to import @traceloop/instrumentation-anthropic. " +
        "Please install it: npm install @traceloop/instrumentation-anthropic",
    );
  }
}
/* v8 ignore end */

// Singleton state
let anthropicInstance: AnthropicInstrumentationManager | null = null;
let anthropicInstrumentorClass: (new () => Instrumentor) | null = null;

/**
 * Manages OpenTelemetry instrumentation lifecycle for the Anthropic SDK.
 */
class AnthropicInstrumentationManager extends BaseInstrumentation<Instrumentor> {
  static instance(): AnthropicInstrumentationManager {
    if (!anthropicInstance) {
      anthropicInstance = new AnthropicInstrumentationManager();
    }
    return anthropicInstance;
  }

  protected createInstrumentor(): Instrumentor {
    if (!anthropicInstrumentorClass) {
      throw new Error(
        "Instrumentor class not loaded. Call instrumentAnthropic() instead of using the class directly.",
      );
    }
    return new anthropicInstrumentorClass();
  }

  protected configureContentCapture(captureContent: ContentCaptureMode): void {
    // Anthropic/Traceloop uses TRACELOOP_TRACE_CONTENT
    if (captureContent === "enabled") {
      this.setEnvVar("TRACELOOP_TRACE_CONTENT", "true");
    } else if (captureContent === "disabled") {
      this.setEnvVar("TRACELOOP_TRACE_CONTENT", "false");
    }
  }

  static resetForTesting(): void {
    if (anthropicInstance) {
      anthropicInstance.uninstrument();
    }
    anthropicInstance = null;
    anthropicInstrumentorClass = null;
  }
}

/**
 * Enable OpenTelemetry instrumentation for the Anthropic SDK.
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
 * // Enable Anthropic instrumentation
 * await ops.instrumentAnthropic();
 *
 * // With content capture enabled
 * await ops.instrumentAnthropic({ captureContent: "enabled" });
 * ```
 */
/* v8 ignore start - requires optional dependency */
export async function instrumentAnthropic(
  options: {
    tracerProvider?: TracerProvider;
    captureContent?: ContentCaptureMode;
  } = {},
): Promise<void> {
  anthropicInstrumentorClass = await getAnthropicInstrumentationClass();
  const manager = AnthropicInstrumentationManager.instance();
  manager.instrument(options);
}
/* v8 ignore end */

/**
 * Disable previously configured Anthropic instrumentation.
 */
export function uninstrumentAnthropic(): void {
  AnthropicInstrumentationManager.instance().uninstrument();
}

/**
 * Return whether Anthropic instrumentation is currently active.
 */
export function isAnthropicInstrumented(): boolean {
  return AnthropicInstrumentationManager.instance().isInstrumented;
}

/**
 * Reset Anthropic instrumentation for testing.
 */
export function resetAnthropicInstrumentationForTesting(): void {
  AnthropicInstrumentationManager.resetForTesting();
}
