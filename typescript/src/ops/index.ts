/**
 * Mirascope ops module for tracing, versioning, and observability.
 */

// Configuration
export { configure, tracerContext } from "@/ops/_internal/configuration";
export type { ConfigureOptions } from "@/ops/_internal/configuration";

// Exceptions
export { ClosureComputationError } from "@/ops/exceptions";
