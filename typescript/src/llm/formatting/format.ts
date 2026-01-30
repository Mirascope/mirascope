/**
 * Format class and utilities for structured LLM outputs.
 *
 * Provides the Format interface and functions for creating and resolving
 * structured output formats.
 */

import type { ToolParameterSchema, ToolSchema, ZodLike } from '@/llm/tools';
import {
  isOutputParser,
  type OutputParser,
} from '@/llm/formatting/output-parser';
import {
  isFormatSpec,
  isZodSchema,
  type FormattingMode,
  type FormatSpec,
} from '@/llm/formatting/types';

/**
 * Reserved tool name for formatted output tools.
 * This is used internally to convert formatted output tool calls to textual output.
 */
export const FORMAT_TOOL_NAME = '__mirascope_formatted_output_tool__';

/**
 * System prompt instructions for tool mode formatting.
 */
export const TOOL_MODE_INSTRUCTIONS = `Always respond to the user's query using the ${FORMAT_TOOL_NAME} tool for structured output.`;

/**
 * System prompt instructions for JSON mode formatting.
 * The {json_schema} placeholder will be replaced with the actual schema.
 */
export const JSON_MODE_INSTRUCTIONS =
  'Respond only with valid JSON that matches this exact schema:\n{json_schema}';

/**
 * Type discriminator symbol for Format.
 */
export const FORMAT_TYPE = Symbol('FORMAT_TYPE');

/**
 * Represents a resolved structured output format.
 *
 * A Format contains all metadata needed to describe a structured output type
 * to the LLM, including the JSON schema, formatting mode, and optional validator.
 *
 * Format objects are created by `defineFormat` or `resolveFormat` and are used
 * internally by providers to configure structured output requests.
 *
 * @template T - The type of the formatted output.
 */
export interface Format<T = unknown> {
  /**
   * Type discriminator for runtime identification.
   */
  readonly __formatType: typeof FORMAT_TYPE;

  /**
   * The name of the format (derived from the type name).
   */
  readonly name: string;

  /**
   * A description of the format, if available.
   */
  readonly description: string | null;

  /**
   * JSON schema representation of the structured output format.
   */
  readonly schema: ToolParameterSchema;

  /**
   * The formatting mode determining how the LLM is configured.
   */
  readonly mode: FormattingMode;

  /**
   * Optional Zod schema for runtime validation.
   */
  readonly validator: ZodLike | null;

  /**
   * Optional OutputParser for custom parsing.
   * When set, indicates this format uses custom parsing instead of JSON.
   */
  readonly outputParser: OutputParser<T> | null;

  /**
   * The formatting instructions to add to the system prompt.
   */
  readonly formattingInstructions: string | null;

  /**
   * Create a ToolSchema for this format.
   * Used when mode is 'tool' to generate a tool for structured output.
   */
  createToolSchema(): ToolSchema;
}

/**
 * Check if an object is a Format.
 *
 * @param obj - The object to check.
 * @returns True if the object is a Format.
 */
export function isFormat(obj: unknown): obj is Format<unknown> {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    '__formatType' in obj &&
    (obj as Format).__formatType === FORMAT_TYPE
  );
}

/**
 * Options for defineFormat when using TypeScript interfaces.
 *
 * The `__schema` field is injected by the compile-time transformer based on
 * the generic type parameter T.
 */
// eslint-disable-next-line @typescript-eslint/no-unused-vars -- T is for type inference
export interface DefineFormatOptions<T = unknown> {
  /**
   * The formatting mode to use.
   */
  mode: FormattingMode;

  /**
   * Optional Zod schema for runtime validation.
   */
  validator?: ZodLike;

  /**
   * Internal: JSON schema injected by compile-time transformer.
   * Do not set this manually - it is populated automatically when using
   * the Mirascope transformer with TypeScript interfaces.
   */
  __schema?: ToolParameterSchema;
}

/**
 * Create a Format with explicit mode control.
 *
 * Use this to create structured output formats for LLM responses. The format
 * can be derived from a Zod schema (via `validator`) or a TypeScript interface
 * (via the compile-time transformer which injects `__schema`).
 *
 * @template T - The type of the formatted output.
 * @param options - The format options including mode and optional validator.
 * @returns A Format object.
 *
 * @example With Zod schema
 * ```typescript
 * const BookSchema = z.object({ title: z.string(), author: z.string() });
 * const bookFormat = defineFormat<Book>({ mode: 'tool', validator: BookSchema });
 * const response = await model.call('Recommend a book', { format: bookFormat });
 * const book = response.parse(); // Typed as Book
 * ```
 *
 * @example With TypeScript interface (requires transformer)
 * ```typescript
 * interface Book { title: string; author: string; }
 *
 * // Transformer injects __schema at compile time
 * const bookFormat = defineFormat<Book>({ mode: 'json' });
 * ```
 */
