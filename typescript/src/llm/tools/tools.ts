/**
 * Tool type definitions for LLM function calling.
 *
 * Provides interfaces for tools that can be called by LLMs,
 * including base types for toolkit storage and callable types
 * for direct invocation.
 */

import type { Context } from '@/llm/context';
import type { ToolCall } from '@/llm/content/tool-call';
import type { ToolOutput } from '@/llm/content/tool-output';
import type { Jsonable } from '@/llm/types/jsonable';
import type { ToolSchema } from '@/llm/tools/tool-schema';

/**
 * Field definition can be a string description or a Zod schema.
 *
 * When a string is provided, it's used as the field description.
 * When a Zod schema is provided, description is extracted from `.describe()`
 * and the schema is used for runtime validation.
 */
export type FieldDefinition = string | ZodLike;

/**
 * Duck-typed Zod schema interface for optional Zod support.
 *
 * This allows accepting Zod schemas without requiring Zod as a dependency.
 * We detect Zod schemas at runtime by checking for these properties.
 *
 * Compatible with both Zod 3 (description in _def.description) and
 * Zod 4 (description may be at schema.description or _def.description).
 */
export interface ZodLike {
  /** Internal Zod definition - structure varies by version */
  // Using 'object' instead of Record<string, unknown> for Zod 4 compatibility
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  readonly _def: any;
  /** Description may be at top level in Zod 4 */
  readonly description?: string;
  safeParse(data: unknown): {
    success: boolean;
    data?: unknown;
    error?: unknown;
  };
}

/**
 * Type discriminator for regular tools.
 * Used at runtime to distinguish from context tools.
 */
export const TOOL_TYPE = 'tool' as const;

/**
 * Type discriminator for context tools.
 * Used at runtime to distinguish from regular tools.
 */
export const CONTEXT_TOOL_TYPE = 'context_tool' as const;

/**
 * Base interface for tools without the callable signature.
 *
 * This is used by Toolkit to store tools without variance issues.
 * The callable signature in Tool<T> causes contravariance problems
 * when storing tools with different argument types in a collection.
 */
export interface BaseTool extends ToolSchema {
  /**
   * Type discriminator - always 'tool' for regular tools.
   * Used at runtime to distinguish from context tools.
   */
  readonly __toolType: typeof TOOL_TYPE;

  /**
   * Execute the tool from a ToolCall.
   *
   * @param toolCall - The tool call from the LLM.
   * @returns A ToolOutput with the result or error.
   */
  execute(toolCall: ToolCall): Promise<ToolOutput<Jsonable>>;

  /** The field definitions, if provided. */
  readonly fieldDefinitions:
    | Partial<Record<string, FieldDefinition>>
    | undefined;
}

/**
 * A defined tool that can be called by an LLM.
 *
 * Tools extend ToolSchema (a tool IS a schema) and are callable.
 * Calling a tool directly executes it with the provided arguments.
 *
 * @template T - The type of arguments the tool accepts.
 */
export interface Tool<
  T extends Record<string, unknown> = Record<string, unknown>,
> extends BaseTool {
  /**
   * Call the tool directly with arguments.
   * This is equivalent to Python's `tool.__call__(*args, **kwargs)`.
   *
   * @param args - The arguments to pass to the tool.
   * @returns The tool result.
   */
  (args: T): Promise<Jsonable>;
}

/**
 * Base interface for context tools without the callable signature.
 *
 * This is used by ContextToolkit to store tools without variance issues.
 *
 * @template DepsT - The type of dependencies in the context.
 */
export interface BaseContextTool<DepsT = unknown> extends ToolSchema {
  /**
   * Type discriminator - always 'context_tool' for context tools.
   * Used at runtime to distinguish from regular tools.
   */
  readonly __toolType: typeof CONTEXT_TOOL_TYPE;

  /**
   * Execute the tool from a ToolCall with context.
   *
   * @param ctx - The context containing dependencies.
   * @param toolCall - The tool call from the LLM.
   * @returns A ToolOutput with the result or error.
   */
  execute(
    ctx: Context<DepsT>,
    toolCall: ToolCall
  ): Promise<ToolOutput<Jsonable>>;

  /** The field definitions, if provided. */
  readonly fieldDefinitions:
    | Partial<Record<string, FieldDefinition>>
    | undefined;
}

/**
 * A defined context tool with dependency injection.
 *
 * Context tools extend ToolSchema and are callable with a context argument.
 *
 * @template T - The type of arguments the tool accepts.
 * @template DepsT - The type of dependencies in the context.
 */
export interface ContextTool<
  T extends Record<string, unknown> = Record<string, unknown>,
  DepsT = unknown,
> extends BaseContextTool<DepsT> {
  /**
   * Call the tool directly with context and arguments.
   * This is equivalent to Python's `tool.__call__(ctx, *args, **kwargs)`.
   *
   * @param ctx - The context containing dependencies.
   * @param args - The arguments to pass to the tool.
   * @returns The tool result.
   */
  (ctx: Context<DepsT>, args: T): Promise<Jsonable>;
}

/**
 * Union type for any tool (regular or context).
 */
export type AnyTool = Tool | ContextTool;

/**
 * Union type for tools that can be used in context paths.
 *
 * Context paths accept BOTH regular tools AND context tools,
 * matching Python's `ContextTools[DepsT] = Tool | ContextTool[DepsT]`.
 *
 * @template DepsT - The type of dependencies in the context.
 */
export type AnyContextTool<DepsT = unknown> = BaseTool | BaseContextTool<DepsT>;

/**
 * Type alias for any tool schema.
 *
 * This is used as a type bound in generic toolkit storage.
 * Matches Python's `AnyToolSchema = ToolSchema[AnyToolFn]`.
 */
export type AnyToolSchema = BaseTool | BaseContextTool;

// =============================================================================
// Array Type Aliases (matching Python's Sequence types)
// =============================================================================

/**
 * Type alias for an array of regular tools.
 * Matches Python's `Tools = Sequence[Tool]`.
 */
export type Tools = readonly BaseTool[];

/**
 * Type alias for an array of tools usable in context paths.
 * Accepts both regular tools AND context tools.
 * Matches Python's `ContextTools[DepsT] = Sequence[Tool | ContextTool[DepsT]]`.
 *
 * @template DepsT - The type of dependencies in the context.
 */
export type ContextTools<DepsT = unknown> = readonly AnyContextTool<DepsT>[];

// =============================================================================
// Type Guards
// =============================================================================

/**
 * Type guard to check if a tool is a context tool.
 *
 * @param tool - The tool to check.
 * @returns True if the tool is a context tool.
 */
export function isContextTool<DepsT = unknown>(
  tool: AnyContextTool<DepsT>
): tool is BaseContextTool<DepsT> {
  return tool.__toolType === CONTEXT_TOOL_TYPE;
}
