/**
 * Tools module for LLM function calling.
 *
 * Provides utilities for defining tools that LLMs can call,
 * including schema generation, validation, and execution.
 */

// Schema types
export type {
  JsonSchemaProperty,
  ToolParameterSchema,
  ToolSchema,
} from '@/llm/tools/tool-schema';

// Tools
export type {
  FieldDefinition,
  ZodLike,
  BaseTool,
  BaseContextTool,
  Tool,
  ContextTool,
  AnyTool,
} from '@/llm/tools/tools';

// Tool definition
export {
  defineTool,
  defineContextTool,
  isZodLike,
} from '@/llm/tools/define-tool';
export type { ToolArgs, ContextToolArgs } from '@/llm/tools/define-tool';

// Toolkit
export {
  Toolkit,
  ContextToolkit,
  createToolkit,
  createContextToolkit,
} from './toolkit';
