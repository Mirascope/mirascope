/**
 * Model context management for runtime model switching.
 *
 * This module provides a way to set a model context that overrides
 * the default model in `defineCall` and `definePrompt`, similar to
 * Python's `with llm.model(...):` context manager.
 *
 * ## Cross-Platform Implementation
 *
 * - **Node.js**: Uses native `AsyncLocalStorage` from `async_hooks` for proper
 *   async context propagation. This handles concurrent async operations correctly.
 *
 * - **Browser**: Uses a stack-based fallback. This works correctly for:
 *   - Synchronous code
 *   - Sequential async/await chains
 *   - Nested `withModel` calls (as long as they are sequential)
 *
 * ## Browser Limitations
 *
 * The browser fallback has a known limitation with **concurrent** async operations:
 *
 * ```typescript
 * // WARNING: In browsers, this may have unexpected behavior:
 * await Promise.all([
 *   llm.withModel(modelA, async () => { await call(); }), // May see modelB!
 *   llm.withModel(modelB, async () => { await call(); }), // May see modelA!
 * ]);
 * ```
 *
 * This is because the browser lacks a native async context mechanism. The stack
 * can become interleaved when multiple async operations run concurrently.
 *
 * ## Future: TC39 AsyncContext Proposal
 *
 * The TC39 "Async Context" proposal (https://github.com/tc39/proposal-async-context)
 * aims to bring `AsyncLocalStorage`-like functionality to all JavaScript environments.
 * Once this proposal is standardized and widely supported, we can update the browser
 * implementation to use native async context, eliminating the concurrent operation
 * limitation.
 *
 * @see https://github.com/tc39/proposal-async-context
 *
 * @example
 * ```typescript
 * const call = llm.defineCall({
 *   model: llm.model("openai/gpt-4o"),
 *   template: () => "Hello"
 * });
 *
 * // Without context - uses default model
 * await call();
 *
 * // With context - overrides default
 * await llm.withModel(llm.model("anthropic/claude-sonnet-4-0"), async () => {
 *   await call(); // Uses Claude
 * });
 * ```
 */

import type { Params } from '@/llm/models/params';
import type { ModelId } from '@/llm/providers/model-id';
import { Model } from '@/llm/models/model';

/**
 * Cross-platform context storage interface.
 * Abstracts over Node.js AsyncLocalStorage and browser fallback.
 * @internal Exported for testing purposes only
 */
export interface ContextStorage<T> {
  get(): T | undefined;
  run<R>(value: T, fn: () => R): R;
}

/**
 * Node.js implementation using AsyncLocalStorage.
 * Provides proper async context propagation across async/await boundaries.
 */
function createNodeStorage<T>(): ContextStorage<T> {
  // Dynamic require to avoid issues in browser bundlers
  // eslint-disable-next-line @typescript-eslint/no-require-imports
  const { AsyncLocalStorage } = require('node:async_hooks') as {
    AsyncLocalStorage: new <T>() => {
      getStore(): T | undefined;
      run<R>(store: T, callback: () => R): R;
    };
  };
  const storage = new AsyncLocalStorage<T>();
  return {
    get: () => storage.getStore(),
    run: <R>(value: T, fn: () => R): R => storage.run(value, fn),
  };
}

/**
 * Browser fallback using a stack.
 *
 * **Limitations**: This implementation works correctly for sequential async operations
 * but does NOT properly isolate concurrent async operations. When multiple `withModel`
 * calls run in parallel via `Promise.all`, their contexts may become interleaved.
 *
 * This is a fundamental limitation of any JavaScript-based solution without native
 * async context support. The TC39 AsyncContext proposal will solve this when available.
 *
 * @see https://github.com/tc39/proposal-async-context
 * @internal Exported for testing purposes only
 */
export function createBrowserStorage<T>(): ContextStorage<T> {
  const stack: T[] = [];
  return {
    get: () => stack[stack.length - 1],
    run: <R>(value: T, fn: () => R): R => {
      stack.push(value);
      try {
        const result = fn();
        // Handle promises to ensure cleanup after async completion
        if (result instanceof Promise) {
          return result.finally(() => {
            stack.pop();
          }) as R;
        }
        stack.pop();
        return result;
      } catch (e) {
        stack.pop();
        throw e;
      }
    },
  };
}

/**
 * Auto-detect environment and create appropriate storage.
 * @internal Exported for testing purposes only
 */
export function createStorage<T>(): ContextStorage<T> {
  try {
    return createNodeStorage<T>();
    /* v8 ignore start - browser fallback only hit when AsyncLocalStorage unavailable */
  } catch {
    // This branch is only hit in browser environments where AsyncLocalStorage
    // is unavailable. Since tests run in Node.js, this is tested indirectly
    // through createBrowserStorage tests.
    return createBrowserStorage<T>();
  }
  /* v8 ignore stop */
}

// Initialize the model storage
const modelStorage = createStorage<Model>();

/**
 * Get the model currently set via context, if any.
 *
 * @returns The current context model, or undefined if none is set.
 *
 * @example
 * ```typescript
 * await llm.withModel(llm.model("anthropic/claude-sonnet-4-0"), async () => {
 *   const model = llm.modelFromContext();
 *   console.log(model?.modelId); // "anthropic/claude-sonnet-4-0"
 * });
 *
 * const outsideModel = llm.modelFromContext(); // undefined
 * ```
 */
export function modelFromContext(): Model | undefined {
  return modelStorage.get();
}

/**
 * Execute a function with a model set in context.
 *
 * All calls to `defineCall` and `definePrompt` within the callback
 * will use the context model instead of their default model.
 *
 * @param model - The model to set in context.
 * @param fn - The function to execute with the model in context.
 * @returns The return value of the function.
 *
 * @example Basic usage
 * ```typescript
 * const response = await llm.withModel(llm.model("openai/gpt-4o"), async () => {
 *   return await call();
 * });
 * ```
 *
 * @example Nested contexts
 * ```typescript
 * await llm.withModel(llm.model("anthropic/claude-sonnet-4-0"), async () => {
 *   const model1 = llm.modelFromContext(); // Claude
 *
 *   await llm.withModel(llm.model("openai/gpt-4o"), async () => {
 *     const model2 = llm.modelFromContext(); // GPT-4o
 *   });
 *
 *   const model3 = llm.modelFromContext(); // Claude (restored)
 * });
 * ```
 */
export function withModel<T>(model: Model, fn: () => T): T {
  return modelStorage.run(model, fn);
}

/**
 * Get the model from context if available, otherwise use the provided model.
 *
 * This function implements the fallback pattern:
 * 1. If a model is set in context, return it (context takes precedence)
 * 2. Otherwise, if a Model instance is provided, return it
 * 3. Otherwise, if a string model ID is provided, create a new Model
 *
 * @param modelOrId - A Model instance or model ID string.
 * @param params - Optional parameters when creating a new Model from string ID.
 * @returns The resolved Model instance.
 *
 * @example
 * ```typescript
 * // Outside context - returns the provided model
 * const model1 = llm.useModel("openai/gpt-4o"); // Creates new Model
 *
 * // Inside context - returns context model
 * await llm.withModel(llm.model("anthropic/claude-sonnet-4-0"), async () => {
 *   const model2 = llm.useModel("openai/gpt-4o"); // Returns Claude model
 * });
 * ```
 */
export function useModel(model: Model | ModelId, params?: Params): Model {
  const contextModel = modelFromContext();
  if (contextModel !== undefined) {
    return contextModel;
  }
  if (typeof model === 'string') {
    return new Model(model, params);
  }
  return model;
}
