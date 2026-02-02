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
import {
  wrapAllResponseResumeMethods,
  unwrapAllResponseResumeMethods,
  isResponseResumeInstrumented,
} from "@/ops/_internal/instrumentation/response";

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
 * ops.instrumentLLM();
 *
 * // Now all Model calls are automatically traced
 * const model = new Model('anthropic/claude-sonnet-4-20250514');
 * const response = await model.call('Hello!');
 * // ^ Creates a span with GenAI semantic conventions
 * ```
 */
export function instrumentLLM(): void {
  if (_instrumented) {
    return;
  }

  const tracer = getTracer();
  if (!tracer) {
    throw new Error(
      "You must call configure() before calling instrumentLLM(). " +
        "The tracer has not been initialized.",
    );
  }

  wrapAllModelMethods();
  wrapAllResponseResumeMethods();
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
 * ops.uninstrumentLLM();
 *
 * // Model calls are no longer traced
 * const response = await model.call('Hello!');
 * ```
 */
export function uninstrumentLLM(): void {
  if (!_instrumented) {
    return;
  }

  unwrapAllModelMethods();
  unwrapAllResponseResumeMethods();
  _instrumented = false;
}

/**
 * Check if LLM instrumentation is currently enabled.
 *
 * @returns true if instrumentLLM() has been called and not yet uninstrumented
 *
 * @example
 * ```typescript
 * import { ops } from 'mirascope';
 *
 * console.log(ops.isLLMInstrumented()); // false
 *
 * ops.configure();
 * ops.instrumentLLM();
 *
 * console.log(ops.isLLMInstrumented()); // true
 *
 * ops.uninstrumentLLM();
 *
 * console.log(ops.isLLMInstrumented()); // false
 * ```
 */
export function isLLMInstrumented(): boolean {
  return (
    _instrumented && isModelInstrumented() && isResponseResumeInstrumented()
  );
}

/**
 * Reset instrumentation state.
 *
 * This is primarily for testing to ensure clean state between tests.
 */
export function resetInstrumentationState(): void {
  _instrumented = false;
}
