/**
 * Context for LLM calls with dependency injection.
 *
 * Context allows you to pass dependencies (like database connections, user info,
 * configuration, etc.) through to your prompts and tools in a type-safe way.
 */

/**
 * Symbol marker used to identify Context objects at runtime.
 * This enables reliable detection of Context instances in unified call/prompt functions.
 */
export const CONTEXT_MARKER = Symbol("mirascope.Context");

/**
 * Context for LLM calls with dependency injection.
 *
 * @template DepsT - The type of dependencies contained in the context.
 *
 * @example
 * ```typescript
 * interface MyDeps {
 *   userId: string;
 *   db: Database;
 * }
 *
 * const ctx = createContext<MyDeps>({ userId: '123', db: myDb });
 * const response = await myPrompt(model, ctx, { greeting: 'Hello' });
 * ```
 */
export interface Context<DepsT> {
  /**
   * Marker property for runtime Context detection.
   * @internal
   */
  readonly [CONTEXT_MARKER]: true;

  /**
   * The dependencies available in this context.
   */
  readonly deps: DepsT;
}

/**
 * Type guard to check if a value is a Context object.
 *
 * @param value - The value to check.
 * @returns True if the value is a Context, false otherwise.
 *
 * @example
 * ```typescript
 * const maybeCtx = getArgument();
 * if (isContext(maybeCtx)) {
 *   console.log(maybeCtx.deps); // TypeScript knows this is a Context
 * }
 * ```
 */
export function isContext(value: unknown): value is Context<unknown> {
  return value !== null && typeof value === "object" && CONTEXT_MARKER in value;
}

/**
 * Create a context with the given dependencies.
 *
 * @template DepsT - The type of dependencies.
 * @param deps - The dependencies to include in the context.
 * @returns A Context containing the provided dependencies.
 *
 * @example
 * ```typescript
 * interface MyDeps {
 *   userId: string;
 *   db: Database;
 * }
 *
 * const ctx = createContext<MyDeps>({ userId: '123', db: myDb });
 * ```
 */
export function createContext<DepsT>(deps: DepsT): Context<DepsT> {
  return { [CONTEXT_MARKER]: true as const, deps };
}
