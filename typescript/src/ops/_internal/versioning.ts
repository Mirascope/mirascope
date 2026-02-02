/**
 * Versioning wrapper for functions.
 *
 * Provides the version() function for wrapping async functions with
 * closure-based versioning and tracing instrumentation.
 */

import { context as otelContext, trace as otelTrace } from "@opentelemetry/api";
import { createHash } from "crypto";

import type { VersionOptions } from "@/ops/_internal/types";

import { Span } from "@/ops/_internal/spans";
import {
  createVersionedResult,
  type ClosureMetadata,
  type VersionInfo,
  type VersionedFunction,
  type VersionedResult,
} from "@/ops/_internal/versioned-functions";

// Re-export VersionedFunction for convenience
export type { VersionedFunction } from "@/ops/_internal/versioned-functions";
import { getClient } from "@/api/client";
import { jsonStringify, type NamedCallable } from "@/ops/_internal/utils";

/**
 * Extended options that includes injected closure metadata from compile-time transform.
 */
interface VersionOptionsWithClosure extends VersionOptions {
  __closure?: ClosureMetadata;
}

/**
 * Runtime fallback for closure computation when transform plugin is not used.
 * WARNING: This uses fn.toString() which gives compiled JS, not original TS.
 */
function computeRuntimeClosure(fn: NamedCallable): ClosureMetadata {
  const code = fn.toString();
  const hash = createHash("sha256").update(code).digest("hex");
  // Can't reliably extract TS signature at runtime
  const signature = "(...)";
  const signatureHash = createHash("sha256").update(signature).digest("hex");
  return { code, hash, signature, signatureHash };
}

/**
 * Create a span for a versioned function invocation.
 */
function createVersionedSpan(
  fn: NamedCallable,
  options: VersionOptions,
  closure: ClosureMetadata,
  functionUuid: string | undefined,
): Span {
  /* v8 ignore next - name fallback chain branches */
  const name = options.name || fn.name || "anonymous";
  const span = new Span(name);
  span.start();

  span.set({
    "mirascope.type": "version",
    "mirascope.version.hash": closure.hash,
    "mirascope.version.signature_hash": closure.signatureHash,
  });

  if (functionUuid) {
    span.set({ "mirascope.version.uuid": functionUuid });
  }

  if (options.name) {
    span.set({ "mirascope.version.name": options.name });
  }

  if (options.tags && options.tags.length > 0) {
    span.set({ "mirascope.version.tags": options.tags });
  }

  if (options.metadata && Object.keys(options.metadata).length > 0) {
    span.set({ "mirascope.version.metadata": jsonStringify(options.metadata) });
  }

  return span;
}

/**
 * Wrap a function with versioning and tracing instrumentation.
 *
 * The version() wrapper tracks function versions using closure hashing.
 * When used with the compile-time transform plugin, it captures the
 * original TypeScript source. Without the transform, it falls back to
 * runtime fn.toString() (which only captures compiled JS).
 *
 * @param fn - The async function to version
 * @param options - Optional version options (name, tags, metadata)
 * @returns A versioned function with versionInfo property
 *
 * @example Direct form
 * ```typescript
 * const computeEmbedding = version(async (text: string) => {
 *   return [0.1, 0.2, 0.3];
 * });
 * console.log(computeEmbedding.versionInfo.hash);
 * ```
 *
 * @example With options
 * ```typescript
 * const computeEmbedding = version(
 *   async (text: string) => [0.1, 0.2, 0.3],
 *   { name: 'embedding-v1', tags: ['production'] }
 * );
 * ```
 *
 * @example Accessing wrapped result
 * ```typescript
 * const result = await computeEmbedding.wrapped("hello");
 * console.log(result.functionUuid); // UUID from Mirascope Cloud
 * await result.annotate({ label: 'pass' });
 * ```
 */
export function version<Args extends unknown[], R>(
  fn: (...args: Args) => Promise<R>,
  options?: VersionOptionsWithClosure,
): VersionedFunction<Args, R>;

