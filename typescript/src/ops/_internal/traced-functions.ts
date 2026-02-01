/**
 * Trace result types for traced functions.
 */

import type { Span } from "@/ops/_internal/spans";
import type { Jsonable } from "@/ops/_internal/types";

import { getClient } from "@/api/client";

/**
 * Result of a traced function execution.
 *
 * Contains the function result along with tracing metadata and
 * an annotate() method for labeling traces as pass/fail.
 */
export interface Trace<R> {
  /** The result returned by the traced function */
  readonly result: R;
  /** The span associated with this trace */
  readonly span: Span;
  /** The OTEL span ID, if available */
  readonly spanId: string | null;
  /** The OTEL trace ID, if available */
  readonly traceId: string | null;
  /**
   * Annotate this trace with a pass/fail label.
   *
   * Sends the annotation to Mirascope Cloud for evaluation tracking.
   *
   * @param options - Annotation options
   * @param options.label - 'pass' or 'fail' label
   * @param options.reasoning - Optional reasoning for the label
   * @param options.metadata - Optional additional metadata
   */
  annotate(options: AnnotateOptions): Promise<void>;
}

/**
 * Options for annotating a trace.
 */
export interface AnnotateOptions {
  /** Pass or fail label */
  label: "pass" | "fail";
  /** Optional reasoning for the label */
  reasoning?: string;
  /** Optional additional metadata */
  metadata?: Record<string, Jsonable>;
}

/**
 * Create a Trace result from a function return value and span.
 *
 * @param result - The result returned by the traced function
 * @param span - The span associated with this trace
 * @returns A Trace object with the result and tracing metadata
 */
export function createTrace<R>(result: R, span: Span): Trace<R> {
  return {
    result,
    span,
    get spanId() {
      return span.spanId;
    },
    get traceId() {
      return span.traceId;
    },
    async annotate({ label, reasoning, metadata }) {
      const spanId = span.spanId;
      const traceId = span.traceId;

      if (!spanId || !traceId) {
        return;
      }

      const client = getClient();
      await client.annotations.create({
        otelSpanId: spanId,
        otelTraceId: traceId,
        label,
        reasoning: reasoning ?? null,
        metadata: metadata ?? null,
      });
    },
  };
}
