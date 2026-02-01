/**
 * Tool definition functions for creating LLM-callable tools.
 *
 * Provides `defineTool()` and `defineContextTool()` for creating tools
 * with type-safe argument inference and optional Zod validation.
 */

import type { Context } from '@/llm/context';
import { ToolExecutionError } from '@/llm/exceptions';
import type { ToolCall } from '@/llm/content/tool-call';
import { ToolOutput } from '@/llm/content/tool-output';
import type { Jsonable } from '@/llm/types/jsonable';
import type { ToolParameterSchema } from '@/llm/tools/tool-schema';
import type {
  FieldDefinition,
  ZodLike,
  Tool,
  ContextTool,
} from '@/llm/tools/tools';

/**
 * Check if a value is a Zod-like schema.
 */
export function isZodLike(value: unknown): value is ZodLike {
  return (
    typeof value === 'object' &&
    value !== null &&
    '_def' in value &&
    typeof (value as ZodLike).safeParse === 'function'
  );
}

/**
 * Get description from a field definition.
 */
function getFieldDescription(field: FieldDefinition): string | undefined {
  if (typeof field === 'string') {
    return field;
  }
  if (isZodLike(field)) {
    return field._def.description;
  }
  return undefined;
}

/**
 * Arguments for defining a tool.
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

  /**
   * Optional field definitions providing descriptions or Zod validators.
   *
   * Keys should match the fields in T. Values can be:
   * - A string description for the field
   * - A Zod schema for validation + description
   */
  fieldDefinitions?: Partial<Record<keyof T, FieldDefinition>>;

  /** The tool implementation function. */
  tool: (args: T) => Jsonable | Promise<Jsonable>;

  /**
   * Internal: JSON schema injected by the compile-time transformer.
   * Users should not set this directly - it's populated automatically.
   */
  __schema?: ToolParameterSchema;
}

/**
 * Arguments for defining a context tool with dependency injection.
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

  /**
   * Optional field definitions providing descriptions or Zod validators.
   *
   * Keys should match the fields in T. Values can be:
   * - A string description for the field
   * - A Zod schema for validation + description
   */
  fieldDefinitions?: Partial<Record<keyof T, FieldDefinition>>;

  /** The tool implementation function with context. */
  tool: (ctx: Context<DepsT>, args: T) => Jsonable | Promise<Jsonable>;

  /**
   * Internal: JSON schema injected by the compile-time transformer.
   * Users should not set this directly - it's populated automatically.
   */
  __schema?: ToolParameterSchema;
}

/**
 * Validate arguments against Zod field definitions.
 *
 * @param args - The arguments to validate.
 * @param fieldDefinitions - The field definitions with potential Zod schemas.
 * @returns The validated arguments (potentially transformed by Zod).
 * @throws Error if validation fails.
 */
function validateArgs<T extends Record<string, unknown>>(
  args: T,
  fieldDefinitions: Partial<Record<keyof T, FieldDefinition>> | undefined
): T {
  if (!fieldDefinitions) {
    return args;
  }

  const validated = { ...args };

  for (const [key, definition] of Object.entries(fieldDefinitions)) {
    if (isZodLike(definition)) {
      const result = definition.safeParse(args[key as keyof T]);
      if (!result.success) {
        throw new Error(
          `Validation failed for field '${key}': ${JSON.stringify(result.error)}`
        );
      }
      validated[key as keyof T] = result.data as T[keyof T];
    }
  }

  return validated;
}

/**
 * Merge field definitions into the schema properties.
 *
 * @param schema - The base schema from __schema.
 * @param fieldDefinitions - The field definitions with descriptions.
 * @returns A new schema with descriptions merged in.
 */
