/**
 * Tool schema types for JSON Schema representation.
 *
 * These types define the structure of tool parameter schemas used
 * to describe tool inputs to LLM providers.
 */

/**
 * Reserved tool name for formatted output tools.
 *
 * This is used internally to convert formatted output tool calls to textual output.
 * It should not be used for regular tool definitions.
 */
export const FORMAT_TOOL_NAME = '__mirascope_formatted_output_tool__' as const;

/**
 * JSON Schema property definition for a single tool parameter.
 */
export interface JsonSchemaProperty {
  type?: string;
  description?: string;
  enum?: readonly (string | number | boolean)[];
  items?: JsonSchemaProperty;
  properties?: Record<string, JsonSchemaProperty>;
  required?: readonly string[];
  additionalProperties?: boolean;
  default?: unknown;
  $ref?: string;
  oneOf?: readonly JsonSchemaProperty[];
  allOf?: readonly JsonSchemaProperty[];
  anyOf?: readonly JsonSchemaProperty[];
}

/**
 * Tool parameter schema following JSON Schema format.
 *
 * This represents the complete parameter schema for a tool,
 * including all properties, required fields, and definitions.
 */
export interface ToolParameterSchema {
  readonly type: 'object';
  readonly title?: string;
  readonly properties: Record<string, JsonSchemaProperty>;
  readonly required: readonly string[];
  readonly additionalProperties: false;
  readonly $defs?: Record<string, JsonSchemaProperty>;
}

/**
 * Complete tool schema including name, description, and parameters.
 *
 * This is the provider-agnostic representation of a tool that
 * gets converted to provider-specific formats (OpenAI, Anthropic, etc.).
 */
export interface ToolSchema {
  readonly name: string;
  readonly description: string;
  readonly parameters: ToolParameterSchema;
  readonly strict?: boolean;
}