export function defineFormat<T>(options: DefineFormatOptions<T>): Format<T> {
  const { mode, validator, __schema } = options;

  // If we have a validator, extract schema from it
  if (validator) {
    return createFormatFromZod<T>(validator, mode);
  }

  // Must have __schema (injected by transformer) at this point
  if (!__schema) {
    throw new Error(
      'Format specification is missing schema. ' +
        'Provide a Zod schema via the `validator` option, ' +
        'or use the Mirascope TypeScript transformer with a type parameter.'
    );
  }

  return createFormatFromSchema<T>(__schema, null, mode);
}

/**
 * Resolve any format input to internal Format representation.
 *
 * This function handles all possible format inputs and converts them to
 * a Format object. It's used internally by providers to normalize format
 * specifications.
 *
 * @template T - The type of the formatted output.
 * @param formatArg - The format specification (can be Format, FormatSpec, ZodLike, OutputParser, or null).
 * @param defaultMode - The default mode to use when not explicitly specified.
 * @returns A Format object or null.
 */
export function resolveFormat<T>(
  formatArg:
    | Format<T>
    | FormatSpec<T>
    | ZodLike
    | OutputParser<T>
    | null
    | undefined,
  defaultMode: FormattingMode
): Format<T> | null {
  // Handle null/undefined
  if (formatArg === null || formatArg === undefined) {
    return null;
  }

  // Handle Format (pass through)
  if (isFormat(formatArg)) {
    return formatArg;
  }

  // Handle OutputParser
  if (isOutputParser(formatArg)) {
    return createFormatFromOutputParser<T>(formatArg);
  }

  // Handle Zod schema
  if (isZodSchema(formatArg)) {
    return createFormatFromZod<T>(formatArg, defaultMode);
  }

  // Handle FormatSpec
  if (isFormatSpec(formatArg)) {
    const spec = formatArg;

    // If we have a validator that's a Zod schema, use it for schema if __schema missing
    if (spec.validator && !spec.__schema) {
      return createFormatFromZod<T>(spec.validator, defaultMode);
    }

    // Must have __schema
    if (!spec.__schema) {
      throw new Error(
        'Format specification is missing __schema. ' +
          'Either use the Mirascope TypeScript transformer, provide a Zod schema, ' +
          'or provide __schema explicitly.'
      );
    }

    return createFormatFromSchema<T>(
      spec.__schema,
      spec.validator ?? null,
      defaultMode
    );
  }

  // Unknown format type - shouldn't happen with proper types
  throw new Error(`Unknown format type: ${typeof formatArg}`);
}

// =============================================================================
// Internal helper functions
// =============================================================================

/**
 * Create a Format from a Zod schema.
 */
function createFormatFromZod<T>(
  zodSchema: ZodLike,
  mode: FormattingMode
): Format<T> {
  // Extract JSON schema from Zod
  // Note: In production, we'd use zod-to-json-schema or similar
  // For now, we assume the transformer or runtime handles this
  const schema = extractSchemaFromZod(zodSchema);
  const name = extractNameFromZod(zodSchema);
  // Zod 4: description at top level, Zod 3: in _def.description
  const def = zodSchema._def as { description?: string };
  const description = zodSchema.description ?? def.description ?? null;

  return createFormat<T>({
    name,
    description,
    schema,
    mode,
    validator: zodSchema,
    outputParser: null,
  });
}

/**
 * Create a Format from a ToolParameterSchema.
 */
function createFormatFromSchema<T>(
  schema: ToolParameterSchema,
  validator: ZodLike | null,
  mode: FormattingMode
): Format<T> {
  // Extract name from schema title or use default
  const name =
    ((schema as unknown as Record<string, unknown>).title as
      | string
      | undefined) ?? 'FormattedOutput';

  return createFormat<T>({
    name,
    description: null,
    schema,
    mode,
    validator,
    outputParser: null,
  });
}

/**
 * Create a Format from an OutputParser.
 */
function createFormatFromOutputParser<T>(parser: OutputParser<T>): Format<T> {
  // OutputParser has empty schema - it uses custom parsing
  const emptySchema: ToolParameterSchema = {
    type: 'object',
    properties: {},
    required: [],
    additionalProperties: false,
  };

  return createFormat<T>({
    name: parser.name,
    description: null,
    schema: emptySchema,
    mode: 'parser',
    validator: null,
    outputParser: parser,
  });
}

/**
 * Internal Format creation options.
 */