function mergeDescriptions(
  schema: ToolParameterSchema,
  fieldDefinitions: Partial<Record<string, FieldDefinition>> | undefined
): ToolParameterSchema {
  if (!fieldDefinitions) {
    return schema;
  }

  const newProperties = { ...schema.properties };

  for (const [key, definition] of Object.entries(fieldDefinitions)) {
    if (key in newProperties && definition !== undefined) {
      const description = getFieldDescription(definition);
      if (description !== undefined) {
        newProperties[key] = {
          ...newProperties[key],
          description,
        };
      }
    }
  }

  return {
    ...schema,
    properties: newProperties,
  };
}

/**
 * Define a tool that can be called by an LLM.
 *
 * @template T - The type of arguments the tool accepts.
 * @param args - The tool definition arguments.
 * @returns A Tool instance.
 *
 * @example Basic usage
 * ```typescript
 * const getWeather = defineTool<{ city: string }>({
 *   name: 'get_weather',
 *   description: 'Get weather for a city',
 *   fieldDefinitions: {
 *     city: 'The city name',
 *   },
 *   tool: ({ city }) => ({ temp: 72, city }),
 * });
 * ```
 *
 * @example With Zod validation
 * ```typescript
 * import { z } from 'zod';
 *
 * const getWeather = defineTool<{ city: string }>({
 *   name: 'get_weather',
 *   description: 'Get weather for a city',
 *   fieldDefinitions: {
 *     city: z.string().min(1).describe('The city name'),
 *   },
 *   tool: ({ city }) => ({ temp: 72, city }),
 * });
 * ```
 */
export function defineTool<T extends Record<string, unknown>>(
  args: ToolArgs<T>
): Tool<T> {
  const { name, description, fieldDefinitions, tool, strict, __schema } = args;

  // Schema is required - either from transformer or explicit
  if (!__schema) {
    throw new Error(
      `Tool '${name}' is missing __schema. ` +
        'Either use the Mirascope TypeScript transformer, or provide __schema explicitly.'
    );
  }

  const parameters = mergeDescriptions(__schema, fieldDefinitions);

  const callable = async (toolArgs: T): Promise<Jsonable> => {
    const validatedArgs = validateArgs(toolArgs, fieldDefinitions);
    const result = tool(validatedArgs);
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

  // Note: We need to use defineProperty for 'name' since Function.name is read-only
  Object.defineProperty(callable, 'name', { value: name, writable: false });
  return Object.assign(callable, {
    description,
    parameters,
    strict,
    execute,
    fieldDefinitions,
  }) as Tool<T>;
}

/**
 * Define a context tool with dependency injection.
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
 * const searchDatabase = defineContextTool<{ query: string }, MyDeps>({
 *   name: 'search_database',
 *   description: 'Search the database',
 *   fieldDefinitions: {
 *     query: 'The search query',
 *   },
 *   tool: (ctx, { query }) => ctx.deps.db.search(query),
 * });
 * ```
 */
export function defineContextTool<
  T extends Record<string, unknown>,
  DepsT = unknown,
>(args: ContextToolArgs<T, DepsT>): ContextTool<T, DepsT> {
  const { name, description, fieldDefinitions, tool, strict, __schema } = args;

  // Schema is required - either from transformer or explicit
  if (!__schema) {
    throw new Error(
      `Tool '${name}' is missing __schema. ` +
        'Either use the Mirascope TypeScript transformer, or provide __schema explicitly.'
    );
  }

  const parameters = mergeDescriptions(__schema, fieldDefinitions);

  const callable = async (
    ctx: Context<DepsT>,
    toolArgs: T
  ): Promise<Jsonable> => {
    const validatedArgs = validateArgs(toolArgs, fieldDefinitions);
    const result = tool(ctx, validatedArgs);
    return result instanceof Promise ? result : Promise.resolve(result);
  };

  const execute = async (
    ctx: Context<DepsT>,
    toolCall: ToolCall
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

  // Note: We need to use defineProperty for 'name' since Function.name is read-only
  Object.defineProperty(callable, 'name', { value: name, writable: false });
  return Object.assign(callable, {
    description,
    parameters,
    strict,
    execute,
    fieldDefinitions,
  }) as ContextTool<T, DepsT>;
}
