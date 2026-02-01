/**
 * AsyncLocalStorage wrapper for ops context propagation.
 */

import { AsyncLocalStorage } from "async_hooks";

import type { Jsonable } from "@/ops/_internal/types";

/**
 * Context stored in AsyncLocalStorage for ops module.
 */
export interface OpsContext {
  sessionId?: string;
  sessionAttributes?: Record<string, Jsonable>;
}

/**
 * AsyncLocalStorage instance for ops context.
 */
export const opsContextStorage = new AsyncLocalStorage<OpsContext>();

/**
 * Get the current ops context.
 */
export function getCurrentContext(): OpsContext | undefined {
  return opsContextStorage.getStore();
}

/**
 * Run a function with a specific ops context.
 */
export function runWithContext<T>(context: OpsContext, fn: () => T): T {
  return opsContextStorage.run(context, fn);
}