interface CreateFormatOptions<T> {
  name: string;
  description: string | null;
  schema: ToolParameterSchema;
  mode: FormattingMode;
  validator: ZodLike | null;
  outputParser: OutputParser<T> | null;
}

/**
 * Create a Format object with all properties.
 */
function createFormat<T>(options: CreateFormatOptions<T>): Format<T> {
  const { name, description, schema, mode, validator, outputParser } = options;

  // Compute formatting instructions based on mode
  let formattingInstructions: string | null;
  if (outputParser) {
    formattingInstructions = outputParser.formattingInstructions;
  } else if (mode === 'tool') {
    formattingInstructions = TOOL_MODE_INSTRUCTIONS;
  } else if (mode === 'json') {
    const jsonSchema = JSON.stringify(schema, null, 2);
    formattingInstructions = JSON_MODE_INSTRUCTIONS.replace(
      '{json_schema}',
      jsonSchema
    );
  } else {
    // strict mode - let provider handle instructions
    formattingInstructions = null;
  }

  return {
    __formatType: FORMAT_TYPE,
    name,
    description,
    schema,
    mode,
    validator,
    outputParser,
    formattingInstructions,
    createToolSchema(): ToolSchema {
      const toolDescription = `Use this tool to extract data in ${name} format for a final response.${
        description ? '\n' + description : ''
      }`;

      // Get all property keys as required
      /* v8 ignore next */ // properties always exists in valid JSON schemas
      const properties = schema.properties ?? {};
      const required = Object.keys(properties);

      // Build parameters object - include $defs if present
      const parameters: ToolParameterSchema = {
        type: 'object',
        properties,
        required,
        additionalProperties: false,
        ...(schema.$defs && { $defs: schema.$defs }),
      };

      return {
        name: FORMAT_TOOL_NAME,
        description: toolDescription,
        parameters,
        strict: undefined, // Provider determines strict mode
      };
    },
  };
}

/**
 * Extract JSON schema from a Zod schema.
 *
 * Supports both Zod 3 and Zod 4:
 * - Zod 4: Uses toJSONSchema() method if available
 * - Zod 3: Manually extracts from _def structure
 */
function extractSchemaFromZod(zodSchema: ZodLike): ToolParameterSchema {
  const schemaAny = zodSchema as unknown as Record<string, unknown>;

  // Zod 4: Use toJSONSchema() if available (preferred method)
  if (typeof schemaAny.toJSONSchema === 'function') {
    try {
      const jsonSchema = (schemaAny.toJSONSchema as () => unknown)() as Record<
        string,
        unknown
      >;
      // Ensure additionalProperties is false for strict matching
      // Note: ?? fallbacks are for edge cases where toJSONSchema returns incomplete data
      const properties =
        /* v8 ignore next */
        (jsonSchema.properties as ToolParameterSchema['properties']) ?? {};
      const required =
        /* v8 ignore next */
        (jsonSchema.required as ToolParameterSchema['required']) ?? [];
      const $defs = jsonSchema.$defs as ToolParameterSchema['$defs'];

      // Include $defs if present (for nested schemas)
      /* v8 ignore start */
      if ($defs) {
        return {
          type: 'object',
          properties,
          required,
          additionalProperties: false,
          $defs,
        } as const satisfies ToolParameterSchema;
      }
      /* v8 ignore end */
      return {
        type: 'object',
        properties,
        required,
        additionalProperties: false,
      } as const satisfies ToolParameterSchema;
    } catch /* v8 ignore start */ {
      // Fall through to manual extraction
    } /* v8 ignore end */
  }

  // Zod 3/4 fallback: Manually extract from _def
  if (typeof schemaAny._def === 'object' && schemaAny._def !== null) {
    const def = schemaAny._def as Record<string, unknown>;

    // Zod 3: typeName is 'ZodObject', shape is a function
    if (def.typeName === 'ZodObject' && typeof def.shape === 'function') {
      return extractSchemaFromZod3(def);
    }

    /* v8 ignore start */
    // Zod 4: type is 'object', shape is a getter (object)
    if (def.type === 'object' && typeof def.shape === 'object') {
      return extractSchemaFromZod4(def);
    }
    /* v8 ignore end */
  }

  // Fallback: return empty schema
  // The transformer should inject proper schema at compile time
  /* v8 ignore start */
  return {
    type: 'object',
    properties: {},
    required: [],
    additionalProperties: false,
  };
  /* v8 ignore end */
}

/**
 * Extract schema from Zod 3 definition.
 */
