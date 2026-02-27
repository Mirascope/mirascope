/**
 * Tool definition functions for creating LLM-callable tools.
 *
 * Provides `defineTool()` and `defineContextTool()` for creating tools
 * with type-safe argument inference.
 *
 * Two patterns are supported:
 * 1. **Zod-native**: Use `validator` option with a Zod schema (no transformer needed)
 * 2. **Transformer-based**: Use generic type parameter (requires transformer for schema injection)
 */

import type { ToolCall } from "@/llm/content/tool-call";
import type { Context } from "@/llm/context";
import type { ToolParameterSchema } from "@/llm/tools/tool-schema";
import type { Jsonable } from "@/llm/types/jsonable";

import { ToolOutput } from "@/llm/content/tool-output";
import { ToolExecutionError } from "@/llm/exceptions";
import { extractSchemaFromZod } from "@/llm/formatting";
import {
  TOOL_TYPE,
  CONTEXT_TOOL_TYPE,
  type ZodLike,
  type InferZod,
  type Tool,
  type ContextTool,
} from "@/llm/tools/tools";

/**
 * Check if a value is a Zod-like schema.
 */
export function isZodLike(value: unknown): value is ZodLike {
  return (
    typeof value === "object" &&
    value !== null &&
    "_def" in value &&
    typeof (value as ZodLike).safeParse === "function"
  );
}

// =============================================================================
// Zod-Native Tool Args (No Transformer Required)
// =============================================================================

/**
 * Arguments for defining a tool using a Zod schema.
 *
 * This pattern does NOT require the compile-time transformer.
 * The schema is extracted from the Zod validator at runtime.
 *
 * @template Z - The Zod schema type.
 */
export interface ZodToolArgs<Z extends ZodLike> {
  /** The name of the tool. */
  name: string;

  /** A description of what the tool does. */
  description: string;

  /**
   * Whether to use strict mode for the tool schema.
   * When true, providers that support it will enforce strict schema validation.
   */
  strict?: boolean;

  /**
   * Zod schema for both schema generation AND runtime validation.
   * Use `.describe()` on fields to add descriptions.
   */
  validator: Z;

  /** The tool implementation function. */
  tool: (args: InferZod<Z>) => Jsonable | Promise<Jsonable>;
}

/**
 * Arguments for defining a context tool using a Zod schema.
 *
 * This pattern does NOT require the compile-time transformer.
 *
 * @template Z - The Zod schema type.
 * @template DepsT - The type of dependencies in the context.
 */
export interface ZodContextToolArgs<Z extends ZodLike, DepsT = unknown> {
  /** The name of the tool. */
  name: string;

  /** A description of what the tool does. */
  description: string;

  /**
   * Whether to use strict mode for the tool schema.
   * When true, providers that support it will enforce strict schema validation.
   */
  strict?: boolean;

  /**
   * Zod schema for both schema generation AND runtime validation.
   * Use `.describe()` on fields to add descriptions.
   */
  validator: Z;

  /** The tool implementation function with context. */
  tool: (
    ctx: Context<DepsT>,
    args: InferZod<Z>,
  ) => Jsonable | Promise<Jsonable>;
}

// =============================================================================
// Transformer-Based Tool Args
// =============================================================================

/**
 * Arguments for defining a tool using the compile-time transformer.
 *
 * @template T - The type of arguments the tool accepts.
 */
export interface ToolArgs<T extends Record<string, unknown>> {
  /** The name of the tool. */
  name: string;

  /** A description of what the tool does. */
  description: string;

  /**
   * Whether to use strict mode for the tool schema.
   * When true, providers that support it will enforce strict schema validation.
   */
  strict?: boolean;

  /** The tool implementation function. */
  tool: (args: T) => Jsonable | Promise<Jsonable>;

  /**
   * Internal: JSON schema injected by the compile-time transformer.
   * Users should not set this directly - it's populated automatically.
   */
  __schema?: ToolParameterSchema;
}

