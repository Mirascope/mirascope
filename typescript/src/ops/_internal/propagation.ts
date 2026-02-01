/**
 * Context propagation utilities for distributed tracing.
 *
 * Provides helpers for extracting and injecting trace context from/to HTTP headers
 * and other carriers, supporting multiple propagation formats.
 */

import {
  propagation,
  context as otelContext,
  type Context,
  type TextMapGetter,
  type TextMapSetter,
} from "@opentelemetry/api";
import {
  W3CTraceContextPropagator,
  CompositePropagator,
} from "@opentelemetry/core";
import { B3Propagator, B3InjectEncoding } from "@opentelemetry/propagator-b3";
import { JaegerPropagator } from "@opentelemetry/propagator-jaeger";

import type { PropagatorFormat } from "@/ops/_internal/types";

import { SESSION_HEADER_NAME, currentSession } from "@/ops/_internal/session";

let _propagator: ContextPropagator | null = null;

/**
 * Getter for extracting values from a carrier object.
 */
const headerGetter: TextMapGetter<Record<string, string | string[]>> = {
  get(carrier, key) {
    const value = carrier[key];
    if (Array.isArray(value)) {
      return value[0];
    }
    return value;
  },
  /* v8 ignore start - required by TextMapGetter interface but not called by standard propagators */
  keys(carrier) {
    return Object.keys(carrier);
  },
  /* v8 ignore end */
};

/**
 * Setter for injecting values into a carrier object.
 */
const headerSetter: TextMapSetter<Record<string, string>> = {
  set(carrier, key, value) {
    carrier[key] = value;
  },
};

/**
 * Context propagator for distributed tracing.
 *
 * Handles extraction and injection of trace context from/to HTTP headers
 * using various propagation formats (W3C TraceContext, B3, Jaeger).
 *
 * @example
 * ```typescript
 * // Create and use a propagator
 * const propagator = new ContextPropagator();
 *
 * // Extract context from incoming request
 * const ctx = propagator.extractContext(req.headers);
 *
 * // Inject context into outgoing request
 * const headers: Record<string, string> = {};
 * propagator.injectContext(headers);
 * ```
 */
export class ContextPropagator {
  private readonly _format: PropagatorFormat;

  /**
   * Create a new ContextPropagator.
   *
   * @param setGlobal - Whether to set this as the global propagator (default: true).
   * @param format - The propagation format to use. Defaults to MIRASCOPE_PROPAGATOR
   *                 environment variable or 'tracecontext'.
   */
  constructor(
    private readonly setGlobal = true,
    format?: PropagatorFormat,
  ) {
    this._format =
      format ??
      ((process.env.MIRASCOPE_PROPAGATOR as PropagatorFormat) ||
        "tracecontext");
    const propagatorInstance = this.createPropagator(this._format);

    if (this.setGlobal) {
      propagation.setGlobalPropagator(propagatorInstance);
    }
  }

  /**
   * Create a propagator instance for the given format.
   */
  private createPropagator(format: PropagatorFormat) {
    switch (format) {
      case "tracecontext":
        return new W3CTraceContextPropagator();
      case "b3":
        return new B3Propagator({
          injectEncoding: B3InjectEncoding.SINGLE_HEADER,
        });
      case "b3multi":
        return new B3Propagator({
          injectEncoding: B3InjectEncoding.MULTI_HEADER,
        });
      case "jaeger":
        return new JaegerPropagator();
      case "composite":
        return new CompositePropagator({
          propagators: [
            new W3CTraceContextPropagator(),
            new B3Propagator(),
            new JaegerPropagator(),
          ],
        });
      default:
        return new W3CTraceContextPropagator();
    }
  }

  /**
   * Get the propagation format being used.
   */
  get format(): PropagatorFormat {
    return this._format;
  }

  /**
   * Extract context from a carrier (e.g., HTTP headers).
   *
   * @param carrier - The carrier object containing trace context headers.
   * @returns The extracted OpenTelemetry context.
   */
  extractContext(carrier: Record<string, string | string[]>): Context {
    return propagation.extract(otelContext.active(), carrier, headerGetter);
  }

  /**
   * Inject context into a carrier (e.g., HTTP headers).
   *
   * Also injects the Mirascope session ID header if a session is active.
   *
   * @param carrier - The carrier object to inject trace context into.
   * @param context - Optional context to inject. Defaults to active context.
   */
  injectContext(carrier: Record<string, string>, context?: Context): void {
    propagation.inject(context ?? otelContext.active(), carrier, headerSetter);

    // Also inject session ID if available
    const session = currentSession();
    if (session) {
      carrier[SESSION_HEADER_NAME] = session.id;
    }
  }
}

/**
 * Get the global ContextPropagator instance.
 *
 * Creates one if it doesn't exist.
 *
 * @returns The global ContextPropagator.
 */
export function getPropagator(): ContextPropagator {
  if (!_propagator) {
    _propagator = new ContextPropagator();
  }
  return _propagator;
}

/**
 * Reset the global propagator.
 *
 * Primarily useful for testing.
 */
export function resetPropagator(): void {
  _propagator = null;
}

/**
 * Extract context from a carrier using the global propagator.
 *
 * @param carrier - The carrier object containing trace context headers.
 * @returns The extracted OpenTelemetry context.
 *
 * @example
 * ```typescript
 * // In an HTTP handler
 * const ctx = extractContext(req.headers);
 * ```
 */
export function extractContext(
  carrier: Record<string, string | string[]>,
): Context {
  return getPropagator().extractContext(carrier);
}

/**
 * Inject context into a carrier using the global propagator.
 *
 * @param carrier - The carrier object to inject trace context into.
 * @param context - Optional context to inject. Defaults to active context.
 *
 * @example
 * ```typescript
 * // Before making an outgoing HTTP request
 * const headers: Record<string, string> = {};
 * injectContext(headers);
 * fetch(url, { headers });
 * ```
 */
export function injectContext(
  carrier: Record<string, string>,
  context?: Context,
): void {
  getPropagator().injectContext(carrier, context);
}

/**
 * Run a function with context extracted from a carrier.
 *
 * Extracts trace context from the carrier and runs the function with that
 * context active, ensuring proper parent-child span relationships.
 *
 * @param carrier - The carrier object containing trace context headers.
 * @param fn - The function to execute within the extracted context.
 * @returns The result of the function.
 *
 * @example
 * ```typescript
 * // In an HTTP handler
 * await propagatedContext(req.headers, async () => {
 *   // Spans created here are linked to the incoming trace
 *   await span('handle-request', async (s) => {
 *     // Process request
 *   });
 * });
 * ```
 */
export async function propagatedContext<T>(
  carrier: Record<string, string | string[]>,
  fn: () => T | Promise<T>,
): Promise<T> {
  const ctx = extractContext(carrier);
  return otelContext.with(ctx, () => fn());
}
