/**
 * Utility functions for the Mirascope ops module.
 */

import type { Jsonable } from "@/ops/_internal/types";

/**
 * Safely serialize a value to JSON string.
 *
 * Handles circular references and non-serializable values by returning
 * a string representation instead of throwing.
 *
 * @param value - The value to serialize.
 * @returns JSON string representation of the value.
 */
export function jsonStringify(value: unknown): string {
  try {
    return JSON.stringify(value);
  } catch {
    return String(value);
  }
}

/**
 * Convert a value to a Jsonable type if possible.
 *
 * @param value - The value to convert.
 * @returns The value as Jsonable, or its string representation if not serializable.
 */
export function toJsonable(value: unknown): Jsonable {
  if (value === null) return null;
  if (typeof value === "string") return value;
  if (typeof value === "number") return value;
  if (typeof value === "boolean") return value;
  if (Array.isArray(value)) {
    return value.map(toJsonable);
  }
  if (typeof value === "object") {
    const result: Record<string, Jsonable> = {};
    for (const [key, val] of Object.entries(value)) {
      result[key] = toJsonable(val);
    }
    return result;
  }
  return String(value);
}

/**
 * Get the qualified name of a function.
 *
 * Returns the function name if available, otherwise "anonymous".
 *
 * @param fn - The function to get the name of.
 * @returns The qualified name of the function.
 */
/**
 * Interface for callable objects with optional name property.
 * Equivalent to Python's Protocol with __call__.
 */
export interface NamedCallable {
  readonly name?: string;
  (...args: never[]): unknown;
}

export function getQualifiedName(fn: NamedCallable): string {
  return fn.name || "anonymous";
}

/**
 * Extract argument types and values from a function call.
 *
 * @param fn - The function being called.
 * @param args - The arguments passed to the function.
 * @returns Object containing argument types and values.
 */
export function extractArguments(
  fn: NamedCallable,
  args: unknown[],
): { argTypes: string[]; argValues: Jsonable[] } {
  const argTypes: string[] = [];
  const argValues: Jsonable[] = [];

  // Try to extract parameter names from function signature
  const fnStr = fn.toString();
  const paramMatch = fnStr.match(/\(([^)]*)\)/);
  const paramNames: string[] = [];

  const paramString = paramMatch?.[1];
  if (paramString) {
    // Parse parameter names (handles destructuring, defaults, types)
    const params = paramString.split(",").map((p) => p.trim());
    for (const param of params) {
      if (!param) continue;
      // Extract just the parameter name (before : or = or destructuring)
      const nameMatch = param.match(/^(\w+)/);
      if (nameMatch?.[1]) {
        paramNames.push(nameMatch[1]);
      }
    }
  }

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    const argType = typeof arg;

    // Use parameter name if available, otherwise use index
    const paramName = paramNames[i] ?? `arg${i}`;
    argTypes.push(`${paramName}: ${argType}`);
    argValues.push(toJsonable(arg));
  }

  return { argTypes, argValues };
}