/**
 * Arguments for defining a context tool using the compile-time transformer.
 *
 * @template T - The type of arguments the tool accepts.
 * @template DepsT - The type of dependencies in the context.
 */
export interface ContextToolArgs<
  T extends Record<string, unknown>,
  DepsT = unknown,
> {
  /** The name of the tool. */
  name: string;

  /** A description of what the tool does. */
  description: string;

  /**
   * Whether to use strict mode for the tool schema.
   * When true, providers that support it will enforce strict schema validation.
   */
  strict?: boolean;

  /** The tool implementation function with context. */
  tool: (ctx: Context<DepsT>, args: T) => Jsonable | Promise<Jsonable>;

  /**
   * Internal: JSON schema injected by the compile-time transformer.
   * Users should not set this directly - it's populated automatically.
   */
  __schema?: ToolParameterSchema;
}

// =============================================================================
// Type Guards
// =============================================================================

/**
 * Check if args have a validator (Zod-native path).
 */
function hasValidator<Z extends ZodLike>(
  args: ZodToolArgs<Z> | ToolArgs<Record<string, unknown>>,
): args is ZodToolArgs<Z> {
  return "validator" in args && isZodLike(args.validator);
}

/**
 * Check if context tool args have a validator (Zod-native path).
 */
function hasContextValidator<Z extends ZodLike, DepsT>(
  args:
    | ZodContextToolArgs<Z, DepsT>
    | ContextToolArgs<Record<string, unknown>, DepsT>,
): args is ZodContextToolArgs<Z, DepsT> {
  return "validator" in args && isZodLike(args.validator);
}

// =============================================================================
// Validation Helper
// =============================================================================

/**
 * Validate arguments against a Zod validator.
 *
 * @param args - The arguments to validate.
 * @param validator - The Zod validator.
 * @returns The validated arguments (potentially transformed by Zod).
 * @throws Error if validation fails.
 */
function validateWithZod<T>(args: T, validator: ZodLike): T {
  const result = validator.safeParse(args);
  if (!result.success) {
    throw new Error(`Validation failed: ${JSON.stringify(result.error)}`);
  }
  return result.data as T;
}

// =============================================================================
// defineTool Function
// =============================================================================

/**
 * Define a tool using a Zod schema (no transformer needed).
 *
 * @template Z - The Zod schema type.
 * @param args - The tool definition arguments with validator.
 * @returns A Tool instance with args inferred from the Zod schema.
 *
 * @example
 * ```typescript
 * import { z } from 'zod';
 *
 * const getWeather = defineTool({
 *   name: 'get_weather',
 *   description: 'Get weather for a city',
 *   validator: z.object({
 *     city: z.string().describe('The city name'),
 *   }),
 *   tool: ({ city }) => ({ temp: 72, city }),
 * });
 * ```
 */
export function defineTool<Z extends ZodLike>(
  args: ZodToolArgs<Z>,
): Tool<InferZod<Z>>;

/**
 * Define a tool using the compile-time transformer.
 *
 * @template T - The type of arguments the tool accepts.
 * @param args - The tool definition arguments.
 * @returns A Tool instance.
 *
 * @example
 * ```typescript
 * interface WeatherArgs {
 *   // JSDoc comments become field descriptions via transformer
 *   city: string;
 * }
 *
 * const getWeather = defineTool<WeatherArgs>({
 *   name: 'get_weather',
 *   description: 'Get weather for a city',
 *   tool: ({ city }) => ({ temp: 72, city }),
 * });
 * ```
 */
export function defineTool<T extends Record<string, unknown>>(
  args: ToolArgs<T>,
): Tool<T>;

/**
 * Implementation of defineTool.
 */
export function defineTool<
  T extends Record<string, unknown>,
  Z extends ZodLike = ZodLike,
