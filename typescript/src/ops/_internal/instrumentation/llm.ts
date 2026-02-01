/**
 * LLM instrumentation entry point.
 *
 * Provides functions to instrument/uninstrument LLM calls with OpenTelemetry tracing.
 */

import { getTracer } from "@/ops/_internal/configuration";
import {
  wrapAllModelMethods,
  unwrapAllModelMethods,
  isModelInstrumented,
} from "@/ops/_internal/instrumentation/model";

let _instrumented = false;

/**
 * Instrument LLM calls with OpenTelemetry tracing.
 *
 * This function wraps all Model class methods to automatically create
 * GenAI semantic convention spans for each LLM call.
 *
 * Must call `configure()` before calling this function to set up the tracer.
 *
 * @throws Error if configure() has not been called
 *
 * @example
 * ```typescript
 * import { ops } from 'mirascope';
 *
 * // Configure tracing first
 * ops.configure({ apiKey: process.env.MIRASCOPE_API_KEY });
 *
 * // Enable LLM instrumentation
 * ops.instrumentLlm();
 *
 * // Now all Model calls are automatically traced
 * const model = new Model('anthropic/claude-sonnet-4-20250514');
 * const response = await model.call('Hello!');
 * // ^ Creates a span with GenAI semantic conventions
 * ```
 */
export function instrumentLlm(): void {
  if (_instrumented) {
    return;
  }

  const tracer = getTracer();
  if (!tracer) {
    throw new Error(
      "You must call configure() before calling instrumentLlm(). " +
        "The tracer has not been initialized.",
    );
  }

  wrapAllModelMethods();
  _instrumented = true;
}

/**
 * Remove LLM instrumentation.
 *
 * Restores all Model methods to their original implementations.
 *
 * @example
 * ```typescript
 * import { ops } from 'mirascope';
 *
 * // Disable instrumentation
 * ops.uninstrumentLlm();
 *
 * // Model calls are no longer traced
 * const response = await model.call('Hello!');
 * ```
 */
export function uninstrumentLlm(): void {
  if (!_instrumented) {
    return;
  }

  unwrapAllModelMethods();
  _instrumented = false;
}

/**
 * Check if LLM instrumentation is currently enabled.
 *
 * @returns true if instrumentLlm() has been called and not yet uninstrumented
 *
 * @example
 * ```typescript
 * import { ops } from 'mirascope';
 *
 * console.log(ops.isLlmInstrumented()); // false
 *
 * ops.configure();
 * ops.instrumentLlm();
 *
 * console.log(ops.isLlmInstrumented()); // true
 *
 * ops.uninstrumentLlm();
 *
 * console.log(ops.isLlmInstrumented()); // false
 * ```
 */
export function isLlmInstrumented(): boolean {
  return _instrumented && isModelInstrumented();
}

/**
 * Reset instrumentation state.
 *
 * This is primarily for testing to ensure clean state between tests.
 */
export function resetInstrumentationState(): void {
  _instrumented = false;
}
