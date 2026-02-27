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
 * Base options shared by tracing and versioning.
 */
export interface BaseOpsOptions {
  /** Tags to attach to the span */
  tags?: string[];
  /** Key-value metadata to attach to the span */
  metadata?: Record<string, string>;
}

/**
 * Options for tracing a function.
 * Name is required since arrow functions have no name.
 */
export interface TraceOptions extends BaseOpsOptions {
  /** Name for the traced function (required since arrow functions have no name) */
  name: string;
}

/**
 * Options for versioning a function.
 * Name is optional since it can be inferred from the function/call.
 */
export interface VersionOptions extends BaseOpsOptions {
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
