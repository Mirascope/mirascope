/**
 * Versioning wrapper for Call objects.
 *
 * Provides the versionCall() function for wrapping calls with
 * closure-based versioning and tracing instrumentation.
 */

import { context as otelContext, trace as otelTrace } from "@opentelemetry/api";
import { createHash } from "crypto";

import type { VersionOptions } from "@/ops/_internal/types";

import { getClient } from "@/api/client";
import { Span } from "@/ops/_internal/spans";
import { createTracedCallSpan } from "@/ops/_internal/traced-calls";
import { jsonStringify } from "@/ops/_internal/utils";
import {
  computeVersion,
  createVersionedResult,
  type ClosureMetadata,
  type VersionInfo,
  type VersionedResult,
} from "@/ops/_internal/versioned-functions";

/**
 * Extended options that includes injected closure metadata from compile-time transform.
 */
interface VersionOptionsWithClosure extends VersionOptions {
  __closure?: ClosureMetadata;
}

/**
 * A versioned call with access to version info and wrapped result.
 *
 * Call normally to get the response directly.
 * Call `.wrapped()` to get the full VersionedResult object with span metadata.
 * Access `.versionInfo` to get information about the call's version.
 */
export interface VersionedCall<CallT> {
  /** Execute the call and return the response directly */
  (...args: unknown[]): Promise<unknown>;
  /** Execute the call and return the full VersionedResult object */
  wrapped(...args: unknown[]): Promise<VersionedResult<unknown>>;
  /** Stream the call and return the stream response directly */
  stream(...args: unknown[]): Promise<unknown>;
  /** Stream the call and return the full VersionedResult object with stream response */
  wrappedStream(...args: unknown[]): Promise<VersionedResult<unknown>>;
  /** The underlying call */
  readonly call: CallT;
  /** Information about the call's version */
  readonly versionInfo: VersionInfo;
}

/**
 * Minimal interface for a Call-like object.
 */
export interface CallLike {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  call(...args: any[]): Promise<unknown>;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  stream(...args: any[]): Promise<unknown>;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  template: ((...args: any[]) => unknown) & { name?: string };
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  prompt: { template: ((...args: any[]) => unknown) & { name?: string } };
}

/**
 * Extract function signature from function's toString() representation.
 *
 * Handles patterns like:
 * - function name(params) { ... }
 * - function (params) { ... }
 * - (params) => ...
 * - async function name(params) { ... }
 * - async (params) => ...
 *
 * @internal Exported for testing only.
 */
export function extractSignatureFromString(fnStr: string): string {
  // Normalize whitespace
  const normalized = fnStr.replace(/\s+/g, " ").trim();

  // Try to match arrow function: (params) => or async (params) =>
  const arrowMatch = normalized.match(
    /^(?:async\s+)?\(([^)]*)\)\s*(?::\s*[^=]+)?\s*=>/,
  );
  if (arrowMatch) {
    return `(${arrowMatch[1]})`;
  }

  // Try to match function declaration: function name(params) or function(params)
  const funcMatch = normalized.match(
    /^(?:async\s+)?function\s*\w*\s*\(([^)]*)\)/,
  );
  if (funcMatch) {
    return `(${funcMatch[1]})`;
  }

  /* v8 ignore next 10 - method match and fallback are defensive, JS toString() always matches above patterns */
  // Try to match method syntax: name(params)
  const methodMatch = normalized.match(/^\w+\s*\(([^)]*)\)/);
  if (methodMatch) {
    return `(${methodMatch[1]})`;
  }

  // Fallback
  return "(...)";
}

/**
 * Runtime fallback for closure computation when transform plugin is not used.
 */
function computeRuntimeClosure(call: CallLike): ClosureMetadata {
  // Use the template function's string representation
  const code = call.template.toString();
  const hash = createHash("sha256").update(code).digest("hex");
  const signature = extractSignatureFromString(code);
  const signatureHash = createHash("sha256").update(signature).digest("hex");
  return { code, hash, signature, signatureHash };
}

/**
 * Create a span for a versioned call invocation.
 *
 * Reuses createTracedCallSpan to get all trace attributes (call.name,
 * call.variables, trace.tags, trace.metadata), then adds version-specific
 * attributes on top.
 */
