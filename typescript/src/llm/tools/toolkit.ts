/**
 * Toolkit class for managing collections of tools.
 *
 * Provides a unified interface for executing tool calls against
 * a collection of registered tools.
 */

import type { Context } from '@/llm/context';
import { ToolNotFoundError } from '@/llm/exceptions';
import type { ToolCall } from '@/llm/content/tool-call';
import { ToolOutput } from '@/llm/content/tool-output';
import type { Jsonable } from '@/llm/types/jsonable';
import {
  isContextTool,
  type BaseTool,
  type AnyContextTool,
  type Tools,
  type ContextTools,
} from '@/llm/tools/tools';
import type { ToolSchema } from '@/llm/tools/tool-schema';
import { ProviderTool, isProviderTool } from '@/llm/tools/provider-tool';

/**
 * Base interface that all toolkit types implement.
 *
 * This provides a unified interface for accessing tool schemas and looking
 * up tools by name. Matches Python's `BaseToolkit[ToolSchemaT]` pattern.
 *
 * @template T - The type of tools stored in this toolkit.
 */
export interface BaseToolkit<T extends ToolSchema = ToolSchema> {
  /**
   * Get all tools in the toolkit (including provider tools).
   */
  readonly tools: readonly (T | ProviderTool)[];

  /**
   * Get the schemas for all tools in the toolkit.
   * Does NOT include provider tools (they have no schema).
   */
  readonly schemas: readonly ToolSchema[];

  /**
   * Get the provider tools in the toolkit.
   */
  readonly providerTools: readonly ProviderTool[];

  /**
   * Map of tool name to tool for direct access.
   */
  readonly toolMap: Map<string, T>;

  /**
   * Get a tool by tool call.
   *
   * @param toolCall - The tool call from the LLM.
   * @returns The tool, or undefined if not found.
   */
  get(toolCall: ToolCall): T | undefined;
}

// =============================================================================
// Type Aliases for Tool Inputs (matching Python's types.py)
// =============================================================================

/**
 * Type alias for any tools input: either a sequence or a toolkit.
 *
 * This accepts either an array of tools or a pre-built Toolkit,
 * matching Python's `Tools = Sequence[Tool] | Toolkit` pattern.
 */
export type AnyTools = Tools | Toolkit;

/**
 * Type alias for any context tools input: either a sequence or a toolkit.
 *
 * This accepts either an array of tools or a pre-built ContextToolkit,
 * matching Python's `ContextTools[DepsT] = Sequence[...] | ContextToolkit[DepsT]` pattern.
 *
 * @template DepsT - The type of dependencies in the context.
 */
export type AnyContextTools<DepsT = unknown> =
  | ContextTools<DepsT>
  | ContextToolkit<DepsT>;

/**
 * A toolkit for managing and executing regular tools.
 *
 * Implements BaseToolkit<BaseTool> for type-safe tool access.
 *
 * @example
 * ```typescript
 * const toolkit = new Toolkit([getWeather, searchWeb]);
 *
 * // Execute a tool call from the LLM
 * const output = await toolkit.execute(toolCall);
 * ```
 */
export class Toolkit implements BaseToolkit<BaseTool> {
  readonly toolMap: Map<string, BaseTool>;
  private readonly providerToolMap: Map<string, ProviderTool>;
  private readonly _tools: readonly (BaseTool | ProviderTool)[];

  /**
   * Create a new Toolkit with the given tools.
   *
   * @param tools - The tools to include in the toolkit, or null/undefined for empty.
   * @throws Error if multiple tools have the same name.
   */
  constructor(tools: readonly (BaseTool | ProviderTool)[] | null | undefined) {
    this.toolMap = new Map();
    this.providerToolMap = new Map();
    this._tools = tools ?? [];

    for (const tool of this._tools) {
      if (isProviderTool(tool)) {
        if (this.providerToolMap.has(tool.name)) {
          throw new Error(`Multiple provider tools with name: ${tool.name}`);
        }
        this.providerToolMap.set(tool.name, tool);
      } else {
        const baseTool = tool as BaseTool;
        if (this.toolMap.has(baseTool.name)) {
          throw new Error(`Multiple tools with name: ${baseTool.name}`);
        }
        this.toolMap.set(baseTool.name, baseTool);
      }
    }
  }

  /**
   * Get all tools in the toolkit (including provider tools).
   */
  get tools(): readonly (BaseTool | ProviderTool)[] {
    return this._tools;
  }

