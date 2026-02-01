/**
 * Base class for OpenTelemetry SDK instrumentation.
 *
 * Provides a singleton pattern for managing provider SDK instrumentation lifecycle.
 */

import type { TracerProvider } from "@opentelemetry/api";

/**
 * Content capture mode for provider instrumentation.
 */
export type ContentCaptureMode = "enabled" | "disabled" | "default";

/**
 * OpenTelemetry semantic conventions environment variable.
 */
export const OTEL_SEMCONV_STABILITY_OPT_IN = "OTEL_SEMCONV_STABILITY_OPT_IN";
export const OTEL_SEMCONV_STABILITY_VALUE = "gen_ai_latest_experimental";

/**
 * Protocol for OpenTelemetry instrumentors.
 */
export interface Instrumentor {
  instrument(config?: { tracerProvider?: TracerProvider }): void;
  disable(): void;
}

/**
 * Base class for managing OpenTelemetry instrumentation lifecycle.
 *
 * This class provides a singleton pattern for SDK instrumentation.
 * Subclasses must implement `createInstrumentor()` and `configureContentCapture()`.
 */
export abstract class BaseInstrumentation<T extends Instrumentor> {
  private static instances = new Map<
    string,
    BaseInstrumentation<Instrumentor>
  >();

  protected instrumentor: T | null = null;
  protected originalEnv: Map<string, string | undefined> = new Map();

  /**
   * Get or create the singleton instance for this instrumentation class.
   */
  protected static getInstance<I extends BaseInstrumentation<Instrumentor>>(
    this: new () => I,
    key: string,
  ): I {
    if (!BaseInstrumentation.instances.has(key)) {
      BaseInstrumentation.instances.set(key, new this());
    }
    return BaseInstrumentation.instances.get(key) as I;
  }

  /**
   * Return whether instrumentation is currently active.
   */
  get isInstrumented(): boolean {
    return this.instrumentor !== null;
  }

  /**
   * Create and return a new instrumentor instance.
   */
  protected abstract createInstrumentor(): T;

  /**
   * Configure environment variables for content capture.
   */
  protected abstract configureContentCapture(
    captureContent: ContentCaptureMode,
  ): void;

  /**
   * Enable OpenTelemetry instrumentation for the SDK.
   */
  instrument(
    options: {
      tracerProvider?: TracerProvider;
      captureContent?: ContentCaptureMode;
    } = {},
  ): void {
    const { tracerProvider, captureContent = "default" } = options;

    if (this.isInstrumented) {
      return;
    }

    // Set OpenTelemetry semantic conventions opt-in
    this.setEnvVar(
      OTEL_SEMCONV_STABILITY_OPT_IN,
      OTEL_SEMCONV_STABILITY_VALUE,
      true,
    );

    // Configure content capture
    this.configureContentCapture(captureContent);

    // Create and configure instrumentor
    const instrumentor = this.createInstrumentor();
    try {
      if (tracerProvider) {
        instrumentor.instrument({ tracerProvider });
      } else {
        instrumentor.instrument();
      }
    } catch (error) {
      this.restoreEnvVars();
      throw error;
    }

    this.instrumentor = instrumentor;
  }

  /**
   * Disable previously configured instrumentation.
   */
  uninstrument(): void {
    if (this.instrumentor === null) {
      return;
    }

    this.instrumentor.disable();
    this.instrumentor = null;
    this.restoreEnvVars();
  }

  /**
   * Set an environment variable and track the original value.
   */
  protected setEnvVar(
    key: string,
    value: string,
    useSetDefault: boolean = false,
  ): void {
    if (!this.originalEnv.has(key)) {
      this.originalEnv.set(key, process.env[key]);
    }

    if (useSetDefault) {
      if (process.env[key] === undefined) {
        process.env[key] = value;
      }
    } else {
      process.env[key] = value;
    }
  }

  /**
   * Restore all environment variables to their original values.
   */
  protected restoreEnvVars(): void {
    for (const [key, value] of this.originalEnv) {
      if (value === undefined) {
        delete process.env[key];
      } else {
        process.env[key] = value;
      }
    }
    this.originalEnv.clear();
  }

  /**
   * Reset singleton instance for testing.
   */
  static resetForTesting(key: string): void {
    const instance = BaseInstrumentation.instances.get(key);
    if (instance) {
      if (instance.instrumentor !== null) {
        instance.instrumentor.disable();
        instance.instrumentor = null;
      }
      instance.restoreEnvVars();
      BaseInstrumentation.instances.delete(key);
    }
  }

  /**
   * Reset all singleton instances for testing.
   */
  static resetAllForTesting(): void {
    for (const key of BaseInstrumentation.instances.keys()) {
      BaseInstrumentation.resetForTesting(key);
    }
  }
}