/**
 * Create a versioning wrapper with options (curried form).
 *
 * @param options - Version options (name, tags, metadata)
 * @returns A function that accepts the function to version
 *
 * @example
 * ```typescript
 * const withVersion = version({ name: 'my-fn', tags: ['v1'] });
 * const versionedFn = withVersion(async (x: number) => x * 2);
 * ```
 */
export function version(
  options: VersionOptionsWithClosure,
): <Args extends unknown[], R>(
  fn: (...args: Args) => Promise<R>,
) => VersionedFunction<Args, R>;

export function version<Args extends unknown[], R>(
  fnOrOptions: ((...args: Args) => Promise<R>) | VersionOptionsWithClosure,
  maybeOptions?: VersionOptionsWithClosure,
):
  | VersionedFunction<Args, R>
  | (<A extends unknown[], T>(
      fn: (...args: A) => Promise<T>,
    ) => VersionedFunction<A, T>) {
  // Curried form: version(options)(fn)
  if (typeof fnOrOptions !== "function") {
    const options = fnOrOptions;
    return <A extends unknown[], T>(fn: (...args: A) => Promise<T>) =>
      version(fn, options);
  }

  const fn = fnOrOptions;
  const options = maybeOptions ?? {};
  const tags = [...new Set(options.tags ?? [])].sort();
  const metadata = options.metadata ?? {};

  // Use injected closure from compile-time transform, or fall back to runtime
  let closure: ClosureMetadata;
  if (options.__closure) {
    // Compile-time transform ran - use injected metadata
    closure = options.__closure;
  } else {
    // Transform didn't run - use runtime fallback
    // Note: This is expected when running without the build plugin
    closure = computeRuntimeClosure(fn);
  }

  const versionInfo: VersionInfo = {
    uuid: undefined,
    hash: closure.hash,
    signatureHash: closure.signatureHash,
    /* v8 ignore next - name fallback chain branches */
    name: options.name || fn.name || "anonymous",
    tags,
    metadata,
  };

  let registeredUuid: string | undefined;
  let registrationAttempted = false;

  /**
   * Attempt to register the function with Mirascope Cloud.
   * Returns the function UUID if successful, undefined otherwise.
   */
  async function ensureRegistration(): Promise<string | undefined> {
    /* v8 ignore start - caching branches for multiple invocations */
    if (registeredUuid) return registeredUuid;
    if (registrationAttempted) return undefined;
    /* v8 ignore end */

    registrationAttempted = true;

    try {
      const client = getClient();

      // Try to find existing function by hash
      try {
        const existing = await client.functions.findbyhash({
          hash: closure.hash,
        });
        registeredUuid = existing.id;
        return registeredUuid;
      } catch {
        // Not found, create new
      }

      // Register new function
      const response = await client.functions.create({
        code: closure.code,
        hash: closure.hash,
        signature: closure.signature,
        signatureHash: closure.signatureHash,
        /* v8 ignore next - name fallback chain branches */
        name: options.name || fn.name || "anonymous",
        tags: tags.length > 0 ? tags : undefined,
        metadata: Object.keys(metadata).length > 0 ? metadata : undefined,
      });

      registeredUuid = response.id;
      return registeredUuid;
    } catch {
      // Registration failed - continue without UUID
      // This is expected when running without API key or offline
      return undefined;
    }
  }

  const versioned = async (...args: Args): Promise<R> => {
    const functionUuid = await ensureRegistration();
    const span = createVersionedSpan(fn, options, closure, functionUuid);

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
        return result;
      } catch (error) {
        if (error instanceof Error) {
          span.error(error.message);
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

  versioned.wrapped = async (...args: Args): Promise<VersionedResult<R>> => {
    const functionUuid = await ensureRegistration();
    const span = createVersionedSpan(fn, options, closure, functionUuid);

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

    async function execute(): Promise<VersionedResult<R>> {
      try {
        const result = await fn(...args);
        return createVersionedResult(result, span, functionUuid);
      } catch (error) {
        if (error instanceof Error) {
          span.error(error.message);
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

  Object.defineProperty(versioned, "versionInfo", {
    value: versionInfo,
    enumerable: true,
    writable: false,
  });

  return versioned as VersionedFunction<Args, R>;
}
