/**
 * Types for versioned functions.
 *
 * Provides type definitions for closure metadata (injected at compile time)
 * and versioned function results.
 */

import type { Span } from "@/ops/_internal/spans";
import type { Jsonable } from "@/ops/_internal/types";

import { getClient } from "@/api/client";

/**
 * Metadata injected by compile-time transform.
 * This captures the original TypeScript source before compilation.
 */
export interface ClosureMetadata {
  /** Original TypeScript source code */
  readonly code: string;
  /** SHA256 hash of normalized source code */
  readonly hash: string;
  /** Function signature with type annotations */
  readonly signature: string;
  /** SHA256 hash of signature (for signature-only versioning) */
  readonly signatureHash: string;
}

/**
 * Information about a versioned function.
 */
export interface VersionInfo {
  /** UUID assigned by Mirascope Cloud (available after registration) */
  readonly uuid?: string;
  /** SHA256 hash of the function's code */
  readonly hash: string;
  /** SHA256 hash of the function's signature */
  readonly signatureHash: string;
  /** Name of the function */
  readonly name: string;
  /** Tags associated with the function */
  readonly tags: string[];
  /** Key-value metadata */
  readonly metadata: Record<string, string>;
}

/**
 * Result of a versioned function execution.
 *
 * Extends Trace with additional version-specific metadata.
 */
export interface VersionedResult<R> {
  /** The result returned by the versioned function */
  readonly result: R;
  /** The span associated with this execution */
  readonly span: Span;
  /** The OTEL span ID, if available */
  readonly spanId: string | null;
  /** The OTEL trace ID, if available */
  readonly traceId: string | null;
  /** UUID of the registered function, if available */
  readonly functionUuid?: string;
  /**
   * Annotate this trace with a pass/fail label.
   *
   * Sends the annotation to Mirascope Cloud for evaluation tracking.
   */
  annotate(options: AnnotateOptions): Promise<void>;
}

/**
 * Options for annotating a versioned result.
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
 * A versioned function with access to version info and wrapped result.
 *
 * Call normally to get the function result directly.
 * Call `.wrapped()` to get the full VersionedResult object with span metadata.
 * Access `.versionInfo` to get information about the function's version.
 */
export interface VersionedFunction<Args extends unknown[], R> {
  /** Execute the function and return the result directly */
  (...args: Args): Promise<R>;
  /** Execute the function and return the full VersionedResult object */
  wrapped(...args: Args): Promise<VersionedResult<R>>;
  /** Information about the function's version */
  readonly versionInfo: VersionInfo;
}

/**
 * Create a VersionedResult from a function return value and span.
 *
 * @param result - The result returned by the versioned function
 * @param span - The span associated with this execution
 * @param functionUuid - Optional UUID of the registered function
 * @returns A VersionedResult object with the result and metadata
 */
export function createVersionedResult<R>(
  result: R,
  span: Span,
  functionUuid?: string,
): VersionedResult<R> {
  return {
    result,
    span,
    functionUuid,
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