  /**
   * Get the schemas for all tools in the toolkit.
   * Does NOT include provider tools (they have no schema).
   */
  get schemas(): readonly ToolSchema[] {
    return Array.from(this.toolMap.values());
  }

  /**
   * Get the provider tools in the toolkit.
   */
  get providerTools(): readonly ProviderTool[] {
    return Array.from(this.providerToolMap.values());
  }

  /**
   * Get a tool by tool call.
   *
   * @param toolCall - The tool call from the LLM.
   * @returns The tool, or undefined if not found.
   */
  get(toolCall: ToolCall): BaseTool | undefined {
    return this.toolMap.get(toolCall.name);
  }

  /**
   * Execute a tool call.
   *
   * Finds the tool matching the call's name and executes it.
   * Returns a ToolOutput with the result or error.
   *
   * @param toolCall - The tool call from the LLM.
   * @returns A ToolOutput with the result or error.
   */
  async execute(toolCall: ToolCall): Promise<ToolOutput<Jsonable>> {
    const tool = this.toolMap.get(toolCall.name);

    if (!tool) {
      const error = new ToolNotFoundError(toolCall.name);
      return ToolOutput.failure(toolCall.id, toolCall.name, error);
    }

    return tool.execute(toolCall);
  }
}

/**
 * A toolkit for managing and executing context tools.
 *
 * This toolkit supports BOTH regular tools (BaseTool) AND context tools
 * (BaseContextTool), matching Python's `ContextToolkit[DepsT]` pattern.
 * Regular tools are executed without context; context tools receive the
 * context for dependency injection.
 *
 * Implements BaseToolkit<AnyContextTool<DepsT>> for type-safe tool access.
 *
 * @template DepsT - The type of dependencies in the context.
 *
 * @example
 * ```typescript
 * interface MyDeps { db: Database; }
 *
 * // Can mix regular and context tools
 * const toolkit = new ContextToolkit<MyDeps>([
 *   regularTool,      // BaseTool - no context needed
 *   searchDatabase,   // BaseContextTool<MyDeps> - receives context
 * ]);
 *
 * // Execute with context - polymorphic dispatch handles both types
 * const ctx = createContext<MyDeps>({ db: myDatabase });
 * const output = await toolkit.execute(ctx, toolCall);
 * ```
 */
export class ContextToolkit<DepsT = unknown>
  implements BaseToolkit<AnyContextTool<DepsT>>
{
  readonly toolMap: Map<string, AnyContextTool<DepsT>>;
  private readonly providerToolMap: Map<string, ProviderTool>;
  private readonly _tools: readonly (AnyContextTool<DepsT> | ProviderTool)[];

  /**
   * Create a new ContextToolkit with the given tools.
   *
   * Accepts regular tools (BaseTool), context tools (BaseContextTool), and provider tools.
   *
   * @param tools - The tools to include in the toolkit, or null/undefined for empty.
   * @throws Error if multiple tools have the same name.
   */
  constructor(
    tools: readonly (AnyContextTool<DepsT> | ProviderTool)[] | null | undefined
  ) {
    this.toolMap = new Map();
    this.providerToolMap = new Map();
    this._tools = tools ?? [];

    for (const tool of this._tools) {
      if (isProviderTool(tool)) {
        if (this.providerToolMap.has(tool.name)) {
          throw new Error(`Multiple provider tools with name: ${tool.name}`);
        }
        this.providerToolMap.set(tool.name, tool);
      } else {
        const contextTool = tool as AnyContextTool<DepsT>;
        if (this.toolMap.has(contextTool.name)) {
          throw new Error(`Multiple tools with name: ${contextTool.name}`);
        }
        this.toolMap.set(contextTool.name, contextTool);
      }
    }
  }

  /**
   * Get all tools in the toolkit (including provider tools).
   */
  get tools(): readonly (AnyContextTool<DepsT> | ProviderTool)[] {
    return this._tools;
  }

  /**
   * Get the schemas for all tools in the toolkit.
   * Does NOT include provider tools (they have no schema).
   */
  get schemas(): readonly ToolSchema[] {
    return Array.from(this.toolMap.values());
  }

  /**
   * Get the provider tools in the toolkit.
   */
  get providerTools(): readonly ProviderTool[] {
    return Array.from(this.providerToolMap.values());
  }

  /**
   * Get a tool by tool call.
   *
   * @param toolCall - The tool call from the LLM.
   * @returns The tool, or undefined if not found.
   */
  get(toolCall: ToolCall): AnyContextTool<DepsT> | undefined {
    return this.toolMap.get(toolCall.name);
  }

  /**
   * Execute a tool call with context.
   *
   * Uses polymorphic dispatch to handle both regular tools and context tools:
   * - Regular tools (BaseTool) are executed without context
   * - Context tools (BaseContextTool) receive the context for dependency injection
   *
   * @param ctx - The context containing dependencies.
   * @param toolCall - The tool call from the LLM.
   * @returns A ToolOutput with the result or error.
   */
  async execute(
    ctx: Context<DepsT>,
    toolCall: ToolCall
  ): Promise<ToolOutput<Jsonable>> {
    const tool = this.toolMap.get(toolCall.name);

    if (!tool) {
      const error = new ToolNotFoundError(toolCall.name);
      return ToolOutput.failure(toolCall.id, toolCall.name, error);
    }

    // Polymorphic dispatch based on tool type
    if (isContextTool<DepsT>(tool)) {
      // Context tool - pass context for dependency injection
      return tool.execute(ctx, toolCall);
    } else {
      // Regular tool - execute without context
      return tool.execute(toolCall);
    }
  }

  /**
   * Execute multiple tool calls in parallel with context.
   *
   * @param ctx - The context containing dependencies.
   * @param toolCalls - The tool calls to execute.
   * @returns An array of ToolOutputs in the same order as the input.
   */
  async executeAll(
    ctx: Context<DepsT>,
    toolCalls: readonly ToolCall[]
  ): Promise<ToolOutput<Jsonable>[]> {
    return Promise.all(toolCalls.map((call) => this.execute(ctx, call)));
  }
}

