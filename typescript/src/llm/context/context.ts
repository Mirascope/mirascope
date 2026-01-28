/**
 * Context for LLM calls with dependency injection.
 *
 * Context allows you to pass dependencies (like database connections, user info,
 * configuration, etc.) through to your prompts and tools in a type-safe way.
 */

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
   * The dependencies available in this context.
   */
  readonly deps: DepsT;
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
  return { deps };
}
