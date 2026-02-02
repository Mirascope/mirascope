/**
 * Tracing wrapper for Call objects.
 *
 * Provides the traceCall() function for wrapping calls with
 * OpenTelemetry tracing instrumentation.
 */

import { context as otelContext, trace as otelTrace } from "@opentelemetry/api";

import type { TraceOptions } from "@/ops/_internal/types";

import { Span } from "@/ops/_internal/spans";
import { createTrace, type Trace } from "@/ops/_internal/traced-functions";
import { jsonStringify, toJsonable } from "@/ops/_internal/utils";
import { isCallLike, type CallLike } from "@/ops/_internal/versioned-calls";

// Re-export for use in tracing.ts
export { isCallLike, type CallLike } from "@/ops/_internal/versioned-calls";

/**
 * A traced call with access to the wrapped result.
 *
 * Call normally to get the response directly.
 * Call `.wrapped()` to get the full Trace object with span metadata.
 */
export interface TracedCall<CallT> {
  /** Execute the call and return the response directly */
  (...args: unknown[]): Promise<unknown>;
  /** Execute the call and return the full Trace object */
  wrapped(...args: unknown[]): Promise<Trace<unknown>>;
  /** Stream the call and return the stream response directly */
  stream(...args: unknown[]): Promise<unknown>;
  /** Stream the call and return the full Trace object with stream response */
  wrappedStream(...args: unknown[]): Promise<Trace<unknown>>;
  /** The underlying call */
  readonly call: CallT;
}

/**
 * Create a span for a traced call invocation.
 */
function createTracedCallSpan(
  callName: string,
  options: TraceOptions,
  vars: unknown,
): Span {
  const span = new Span(callName);
  span.start();

  span.set({
    "mirascope.type": "trace",
    "mirascope.call.name": callName,
  });

  if (vars !== undefined) {
    span.set({
      "mirascope.call.variables": jsonStringify(toJsonable(vars)),
    });
  }

  if (options.tags && options.tags.length > 0) {
    span.set({ "mirascope.trace.tags": options.tags });
  }

  if (options.metadata && Object.keys(options.metadata).length > 0) {
    span.set({ "mirascope.trace.metadata": jsonStringify(options.metadata) });
  }

  return span;
}

/**
 * Wrap a Call with tracing instrumentation.
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
 * const tracedCall = traceCall(recommendBook, { tags: ['recommendation'] });
 * const response = await tracedCall({ genre: 'fantasy' });
 * ```
 *
 * @example Accessing span metadata
 * ```typescript
 * const traced = await tracedCall.wrapped({ genre: 'fantasy' });
 * console.log(traced.result.text());
 * await traced.annotate({ label: 'pass' });
 * ```
 */
export function traceCall<CallT extends CallLike>(
  call: CallT,
  options?: TraceOptions,
): TracedCall<CallT>;

/**
 * Create a tracing wrapper with options (curried form).
 *
 * @param options - Trace options (tags, metadata)
 * @returns A function that accepts the call to trace
 */
export function traceCall(
  options: TraceOptions,
): <CallT extends CallLike>(call: CallT) => TracedCall<CallT>;

export function traceCall<CallT extends CallLike>(
  callOrOptions: CallT | TraceOptions,
  maybeOptions?: TraceOptions,
): TracedCall<CallT> | (<C extends CallLike>(call: C) => TracedCall<C>) {
  // Curried form
  if (!isCallLike(callOrOptions)) {
    const options = callOrOptions;
    return <C extends CallLike>(c: C) => traceCall(c, options);
  }

  const call = callOrOptions;
  const options = maybeOptions ?? {};

  // Get a name for the call
  const callName =
    call.template.name ||
    (call as { name?: string }).name ||
    call.prompt.template.name ||
    "call";

  // Create the traced wrapper
  const traced = async (...args: unknown[]): Promise<unknown> => {
    const vars = args[0];
    const span = createTracedCallSpan(callName, options, vars);

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

    async function execute(): Promise<unknown> {
      try {
        const response = await call.call(...args);
        return response;
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

  traced.wrapped = async (...args: unknown[]): Promise<Trace<unknown>> => {
    const vars = args[0];
    const span = createTracedCallSpan(callName, options, vars);

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

    async function execute(): Promise<Trace<unknown>> {
      try {
        const response = await call.call(...args);
        return createTrace(response, span);
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

  traced.stream = async (...args: unknown[]): Promise<unknown> => {
    const vars = args[0];
    const span = createTracedCallSpan(callName, options, vars);

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

    async function execute(): Promise<unknown> {
      try {
        const response = await call.stream(...args);
        return response;
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

  traced.wrappedStream = async (
    ...args: unknown[]
  ): Promise<Trace<unknown>> => {
    const vars = args[0];
    const span = createTracedCallSpan(callName, options, vars);

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

    async function execute(): Promise<Trace<unknown>> {
      try {
        const response = await call.stream(...args);
        return createTrace(response, span);
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

  Object.defineProperty(traced, "call", {
    value: call,
    enumerable: true,
  });

  return traced as TracedCall<CallT>;
}
