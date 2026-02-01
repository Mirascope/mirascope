/**
 * Span management for explicit tracing in the Mirascope ops module.
 */

import {
  trace,
  context as otelContext,
  SpanStatusCode,
  type Span as OtelSpan,
  type SpanContext,
} from "@opentelemetry/api";

import { currentSession } from "@/ops/_internal/session";
import { jsonStringify } from "@/ops/_internal/utils";

/**
 * A wrapper around OpenTelemetry spans with convenience methods for logging.
 *
 * Provides a fluent API for creating spans, setting attributes, adding events,
 * and logging at different severity levels.
 *
 * @example
 * ```typescript
 * const span = new Span('my-operation', { 'initial.attr': 'value' });
 * span.start();
 *
 * span.info('Starting operation');
 * span.set({ 'custom.key': 'value' });
 *
 * try {
 *   // Do work
 * } catch (error) {
 *   span.error(error.message);
 * } finally {
 *   span.finish();
 * }
 * ```
 */
export class Span {
  private _span: OtelSpan | null = null;
  private _isNoop = true;
  private _finished = false;

  /**
   * Create a new Span wrapper.
   *
   * @param _name - The name of the span.
   * @param _initialAttributes - Optional initial attributes to set on the span.
   */
  constructor(
    private readonly _name: string,
    private readonly _initialAttributes: Record<string, unknown> = {},
  ) {}

  /**
   * Start the span.
   *
   * Creates the underlying OpenTelemetry span and sets initial attributes
   * including session context if available.
   *
   * @returns This span instance for chaining.
   */
  start(): this {
    const tracer = trace.getTracer("mirascope.ops");
    this._span = tracer.startSpan(this._name, undefined, otelContext.active());

    // Check if this is a noop span (no tracer configured)
    if (this._span.constructor.name === "NonRecordingSpan") {
      this._isNoop = true;
      this._span = null;
    } else {
      this._isNoop = false;
      this._span.setAttribute("mirascope.type", "span");

      // Add session context if available
      const session = currentSession();
      if (session) {
        this._span.setAttribute("mirascope.ops.session.id", session.id);
        if (session.attributes) {
          this._span.setAttribute(
            "mirascope.ops.session.attributes",
            jsonStringify(session.attributes),
          );
        }
      }

      // Set initial attributes
      if (Object.keys(this._initialAttributes).length > 0) {
        this.set(this._initialAttributes);
      }
    }

    return this;
  }

  /**
   * Set attributes on the span.
   *
   * Objects are automatically JSON-serialized.
   *
   * @param attributes - Key-value pairs to set as span attributes.
   */
  set(attributes: Record<string, unknown>): void {
    if (this._span && !this._finished) {
      for (const [key, value] of Object.entries(attributes)) {
        const attrValue =
          typeof value === "object" && value !== null
            ? jsonStringify(value)
            : value;
        this._span.setAttribute(
          key,
          attrValue as string | number | boolean | string[] | number[],
        );
      }
    }
  }

  /**
   * Add an event to the span.
   *
   * @param name - The name of the event.
   * @param attributes - Optional attributes for the event.
   */
  event(name: string, attributes?: Record<string, unknown>): void {
    if (this._span && !this._finished) {
      const processedAttrs: Record<string, string | number | boolean> = {};
      if (attributes) {
        for (const [key, value] of Object.entries(attributes)) {
          if (
            typeof value === "string" ||
            typeof value === "number" ||
            typeof value === "boolean"
          ) {
            processedAttrs[key] = value;
          } else {
            processedAttrs[key] = jsonStringify(value);
          }
        }
      }
      this._span.addEvent(name, processedAttrs);
    }
  }

  /**
   * Log a debug-level message to the span.
   *
   * @param message - The log message.
   * @param attributes - Optional additional attributes.
   */
  debug(message: string, attributes?: Record<string, unknown>): void {
    this.event("log", { level: "debug", message, ...attributes });
  }

  /**
   * Log an info-level message to the span.
   *
   * @param message - The log message.
   * @param attributes - Optional additional attributes.
   */
  info(message: string, attributes?: Record<string, unknown>): void {
    this.event("log", { level: "info", message, ...attributes });
  }

  /**
   * Log a warning-level message to the span.
   *
   * @param message - The log message.
   * @param attributes - Optional additional attributes.
   */
  warning(message: string, attributes?: Record<string, unknown>): void {
    this.event("log", { level: "warning", message, ...attributes });
  }

  /**
   * Log an error-level message and set span status to ERROR.
   *
   * @param message - The error message.
   * @param attributes - Optional additional attributes.
   */
  error(message: string, attributes?: Record<string, unknown>): void {
    this.event("log", { level: "error", message, ...attributes });
    if (this._span && !this._finished) {
      this._span.setStatus({ code: SpanStatusCode.ERROR, message });
    }
  }

  /**
   * Log a critical-level message and set span status to ERROR.
   *
   * @param message - The critical error message.
   * @param attributes - Optional additional attributes.
   */
  critical(message: string, attributes?: Record<string, unknown>): void {
    this.event("log", { level: "critical", message, ...attributes });
    if (this._span && !this._finished) {
      this._span.setStatus({ code: SpanStatusCode.ERROR, message });
    }
  }

  /**
   * End the span.
   *
   * The span cannot be modified after calling finish().
   */
  finish(): void {
    if (!this._finished) {
      this._finished = true;
      this._span?.end();
    }
  }

  /**
   * Get the span ID if available.
   */
  get spanId(): string | null {
    return this._span?.spanContext().spanId ?? null;
  }

  /**
   * Get the trace ID if available.
   */
  get traceId(): string | null {
    return this._span?.spanContext().traceId ?? null;
  }

  /**
   * Check if this is a noop span (no tracer configured).
   */
  get isNoop(): boolean {
    return this._isNoop;
  }

  /**
   * Get the underlying span context if available.
   */
  get spanContext(): SpanContext | null {
    return this._span?.spanContext() ?? null;
  }

  /**
   * Check if the span has been finished.
   */
  get isFinished(): boolean {
    return this._finished;
  }

  /**
   * Get the underlying OpenTelemetry span.
   *
   * Primarily for internal use.
   */
  get otelSpan(): OtelSpan | null {
    return this._span;
  }
}

/**
 * Execute a function within a span context.
 *
 * Creates a span, executes the function, and automatically finishes the span
 * when the function completes (or throws). Errors are logged to the span
 * before being re-thrown.
 *
 * @param name - The name of the span.
 * @param fn - The function to execute within the span context.
 * @param attributes - Optional initial attributes for the span.
 * @returns The result of the function.
 *
 * @example
 * ```typescript
 * const result = await span('process-data', async (s) => {
 *   s.info('Starting processing');
 *   s.set({ 'data.count': items.length });
 *
 *   const processed = await processItems(items);
 *
 *   s.info('Processing complete');
 *   return processed;
 * });
 * ```
 */
export async function span<T>(
  name: string,
  fn: (span: Span) => T | Promise<T>,
  attributes?: Record<string, unknown>,
): Promise<T> {
  const s = new Span(name, attributes).start();
  try {
    return await fn(s);
  } catch (error) {
    if (error instanceof Error) {
      s.error(error.message);
    } else {
      s.error(String(error));
    }
    throw error;
    /* v8 ignore start - finally is always executed, v8 branch tracking artifact */
  } finally {
    /* v8 ignore end */
    s.finish();
  }
}
