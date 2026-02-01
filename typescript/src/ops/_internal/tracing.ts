/**
 * Tracing wrapper for functions.
 *
 * Provides the trace() function for wrapping async functions with
 * OpenTelemetry tracing instrumentation.
 */

import { context as otelContext, trace as otelTrace } from "@opentelemetry/api";

import type { TraceOptions } from "@/ops/_internal/types";

import { Span } from "@/ops/_internal/spans";
import { createTrace, type Trace } from "@/ops/_internal/traced-functions";
import {
  jsonStringify,
  getQualifiedName,
  extractArguments,
  toJsonable,
  type NamedCallable,
} from "@/ops/_internal/utils";

/**
 * A traced function with access to the wrapped result.
 *
 * Call normally to get the function result directly.
 * Call `.wrapped()` to get the full Trace object with span metadata.
 */
export interface TracedFunction<Args extends unknown[], R> {
  /** Execute the function and return the result directly */
  (...args: Args): Promise<R>;
  /** Execute the function and return the full Trace object */
  wrapped(...args: Args): Promise<Trace<R>>;
}

/**
 * Create a span for a traced function invocation.
 */
function createTracedSpan<Args extends unknown[]>(
  fn: NamedCallable,
  options: TraceOptions,
  args: Args,
): Span {
  const qualifiedName = getQualifiedName(fn);
  const { argTypes, argValues } = extractArguments(fn, args);

  const span = new Span(qualifiedName);
  span.start();

  span.set({
    "mirascope.type": "trace",
    "mirascope.fn.qualname": qualifiedName,
    "mirascope.trace.arg_types": jsonStringify(argTypes),
    "mirascope.trace.arg_values": jsonStringify(argValues),
  });

  if (options.tags && options.tags.length > 0) {
    span.set({ "mirascope.trace.tags": options.tags });
  }

  if (options.metadata && Object.keys(options.metadata).length > 0) {
    span.set({ "mirascope.trace.metadata": jsonStringify(options.metadata) });
  }

  return span;
}

/**
 * Record the result of a traced function on its span.
 */
function recordResult(span: Span, result: unknown): void {
  if (result === null || result === undefined) {
    return;
  }

  let output: string;
  if (
    typeof result === "string" ||
    typeof result === "number" ||
    typeof result === "boolean"
  ) {
    output = String(result);
  } else {
    output = jsonStringify(toJsonable(result));
  }

  span.set({ "mirascope.trace.output": output });
}

/**
 * Wrap a function with tracing instrumentation.
 *
 * @param fn - The async function to trace
 * @param options - Optional trace options (tags, metadata)
 * @returns A traced function that creates spans on each invocation
 *
 * @example Direct form
 * ```typescript
 * const tracedFn = trace(async (x: number) => x * 2);
 * const result = await tracedFn(5);  // Returns 10
 * ```
 *
 * @example With options
 * ```typescript
 * const tracedFn = trace(
 *   async (x: number) => x * 2,
 *   { tags: ['math'], metadata: { operation: 'double' } }
 * );
 * ```
 *
 * @example Accessing span metadata
 * ```typescript
 * const traced = await tracedFn.wrapped(5);
 * console.log(traced.result);  // 10
 * console.log(traced.traceId); // The trace ID
 * await traced.annotate({ label: 'pass' });
 * ```
 */
export function trace<Args extends unknown[], R>(
  fn: (...args: Args) => Promise<R>,
  options?: TraceOptions,
): TracedFunction<Args, R>;

/**
 * Create a tracing wrapper with options (curried form).
 *
 * @param options - Trace options (tags, metadata)
 * @returns A function that accepts the function to trace
 *
 * @example
 * ```typescript
 * const withTracing = trace({ tags: ['api'] });
 * const tracedFn = withTracing(async (x: number) => x * 2);
 * ```
 */
export function trace(
  options: TraceOptions,
): <Args extends unknown[], R>(
  fn: (...args: Args) => Promise<R>,
) => TracedFunction<Args, R>;

export function trace<Args extends unknown[], R>(
  fnOrOptions: ((...args: Args) => Promise<R>) | TraceOptions,
  maybeOptions?: TraceOptions,
):
  | TracedFunction<Args, R>
  | (<A extends unknown[], T>(
      fn: (...args: A) => Promise<T>,
    ) => TracedFunction<A, T>) {
  if (typeof fnOrOptions !== "function") {
    const options = fnOrOptions;
    return <A extends unknown[], T>(fn: (...args: A) => Promise<T>) =>
      trace(fn, options);
  }

  const fn = fnOrOptions;
  const options = maybeOptions ?? {};

  const traced = async (...args: Args): Promise<R> => {
    const span = createTracedSpan(fn, options, args);

    // Run within the span's context so child spans are properly linked
    const otelSpan = span.otelSpan;
    /* v8 ignore start - ternary branch with no-tracer case difficult to test */
    const runInContext = otelSpan
      ? () =>
          otelContext.with(
            otelTrace.setSpan(otelContext.active(), otelSpan),
            execute,
          )
      : execute;
    /* v8 ignore end */

    async function execute(): Promise<R> {
      try {
        const result = await fn(...args);
        recordResult(span, result);
        return result;
      } catch (error) {
        if (error instanceof Error) {
          span.error(error.message);
        } else {
          span.error(String(error));
        }
        throw error;
      } finally {
        span.finish();
      }
    }

    return runInContext();
  };

  traced.wrapped = async (...args: Args): Promise<Trace<R>> => {
    const span = createTracedSpan(fn, options, args);

    const otelSpan = span.otelSpan;
    /* v8 ignore start - ternary branch with no-tracer case difficult to test */
    const runInContext = otelSpan
      ? () =>
          otelContext.with(
            otelTrace.setSpan(otelContext.active(), otelSpan),
            execute,
          )
      : execute;
    /* v8 ignore end */

    async function execute(): Promise<Trace<R>> {
      try {
        const result = await fn(...args);
        recordResult(span, result);
        return createTrace(result, span);
      } catch (error) {
        if (error instanceof Error) {
          span.error(error.message);
        } else {
          span.error(String(error));
        }
        throw error;
      } finally {
        span.finish();
      }
    }

    return runInContext();
  };

  return traced as TracedFunction<Args, R>;
}