// =============================================================================
// Factory Functions (for direct construction)
// =============================================================================

/**
 * Create a toolkit from an array of tools.
 *
 * This is a convenience function for creating Toolkit instances.
 *
 * @param tools - The tools to include in the toolkit.
 * @returns A new Toolkit instance.
 */
export function createToolkit(
  tools: readonly (BaseTool | ProviderTool)[]
): Toolkit {
  return new Toolkit(tools);
}

/**
 * Create a context toolkit from an array of tools.
 *
 * This is a convenience function for creating ContextToolkit instances.
 * Accepts regular tools (BaseTool), context tools (BaseContextTool), and provider tools.
 *
 * @template DepsT - The type of dependencies in the context.
 * @param tools - The tools to include in the toolkit.
 * @returns A new ContextToolkit instance.
 */
export function createContextToolkit<DepsT = unknown>(
  tools: readonly (AnyContextTool<DepsT> | ProviderTool)[]
): ContextToolkit<DepsT> {
  return new ContextToolkit(tools);
}

// =============================================================================
// Normalization Functions (matching Python's types.py)
// =============================================================================

/**
 * Normalize tools input to a Toolkit.
 *
 * Handles multiple input types:
 * - null/undefined → empty Toolkit
 * - Toolkit → passthrough (returns as-is)
 * - array → wraps in new Toolkit
 *
 * Matches Python's `normalize_tools()` function.
 *
 * @param tools - A sequence of Tools, a Toolkit, or null/undefined.
 * @returns A Toolkit containing the tools (or an empty Toolkit if null/undefined).
 */
export function normalizeTools(tools: AnyTools | null | undefined): Toolkit {
  if (tools == null) {
    return new Toolkit(null);
  }
  if (tools instanceof Toolkit) {
    return tools;
  }
  return new Toolkit(tools);
}

/**
 * Normalize context tools input to a ContextToolkit.
 *
 * Handles multiple input types:
 * - null/undefined → empty ContextToolkit
 * - ContextToolkit → passthrough (returns as-is)
 * - array → wraps in new ContextToolkit
 *
 * Matches Python's `normalize_context_tools()` function.
 *
 * @template DepsT - The type of dependencies in the context.
 * @param tools - A sequence of Tools/ContextTools, a ContextToolkit, or null/undefined.
 * @returns A ContextToolkit containing the tools (or an empty ContextToolkit if null/undefined).
 */
export function normalizeContextTools<DepsT = unknown>(
  tools: AnyContextTools<DepsT> | null | undefined
): ContextToolkit<DepsT> {
  if (tools == null) {
    return new ContextToolkit<DepsT>(null);
  }
  if (tools instanceof ContextToolkit) {
    return tools;
  }
  return new ContextToolkit<DepsT>(tools);
}