function extractSchemaFromZod3(
  def: Record<string, unknown>
): ToolParameterSchema {
  const shape = (def.shape as () => Record<string, ZodLike>)();
  const properties: Record<string, unknown> = {};
  const required: string[] = [];

  for (const [key, fieldSchema] of Object.entries(shape)) {
    properties[key] = extractFieldSchema(fieldSchema);
    // Check if field is optional
    const fieldDef = fieldSchema._def as Record<string, unknown>;
    if (fieldDef.typeName !== 'ZodOptional') {
      required.push(key);
    }
  }

  return {
    type: 'object',
    properties: properties as Record<
      string,
      { type?: string; description?: string }
    >,
    required,
    additionalProperties: false,
  };
}

/**
 * Extract schema from Zod 4 definition.
 * This is a fallback when toJSONSchema() is not available.
 */
/* v8 ignore start */
function extractSchemaFromZod4(
  def: Record<string, unknown>
): ToolParameterSchema {
  const shape = def.shape as Record<string, ZodLike>;
  const properties: Record<string, unknown> = {};
  const required: string[] = [];

  for (const [key, fieldSchema] of Object.entries(shape)) {
    properties[key] = extractFieldSchemaZod4(fieldSchema);
    // Check if field is optional (Zod 4 uses isOptional method)
    const schemaAny = fieldSchema as unknown as {
      isOptional?: () => boolean;
      _def?: { type?: string };
    };
    const isOptional =
      typeof schemaAny.isOptional === 'function'
        ? schemaAny.isOptional()
        : schemaAny._def?.type === 'optional';
    if (!isOptional) {
      required.push(key);
    }
  }

  return {
    type: 'object',
    properties: properties as Record<
      string,
      { type?: string; description?: string }
    >,
    required,
    additionalProperties: false,
  };
}
/* v8 ignore end */

/**
 * Extract JSON schema for a single Zod 3 field.
 */
function extractFieldSchema(zodField: ZodLike): {
  type?: string;
  description?: string;
} {
  const def = zodField._def as Record<string, unknown>;
  const description = def.description as string | undefined;

  // Handle wrapped types (optional, nullable, etc.)
  if (def.innerType && typeof def.innerType === 'object') {
    const inner = extractFieldSchema(def.innerType as ZodLike);
    /* v8 ignore next */ // description ?? inner.description - both branches tested
    return { ...inner, description: description ?? inner.description };
  }

  // Map Zod types to JSON Schema types
  const typeMapping: Record<string, string> = {
    ZodString: 'string',
    ZodNumber: 'number',
    ZodBoolean: 'boolean',
    ZodArray: 'array',
    ZodObject: 'object',
  };

  const typeName = def.typeName as string;
  const type = typeMapping[typeName];

  return {
    ...(type && { type }),
    /* v8 ignore next */ // description is usually undefined for simple fields
    ...(description && { description }),
  };
}

/**
 * Extract JSON schema for a single Zod 4 field.
 * This is a fallback when toJSONSchema() is not available.
 */
/* v8 ignore start */
function extractFieldSchemaZod4(zodField: ZodLike): {
  type?: string;
  description?: string;
  items?: { type?: string };
} {
  const def = zodField._def as Record<string, unknown>;
  const fieldAny = zodField as unknown as { description?: string };
  // Zod 4: description at top level, Zod 3: in _def.description
  const description =
    fieldAny.description ?? (def.description as string | undefined);

  // Handle wrapped types (optional, nullable, etc.)
  if (def.innerType && typeof def.innerType === 'object') {
    const inner = extractFieldSchemaZod4(def.innerType as ZodLike);
    return { ...inner, description: description ?? inner.description };
  }

  // Zod 4 uses _def.type directly as a string
  const zodType = def.type as string | undefined;

  // Map Zod 4 types to JSON Schema types
  const typeMapping: Record<string, string> = {
    string: 'string',
    number: 'number',
    boolean: 'boolean',
    array: 'array',
    object: 'object',
    int: 'integer',
  };

  const type = zodType ? typeMapping[zodType] : undefined;

  // Handle array items
  if (zodType === 'array' && def.element) {
    const itemSchema = extractFieldSchemaZod4(def.element as ZodLike);
    return {
      type: 'array',
      items: itemSchema,
      ...(description && { description }),
    };
  }

  return {
    ...(type && { type }),
    ...(description && { description }),
  };
}
/* v8 ignore end */

/**
 * Extract a name from a Zod schema.
 */
function extractNameFromZod(zodSchema: ZodLike): string {
  // Try to get description as name (Zod 4: top level, Zod 3: _def.description)
  const def = zodSchema._def as { description?: string };
  const description = zodSchema.description ?? def.description;
  if (description) {
    // Use first word of description as name
    const firstWord = description.split(/\s+/)[0];
    if (firstWord && firstWord.length < 30) {
      return firstWord;
    }
  }

  return 'FormattedOutput';
}