function createVersionedCallSpan(
  callName: string,
  options: VersionOptions,
  closure: ClosureMetadata,
  functionUuid: string | undefined,
  vars: unknown,
): Span {
  // Create span with all trace attributes
  const span = createTracedCallSpan(callName, options, vars);

  span.set({
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
 * Wrap a Call with versioning and tracing instrumentation.
 *
 * @param call - The call to version
 * @param options - Optional version options (name, tags, metadata)
 * @returns A versioned call with versionInfo property
 *
 * @example
 * ```typescript
 * const recommendBook = defineCall({
 *   model: 'anthropic/claude-sonnet-4-20250514',
 *   template: ({ genre }: { genre: string }) => `Recommend a ${genre} book`,
 * });
 *
 * const versionedCall = versionCall(recommendBook, {
 *   name: 'recommend-book-v1',
 *   tags: ['production']
 * });
 *
 * console.log(versionedCall.versionInfo.hash);
 * const response = await versionedCall({ genre: 'fantasy' });
 * ```
 */
export function versionCall<CallT extends CallLike>(
  call: CallT,
  options?: VersionOptionsWithClosure,
): VersionedCall<CallT>;

/**
 * Create a versioning wrapper with options (curried form).
 *
 * @param options - Version options (name, tags, metadata)
 * @returns A function that accepts the call to version
 */
export function versionCall(
  options: VersionOptionsWithClosure,
): <CallT extends CallLike>(call: CallT) => VersionedCall<CallT>;

export function versionCall<CallT extends CallLike>(
  callOrOptions: CallT | VersionOptionsWithClosure,
  maybeOptions?: VersionOptionsWithClosure,
): VersionedCall<CallT> | (<C extends CallLike>(call: C) => VersionedCall<C>) {
  // Curried form
  if (!isCallLike(callOrOptions)) {
    const options = callOrOptions;
    return <C extends CallLike>(c: C) => versionCall(c, options);
  }

  const call = callOrOptions;
  const options = maybeOptions ?? {};
  const tags = [...new Set(options.tags ?? [])].sort();
  const metadata = options.metadata ?? {};

  // Get a name for the call (use || to handle empty strings)
  /* v8 ignore start - name fallback chain branches are difficult to test exhaustively */
  const callName =
    options.name ||
    call.template.name ||
    (call as { name?: string }).name ||
    call.prompt.template.name ||
    "call";
  /* v8 ignore end */

  // Use injected closure from compile-time transform, or fall back to runtime
  let closure: ClosureMetadata;
  if (options.__closure) {
    closure = options.__closure;
  } else {
    closure = computeRuntimeClosure(call);
  }

  const versionInfo: VersionInfo = {
    uuid: undefined,
    hash: closure.hash,
    signatureHash: closure.signatureHash,
    name: callName,
    description: undefined, // Docstring extraction not yet supported in TypeScript
    version: computeVersion(closure.hash),
    tags,
    metadata,
  };

  let registeredUuid: string | undefined;
  let registrationAttempted = false;

  /**
   * Attempt to register the function with Mirascope Cloud.
   */
  async function ensureRegistration(): Promise<string | undefined> {
    /* v8 ignore start - caching branches for multiple invocations */
    if (registeredUuid) return registeredUuid;
    if (registrationAttempted) return undefined;
    /* v8 ignore end */

    registrationAttempted = true;

    try {
      const client = getClient();

      try {
        const existing = await client.functions.findbyhash({
          hash: closure.hash,
        });
        registeredUuid = existing.id;
        return registeredUuid;
      } catch {
        // Not found, create new
      }

      const response = await client.functions.create({
        code: closure.code,
        hash: closure.hash,
        signature: closure.signature,
        signatureHash: closure.signatureHash,
        name: callName,
        language: "typescript",
        tags: tags.length > 0 ? tags : undefined,
        metadata: Object.keys(metadata).length > 0 ? metadata : undefined,
      });

      registeredUuid = response.id;
      return registeredUuid;
    } catch {
      return undefined;
    }
  }

  const versioned = async (...args: unknown[]): Promise<unknown> => {
    const vars = args[0];
    const functionUuid = await ensureRegistration();
    const span = createVersionedCallSpan(
      callName,
      options,
      closure,
      functionUuid,
      vars,
    );

    const otelSpan = span.otelSpan;
    /* v8 ignore start */
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

  versioned.wrapped = async (
    ...args: unknown[]
  ): Promise<VersionedResult<unknown>> => {
    const vars = args[0];
    const functionUuid = await ensureRegistration();
    const span = createVersionedCallSpan(
      callName,
      options,
      closure,
      functionUuid,
      vars,
    );

    const otelSpan = span.otelSpan;
    /* v8 ignore start */
    const runInContext = otelSpan
      ? () =>
          otelContext.with(
            otelTrace.setSpan(otelContext.active(), otelSpan),
            execute,
          )
      : execute;
    /* v8 ignore end */

    async function execute(): Promise<VersionedResult<unknown>> {
      try {
        const response = await call.call(...args);
        return createVersionedResult(response, span, functionUuid);
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

  versioned.stream = async (...args: unknown[]): Promise<unknown> => {
    const vars = args[0];
    const functionUuid = await ensureRegistration();
    const span = createVersionedCallSpan(
      callName,
      options,
      closure,
      functionUuid,
      vars,
    );

    const otelSpan = span.otelSpan;
    /* v8 ignore start */
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

  versioned.wrappedStream = async (
    ...args: unknown[]
  ): Promise<VersionedResult<unknown>> => {
    const vars = args[0];
    const functionUuid = await ensureRegistration();
    const span = createVersionedCallSpan(
      callName,
      options,
      closure,
      functionUuid,
      vars,
    );

    const otelSpan = span.otelSpan;
    /* v8 ignore start */
    const runInContext = otelSpan
      ? () =>
          otelContext.with(
            otelTrace.setSpan(otelContext.active(), otelSpan),
            execute,
          )
      : execute;
    /* v8 ignore end */

    async function execute(): Promise<VersionedResult<unknown>> {
      try {
        const response = await call.stream(...args);
        return createVersionedResult(response, span, functionUuid);
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

  Object.defineProperty(versioned, "call", {
    value: call,
    enumerable: true,
  });

  Object.defineProperty(versioned, "versionInfo", {
    value: versionInfo,
    enumerable: true,
    writable: false,
  });

  return versioned as VersionedCall<CallT>;
}

/**
 * Type guard to check if a value is a Call-like object.
 */
export function isCallLike(value: unknown): value is CallLike {
  return (
    typeof value === "function" &&
    "call" in value &&
    "stream" in value &&
    "prompt" in value
  );
}
