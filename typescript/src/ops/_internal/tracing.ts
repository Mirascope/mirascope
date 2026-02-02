/**
 * Tracing wrapper for functions and calls.
 *
 * Provides the trace() function for wrapping async functions OR Call objects
 * with OpenTelemetry tracing instrumentation.
 *
 * This unified API matches Python's @ops.trace decorator pattern.
 */

import { context as otelContext, trace as otelTrace } from "@opentelemetry/api";

import type { TraceOptions } from "@/ops/_internal/types";

import { Span } from "@/ops/_internal/spans";
import {
  traceCall,
  isCallLike,
  type TracedCall,
  type CallLike,
} from "@/ops/_internal/traced-calls";
import { createTrace, type Trace } from "@/ops/_internal/traced-functions";
import {
  jsonStringify,
  getQualifiedName,
  extractArguments,
  toJsonable,
  type NamedCallable,
} from "@/ops/_internal/utils";

// Re-export types for convenience
export type { TracedCall, CallLike } from "@/ops/_internal/traced-calls";

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
    "mirascope.fn.module": "", // TypeScript doesn't have module metadata like Python (yet)
    "mirascope.fn.is_async": true, // All traced functions in TypeScript are async
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
 * Wrap a Call object with tracing instrumentation.
 *
 * This overload handles Call objects created with defineCall().
 *
 * @param call - The call to trace
 * @param options - Optional trace options (tags, metadata)
 * @returns A traced call that creates spans on each invocation
 *
 * @example
 * ```typescript
 * const recommendBook = defineCall({
 *   model: 'anthropic/claude-sonnet-4-20250514',
 *   template: ({ genre }: { genre: string }) => `Recommend a ${genre} book`,
 * });
 *
 * const tracedCall = trace(recommendBook, { tags: ['recommendation'] });
 * const response = await tracedCall({ genre: 'fantasy' });
 * ```
 */
export function trace<CallT extends CallLike>(
  call: CallT,
  options?: TraceOptions,
): TracedCall<CallT>;

/**
 * Create a tracing wrapper with options (curried form).
 *
 * @param options - Trace options (tags, metadata)
 * @returns A function that accepts the function or call to trace
 *
 * @example
 * ```typescript
 * const withTracing = trace({ tags: ['api'] });
 * const tracedFn = withTracing(async (x: number) => x * 2);
 * ```
 */
export function trace(options: TraceOptions): {
  <Args extends unknown[], R>(
    fn: (...args: Args) => Promise<R>,
  ): TracedFunction<Args, R>;
  <CallT extends CallLike>(call: CallT): TracedCall<CallT>;
};

export function trace<Args extends unknown[], R, CallT extends CallLike>(
  fnOrCallOrOptions: ((...args: Args) => Promise<R>) | CallT | TraceOptions,
  maybeOptions?: TraceOptions,
):
  | TracedFunction<Args, R>
  | TracedCall<CallT>
  | {
      <A extends unknown[], T>(
        fn: (...args: A) => Promise<T>,
      ): TracedFunction<A, T>;
      <C extends CallLike>(call: C): TracedCall<C>;
    } {
  // Curried form: trace(options)(fn or call)
  if (typeof fnOrCallOrOptions !== "function") {
    const options = fnOrCallOrOptions as TraceOptions;
    // Return a function that handles both functions and calls
    return (<T>(target: T) => {
      if (isCallLike(target)) {
        return traceCall(target, options);
      }
      return trace(target as (...args: unknown[]) => Promise<unknown>, options);
    }) as {
      <A extends unknown[], T>(
        fn: (...args: A) => Promise<T>,
      ): TracedFunction<A, T>;
      <C extends CallLike>(call: C): TracedCall<C>;
    };
  }

  // Check if it's a Call object - delegate to traceCall
  if (isCallLike(fnOrCallOrOptions)) {
    return traceCall(
      fnOrCallOrOptions,
      maybeOptions,
    ) as unknown as TracedCall<CallT>;
  }

  const fn = fnOrCallOrOptions as (...args: Args) => Promise<R>;
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
          span.recordException(error);
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
          span.recordException(error);
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
