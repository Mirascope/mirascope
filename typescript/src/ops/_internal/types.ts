/**
 * Core types for the Mirascope ops module.
 */

/**
 * JSON-serializable value type.
 */
export type Jsonable =
  | string
  | number
  | boolean
  | null
  | Jsonable[]
  | { [key: string]: Jsonable };

/**
 * Options for tracing a function.
 */
export interface TraceOptions {
  /** Tags to attach to the trace span */
  tags?: string[];
  /** Key-value metadata to attach to the trace span */
  metadata?: Record<string, string>;
}

/**
 * Options for versioning a function.
 */
export interface VersionOptions extends TraceOptions {
  /** Optional name override for the versioned function */
  name?: string;
}

/**
 * Supported context propagation formats.
 */
export type PropagatorFormat =
  | "tracecontext"
  | "b3"
  | "b3multi"
  | "jaeger"
  | "composite";
