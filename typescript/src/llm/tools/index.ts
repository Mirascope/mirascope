/**
 * Tools module for LLM function calling.
 *
 * Provides utilities for defining tools that LLMs can call,
 * including schema generation, validation, and execution.
 */

// Schema types and constants
export { FORMAT_TOOL_NAME } from '@/llm/tools/tool-schema';
export type {
  JsonSchemaProperty,
  ToolParameterSchema,
  ToolSchema,
} from '@/llm/tools/tool-schema';

// Tools
export { TOOL_TYPE, CONTEXT_TOOL_TYPE, isContextTool } from '@/llm/tools/tools';
export type {
  FieldDefinition,
  ZodLike,
  BaseTool,
  BaseContextTool,
  Tool,
  ContextTool,
  AnyTool,
  AnyContextTool,
  AnyToolSchema,
  // Array type aliases (matching Python's Sequence types)
  Tools,
  ContextTools,
} from '@/llm/tools/tools';

// Tool definition
export {
  defineTool,
  defineContextTool,
  isZodLike,
} from '@/llm/tools/define-tool';
export type { ToolArgs, ContextToolArgs } from '@/llm/tools/define-tool';

// Toolkit
export type {
  BaseToolkit,
  AnyTools,
  AnyContextTools,
} from '@/llm/tools/toolkit';
export {
  Toolkit,
  ContextToolkit,
  createToolkit,
  createContextToolkit,
  normalizeTools,
  normalizeContextTools,
} from '@/llm/tools/toolkit';