>(args: ZodToolArgs<Z> | ToolArgs<T>): Tool<T> | Tool<InferZod<Z>> {
  const { name, description, strict } = args;

  // Determine which path to use
  if (
    hasValidator<Z>(args as ZodToolArgs<Z> | ToolArgs<Record<string, unknown>>)
  ) {
    // Zod-native path
    const { validator, tool } = args as ZodToolArgs<Z>;
    const { schema: parameters } = extractSchemaFromZod(validator);

    const callable = async (toolArgs: InferZod<Z>): Promise<Jsonable> => {
      const validatedArgs = validateWithZod(toolArgs, validator);
      const result = tool(validatedArgs);
      return result instanceof Promise ? result : Promise.resolve(result);
    };

    const execute = async (
      toolCall: ToolCall,
    ): Promise<ToolOutput<Jsonable>> => {
      try {
        const parsedArgs = JSON.parse(toolCall.args) as InferZod<Z>;
        const result = await callable(parsedArgs);
        return ToolOutput.success(toolCall.id, name, result);
      } catch (error) {
        const err = error instanceof Error ? error : new Error(String(error));
        return ToolOutput.failure(
          toolCall.id,
          name,
          new ToolExecutionError(err),
        );
      }
    };

    Object.defineProperty(callable, "name", { value: name, writable: false });
    return Object.assign(callable, {
      __toolType: TOOL_TYPE,
      description,
      parameters,
      strict,
      execute,
      validator,
    }) as Tool<InferZod<Z>>;
  }

  // Transformer-based path
  const { tool, __schema } = args as ToolArgs<T>;

  // Schema is required from transformer
  // Coverage ignored: When using the Mirascope transformer, __schema is always
  // injected at compile time. This error path is defensive for non-transformed usage.
  /* v8 ignore start */
  if (!__schema) {
    throw new Error(
      `Tool '${name}' is missing __schema. ` +
        "Either use the Mirascope TypeScript transformer, " +
        "or use the Zod-native pattern with a 'validator' option.",
    );
  }
  /* v8 ignore end */

  const callable = async (toolArgs: T): Promise<Jsonable> => {
    const result = tool(toolArgs);
    return result instanceof Promise ? result : Promise.resolve(result);
  };

  const execute = async (toolCall: ToolCall): Promise<ToolOutput<Jsonable>> => {
    try {
      const parsedArgs = JSON.parse(toolCall.args) as T;
      const result = await callable(parsedArgs);
      return ToolOutput.success(toolCall.id, name, result);
    } catch (error) {
      const err = error instanceof Error ? error : new Error(String(error));
      return ToolOutput.failure(toolCall.id, name, new ToolExecutionError(err));
    }
  };

  Object.defineProperty(callable, "name", { value: name, writable: false });
  return Object.assign(callable, {
    __toolType: TOOL_TYPE,
    description,
    parameters: __schema,
    strict,
    execute,
    validator: undefined,
  }) as Tool<T>;
}

// =============================================================================
// defineContextTool Function
// =============================================================================

/**
 * Define a context tool using a Zod schema (no transformer needed).
 *
 * @template Z - The Zod schema type.
 * @template DepsT - The type of dependencies in the context.
 * @param args - The tool definition arguments with validator.
 * @returns A ContextTool instance with args inferred from the Zod schema.
 *
 * @example
 * ```typescript
 * import { z } from 'zod';
 *
 * const searchDatabase = defineContextTool({
 *   name: 'search_database',
 *   description: 'Search the database',
 *   validator: z.object({
 *     query: z.string().describe('The search query'),
 *   }),
 *   tool: (ctx, { query }) => ctx.deps.db.search(query),
 * });
 * ```
 */
export function defineContextTool<Z extends ZodLike, DepsT = unknown>(
  args: ZodContextToolArgs<Z, DepsT>,
): ContextTool<InferZod<Z>, DepsT>;

/**
 * Define a context tool using the compile-time transformer.
 *
 * @template T - The type of arguments the tool accepts.
 * @template DepsT - The type of dependencies in the context.
 * @param args - The tool definition arguments.
 * @returns A ContextTool instance.
 *
 * @example
 * ```typescript
 * interface MyDeps {
 *   db: Database;
 * }
 *
 * interface SearchArgs {
 *   query: string;
 * }
 *
 * const searchDatabase = defineContextTool<SearchArgs, MyDeps>({
 *   name: 'search_database',
 *   description: 'Search the database',
 *   tool: (ctx, { query }) => ctx.deps.db.search(query),
 * });
 * ```
 */
