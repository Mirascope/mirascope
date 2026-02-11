/**
 * Configuration utilities for Mirascope ops module initialization and setup.
 */

import type { Tracer } from "@opentelemetry/api";

import {
  NodeTracerProvider,
  BatchSpanProcessor,
} from "@opentelemetry/sdk-trace-node";

import { MirascopeClient } from "@/api/client";
import { updateSettings } from "@/api/settings";
import { MirascopeOTLPExporter } from "@/ops/_internal/exporters";

const DEFAULT_TRACER_NAME = "mirascope.llm";

let _tracerProvider: NodeTracerProvider | null = null;
let _tracerName: string = DEFAULT_TRACER_NAME;
let _tracerVersion: string | undefined = undefined;
let _tracer: Tracer | null = null;

/**
 * Options for configuring the ops module.
 */
export interface ConfigureOptions {
  /** Mirascope Cloud API key */
  apiKey?: string;
  /** Mirascope Cloud base URL */
  baseURL?: string;
  /** Custom tracer provider (overrides automatic Mirascope Cloud setup) */
  tracerProvider?: NodeTracerProvider;
  /** Tracer name (default: "mirascope.llm") */
  tracerName?: string;
  /** Tracer version */
  tracerVersion?: string;
}

/**
 * Create a TracerProvider configured for Mirascope Cloud.
 */
function createMirascopeCloudProvider(
  apiKey?: string,
  baseURL?: string,
): NodeTracerProvider {
  const client = new MirascopeClient({ apiKey, baseURL });
  const exporter = new MirascopeOTLPExporter(client);
  const provider = new NodeTracerProvider({
    spanProcessors: [new BatchSpanProcessor(exporter)],
  });
  return provider;
}

/**
 * Configure the ops module for tracing.
 *
 * When called without arguments, automatically configures Mirascope Cloud
 * using the MIRASCOPE_API_KEY environment variable.
 *
 * @example
 * Simple Mirascope Cloud configuration (recommended):
 * ```typescript
 * import { ops } from 'mirascope';
 *
 * // Assumes MIRASCOPE_API_KEY is set in environment
 * ops.configure();
 * ```
 *
 * @example
 * With explicit API key:
 * ```typescript
 * import { ops } from 'mirascope';
 *
 * ops.configure({ apiKey: 'your-api-key' });
 * ```
 *
 * @example
 * With custom tracer provider:
 * ```typescript
 * import { ops } from 'mirascope';
 * import { NodeTracerProvider } from '@opentelemetry/sdk-trace-node';
 *
 * const provider = new NodeTracerProvider();
 * ops.configure({ tracerProvider: provider });
 * ```
 */
export function configure(options: ConfigureOptions = {}): void {
  const {
    apiKey,
    baseURL,
    tracerProvider,
    tracerName = DEFAULT_TRACER_NAME,
    tracerVersion,
  } = options;

  // Update API settings if provided
  if (apiKey !== undefined || baseURL !== undefined) {
    updateSettings({ apiKey, baseURL });
  }

  // Use custom provider or create Mirascope Cloud provider
  if (tracerProvider) {
    _tracerProvider = tracerProvider;
  } else {
    _tracerProvider = createMirascopeCloudProvider(apiKey, baseURL);
  }

  // Register the provider which sets up both tracer provider AND context manager
  // This is critical for async context propagation (span nesting)
  _tracerProvider.register();

  _tracerName = tracerName;
  _tracerVersion = tracerVersion;
  _tracer = _tracerProvider.getTracer(_tracerName, _tracerVersion);
}

/**
 * Get the configured tracer instance.
 *
 * @returns The current tracer, or null if not configured.
 */
export function getTracer(): Tracer | null {
  return _tracer;
}

/**
 * Set the tracer instance.
 *
 * @param tracer - The tracer to set, or null to clear.
 */
export function setTracer(tracer: Tracer | null): void {
  _tracer = tracer;
}

/**
 * Run a function with a temporary tracer.
 *
 * Temporarily sets the tracer for the duration of the function execution
 * and restores the previous tracer when the function returns.
 *
 * @param tracer - The tracer to use during function execution.
 * @param fn - The function to execute.
 * @returns The result of the function.
 *
 * @example
 * ```typescript
 * import { ops } from 'mirascope';
 * import { NodeTracerProvider } from '@opentelemetry/sdk-trace-node';
 *
 * const provider = new NodeTracerProvider();
 * const tracer = provider.getTracer('my-tracer');
 *
 * const result = ops.tracerContext(tracer, () => {
 *   // Use the tracer within this context
 *   return someOperation();
 * });
 * // Previous tracer is restored here
 * ```
 */
export function tracerContext<T>(tracer: Tracer | null, fn: () => T): T {
  const previous = _tracer;
  _tracer = tracer;
  try {
    return fn();
  } finally {
    _tracer = previous;
  }
}

/**
 * Force flush all pending spans to be exported.
 *
 * Convenience wrapper around the standard OpenTelemetry
 * {@link NodeTracerProvider.forceFlush} method. Delegates directly to the
 * underlying provider; no-ops when {@link configure} has not been called.
 *
 * @returns A promise that resolves when all spans have been flushed.
 *
 * @example
 * ```typescript
 * import { ops } from 'mirascope';
 *
 * ops.configure();
 * ops.instrumentLLM();
 *
 * // Run your traced operations
 * await myTracedFunction();
 *
 * // Force flush before script exits
 * await ops.forceFlush();
 * ```
 */
export async function forceFlush(): Promise<void> {
  if (_tracerProvider) {
    await _tracerProvider.forceFlush();
  }
}

/**
 * Shutdown the tracer provider and flush all pending spans.
 *
 * Convenience wrapper around the standard OpenTelemetry
 * {@link NodeTracerProvider.shutdown} method. Delegates directly to the
 * underlying provider; no-ops when {@link configure} has not been called.
 *
 * @returns A promise that resolves when the provider has been shut down.
 *
 * @example
 * ```typescript
 * import { ops } from 'mirascope';
 *
 * // At application shutdown
 * process.on('SIGTERM', async () => {
 *   await ops.shutdown();
 *   process.exit(0);
 * });
 * ```
 */
export async function shutdown(): Promise<void> {
  if (_tracerProvider) {
    await _tracerProvider.shutdown();
  }
}

/**
 * Reset configuration state.
 *
 * This is primarily useful for testing to ensure a clean state between tests.
 */
export function resetConfiguration(): void {
  _tracerProvider = null;
  _tracerName = DEFAULT_TRACER_NAME;
  _tracerVersion = undefined;
  _tracer = null;
}
