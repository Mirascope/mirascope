/**
 * Formatting types for structured LLM outputs.
 *
 * Provides types for defining structured output formats that LLMs
 * should follow when generating responses.
 */

import type { ToolParameterSchema, ZodLike } from "@/llm/tools";

/**
 * Formatting mode determines how the structured output is requested from the LLM.
 *
 * - `strict`: Use provider's strict structured output mode (requires provider support)
 * - `json`: Use JSON mode with schema instructions in system prompt
 * - `tool`: Use tool calling with a format tool to get structured output
 * - `parser`: Use custom OutputParser for non-JSON formats
 */
export type FormattingMode = "strict" | "json" | "tool" | "parser";

/**
 * User-facing format specification.
 *
 * Can be one of:
 * - A TypeScript interface/type (transformer injects __schema)
 * - A Zod schema (used for both schema and validation)
 * - { schema: T, validator: ZodSchema } for explicit control
 * - Format (from defineFormat)
 * - OutputParser (from defineOutputParser)
 *
 * @template T - The type of the formatted output.
 */
export interface FormatSpec<T = unknown> {
  /**
   * The schema marker for the TypeScript type.
   * The compile-time transformer uses this to determine which type to extract schema from.
   */
  schema?: T;

  /**
   * Optional Zod schema for runtime validation.
   * When provided, parsed output will be validated against this schema.
   */
  validator?: ZodLike;

  /**
   * Internal: JSON schema injected by the compile-time transformer.
   * Users should not set this directly.
   */
  __schema?: ToolParameterSchema;
}

/**
 * Check if a value is a Zod-like schema.
 *
 * @param value - The value to check.
 * @returns True if the value has Zod-like properties.
 */
export function isZodSchema(value: unknown): value is ZodLike {
  return (
    typeof value === "object" &&
    value !== null &&
    "_def" in value &&
    typeof (value as ZodLike).safeParse === "function"
  );
}

/**
 * Check if a value is a FormatSpec object.
 *
 * @param value - The value to check.
 * @returns True if the value is a FormatSpec object.
 */
export function isFormatSpec(value: unknown): value is FormatSpec {
  if (typeof value !== "object" || value === null) return false;

  // FormatSpec has optional schema, validator, or __schema
  const obj = value as Record<string, unknown>;
  return (
    "__schema" in obj ||
    "validator" in obj ||
    ("schema" in obj && !("__formatType" in obj))
  );
}

// Import Format and OutputParser types for ExtractFormatType
// These are imported lazily to avoid circular dependencies
import type { Format } from "@/llm/formatting/format";
import type { OutputParser } from "@/llm/formatting/output-parser";

/**
 * Any format input that can be provided to defineCall/definePrompt.
 * Used for constraining format type parameters.
 *
 * @template F - The output type of the format. Defaults to unknown.
 */
export type FormatInput<F = unknown> =
  | Format<F>
  | FormatSpec<F>
  | OutputParser<F>
  | ZodLike
  | null
  | undefined;

/**
 * Union of all possible format input types (non-generic version).
 * Used for type narrowing in resolveFormat.
 */
export type AnyFormatInput =
  | Format<unknown>
  | FormatSpec<unknown>
  | OutputParser<unknown>
  | ZodLike
  | null
  | undefined;

/**
 * Extract the format output type from a format input.
 *
 * This utility type enables automatic type inference when using formats
 * with defineCall and definePrompt, eliminating the need to specify the
 * format type parameter explicitly.
 *
 * @template F - The format input type.
 * @returns The extracted output type, or `unknown` if not determinable.
 *
 * @example
 * ```typescript
 * // ExtractFormatType<Format<Book>> = Book
 * // ExtractFormatType<OutputParser<Recipe>> = Recipe
 * // ExtractFormatType<typeof BookSchema> = z.infer<typeof BookSchema>
 * // ExtractFormatType<null> = unknown
 * ```
 */
export type ExtractFormatType<F> =
  // Format<F> -> F
  F extends Format<infer F>
    ? F
    : // OutputParser<F> -> F
      F extends OutputParser<infer F>
      ? F
      : // FormatSpec<F> -> F
        F extends FormatSpec<infer F>
        ? F
        : // Zod schema - infer from _output type (used by z.infer)
          F extends { _output: infer O }
          ? O
          : // null/undefined -> unknown
            F extends null | undefined
            ? unknown
            : // Fallback
              unknown;