export function defineContextTool<
  T extends Record<string, unknown>,
  DepsT = unknown,
>(args: ContextToolArgs<T, DepsT>): ContextTool<T, DepsT>;

/**
 * Implementation of defineContextTool.
 */
export function defineContextTool<
  T extends Record<string, unknown>,
  DepsT = unknown,
  Z extends ZodLike = ZodLike,
>(
  args: ZodContextToolArgs<Z, DepsT> | ContextToolArgs<T, DepsT>,
): ContextTool<T, DepsT> | ContextTool<InferZod<Z>, DepsT> {
  const { name, description, strict } = args;

  // Determine which path to use
  if (
    hasContextValidator<Z, DepsT>(
      args as
        | ZodContextToolArgs<Z, DepsT>
        | ContextToolArgs<Record<string, unknown>, DepsT>,
    )
  ) {
    // Zod-native path
    const { validator, tool } = args as ZodContextToolArgs<Z, DepsT>;
    const { schema: parameters } = extractSchemaFromZod(validator);

    const callable = async (
      ctx: Context<DepsT>,
      toolArgs: InferZod<Z>,
    ): Promise<Jsonable> => {
      const validatedArgs = validateWithZod(toolArgs, validator);
      const result = tool(ctx, validatedArgs);
      return result instanceof Promise ? result : Promise.resolve(result);
    };

    const execute = async (
      ctx: Context<DepsT>,
      toolCall: ToolCall,
    ): Promise<ToolOutput<Jsonable>> => {
      try {
        const parsedArgs = JSON.parse(toolCall.args) as InferZod<Z>;
        const result = await callable(ctx, parsedArgs);
        return ToolOutput.success(toolCall.id, name, result);
      } catch (error) {
        const err = error instanceof Error ? error : new Error(String(error));
        return ToolOutput.failure(
          toolCall.id,
          name,
          new ToolExecutionError(err),
        );
      }
    };

    Object.defineProperty(callable, "name", { value: name, writable: false });
    return Object.assign(callable, {
      __toolType: CONTEXT_TOOL_TYPE,
      description,
      parameters,
      strict,
      execute,
      validator,
    }) as ContextTool<InferZod<Z>, DepsT>;
  }

  // Transformer-based path
  const { tool, __schema } = args as ContextToolArgs<T, DepsT>;

  // Schema is required from transformer
  // Coverage ignored: When using the Mirascope transformer, __schema is always
  // injected at compile time. This error path is defensive for non-transformed usage.
  /* v8 ignore start */
  if (!__schema) {
    throw new Error(
      `Tool '${name}' is missing __schema. ` +
        "Either use the Mirascope TypeScript transformer, " +
        "or use the Zod-native pattern with a 'validator' option.",
    );
  }
  /* v8 ignore end */

  const callable = async (
    ctx: Context<DepsT>,
    toolArgs: T,
  ): Promise<Jsonable> => {
    const result = tool(ctx, toolArgs);
    return result instanceof Promise ? result : Promise.resolve(result);
  };

  const execute = async (
    ctx: Context<DepsT>,
    toolCall: ToolCall,
  ): Promise<ToolOutput<Jsonable>> => {
    try {
      const parsedArgs = JSON.parse(toolCall.args) as T;
      const result = await callable(ctx, parsedArgs);
      return ToolOutput.success(toolCall.id, name, result);
    } catch (error) {
      const err = error instanceof Error ? error : new Error(String(error));
      return ToolOutput.failure(toolCall.id, name, new ToolExecutionError(err));
    }
  };

  Object.defineProperty(callable, "name", { value: name, writable: false });
  return Object.assign(callable, {
    __toolType: CONTEXT_TOOL_TYPE,
    description,
    parameters: __schema,
    strict,
    execute,
    validator: undefined,
  }) as ContextTool<T, DepsT>;
}
