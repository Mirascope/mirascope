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
import type { BaseTool, BaseContextTool } from '@/llm/tools/tools';
import type { ToolSchema } from '@/llm/tools/tool-schema';

/**
 * A toolkit for managing and executing regular tools.
 *
 * @example
 * ```typescript
 * const toolkit = new Toolkit([getWeather, searchWeb]);
 *
 * // Execute a tool call from the LLM
 * const output = await toolkit.execute(toolCall);
 * ```
 */
export class Toolkit {
  readonly toolMap: Map<string, BaseTool>;

  /**
   * Create a new Toolkit with the given tools.
   *
   * @param tools - The tools to include in the toolkit.
   */
  constructor(tools: readonly BaseTool[]) {
    this.toolMap = new Map();
    for (const tool of tools) {
      this.toolMap.set(tool.name, tool);
    }
  }

  /**
   * Get all tools in the toolkit.
   */
  get tools(): readonly BaseTool[] {
    return Array.from(this.toolMap.values());
  }

  /**
   * Get the schemas for all tools in the toolkit.
   * Tools ARE schemas (they extend ToolSchema), so we return them directly.
   */
  get schemas(): readonly ToolSchema[] {
    return this.tools;
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
 * @template DepsT - The type of dependencies in the context.
 *
 * @example
 * ```typescript
 * interface MyDeps { db: Database; }
 *
 * const toolkit = new ContextToolkit<MyDeps>([searchDatabase, getUserById]);
 *
 * // Execute with context
 * const ctx = createContext<MyDeps>({ db: myDatabase });
 * const output = await toolkit.execute(ctx, toolCall);
 * ```
 */
export class ContextToolkit<DepsT = unknown> {
  readonly toolMap: Map<string, BaseContextTool<DepsT>>;

  /**
   * Create a new ContextToolkit with the given tools.
   *
   * @param tools - The context tools to include in the toolkit.
   */
  constructor(tools: readonly BaseContextTool<DepsT>[]) {
    this.toolMap = new Map();
    for (const tool of tools) {
      this.toolMap.set(tool.name, tool);
    }
  }

  /**
   * Get all tools in the toolkit.
   */
  get tools(): readonly BaseContextTool<DepsT>[] {
    return Array.from(this.toolMap.values());
  }

  /**
   * Get the schemas for all tools in the toolkit.
   * Tools ARE schemas (they extend ToolSchema), so we return them directly.
   */
  get schemas(): readonly ToolSchema[] {
    return this.tools;
  }

  /**
   * Get a tool by tool call.
   *
   * @param toolCall - The tool call from the LLM.
   * @returns The tool, or undefined if not found.
   */
  get(toolCall: ToolCall): BaseContextTool<DepsT> | undefined {
    return this.toolMap.get(toolCall.name);
  }

  /**
   * Execute a tool call with context.
   *
   * Finds the tool matching the call's name and executes it with the context.
   * Returns a ToolOutput with the result or error.
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

    return tool.execute(ctx, toolCall);
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

/**
 * Create a toolkit from an array of tools.
 *
 * This is a convenience function for creating Toolkit instances.
 *
 * @param tools - The tools to include in the toolkit.
 * @returns A new Toolkit instance.
 */
export function createToolkit(tools: readonly BaseTool[]): Toolkit {
  return new Toolkit(tools);
}

/**
 * Create a context toolkit from an array of context tools.
 *
 * This is a convenience function for creating ContextToolkit instances.
 *
 * @template DepsT - The type of dependencies in the context.
 * @param tools - The context tools to include in the toolkit.
 * @returns A new ContextToolkit instance.
 */
export function createContextToolkit<DepsT = unknown>(
  tools: readonly BaseContextTool<DepsT>[]
): ContextToolkit<DepsT> {
  return new ContextToolkit(tools);
}
