/**
 * Types for versioned functions.
 *
 * Provides type definitions for closure metadata (injected at compile time)
 * and versioned function results.
 */

import type { Span } from "@/ops/_internal/spans";
import type { Jsonable } from "@/ops/_internal/types";

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
  /** SHA256 hash of the function's code */
  readonly hash: string;
  /** SHA256 hash of the function's signature */
  readonly signatureHash: string;
  /** Name of the function */
  readonly name: string;
  /** Human-readable description (docstring) of the versioned function */
  readonly description?: string;
  /** Auto-computed semantic version in X.Y format */
  readonly version: string;
  /** Tags associated with the function */
  readonly tags: string[];
  /** Key-value metadata */
  readonly metadata: Record<string, string>;
}

/**
 * Computes the version string from the closure hash.
 *
 * For new functions without server history, returns "1.0" as the initial version.
 *
 * @param _hash - SHA256 hash of the complete closure code (unused)
 * @returns Version string in X.Y format
 */
export function computeVersion(_hash: string): string {
  return "1.0";
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
  /**
   * Annotate this trace with a pass/fail label.
   *
   * Sets annotation attributes on the span.
   */
  annotate(options: AnnotateOptions): void;
  /**
   * Add tags to this trace.
   *
   * @param tags - Tags to add to the trace
   * @throws NotImplementedError - This feature is not yet implemented
   */
  tag(...tags: string[]): Promise<void>;
  /**
   * Assign this trace to users by email.
   *
   * @param emails - Email addresses to assign the trace to
   * @throws NotImplementedError - This feature is not yet implemented
   */
  assign(...emails: string[]): Promise<void>;
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
  /**
   * Get a specific version of this function.
   *
   * @param versionId - The version identifier (tag, hash, or semantic version)
   * @returns A VersionedFunction bound to the specified version
   * @throws NotImplementedError - This feature is not yet implemented
   */
  getVersion(versionId: string): Promise<VersionedFunction<Args, R>>;
}

/**
 * Create a VersionedResult from a function return value and span.
 *
 * @param result - The result returned by the versioned function
 * @param span - The span associated with this execution
 * @returns A VersionedResult object with the result and metadata
 */
export function createVersionedResult<R>(
  result: R,
  span: Span,
): VersionedResult<R> {
  return {
    result,
    span,
    get spanId() {
      return span.spanId;
    },
    get traceId() {
      return span.traceId;
    },
    annotate({ label, reasoning, metadata }) {
      const spanId = span.spanId;
      const traceId = span.traceId;

      if (!spanId || !traceId) {
        return;
      }

      span.set({ "mirascope.annotation.label": label });

      if (reasoning) {
        span.set({ "mirascope.annotation.reasoning": reasoning });
      }

      if (metadata) {
        span.set({
          "mirascope.annotation.metadata": JSON.stringify(metadata),
        });
      }
    },
    async tag(..._tags: string[]): Promise<void> {
      throw new Error(
        "tag() is not yet implemented. Tagging will be available in a future release.",
      );
    },
    async assign(..._emails: string[]): Promise<void> {
      throw new Error(
        "assign() is not yet implemented. Assignment will be available in a future release.",
      );
    },
  };
}
