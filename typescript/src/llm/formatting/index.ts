/**
 * Response formatting interfaces for structuring LLM outputs.
 *
 * This module provides a way to define structured output formats for LLM responses.
 * Use `defineFormat` to create formats with explicit mode control, or pass
 * format specs directly to call/stream methods.
 *
 * The `defineOutputParser` function can be used to create custom parsers for
 * non-JSON formats like XML, YAML, CSV, or any custom text structure.
 */

// Types
export type {
  FormattingMode,
  FormatSpec,
  FormatInput,
  AnyFormatInput,
  ExtractFormatType,
} from "@/llm/formatting/types";
export { isZodSchema, isFormatSpec } from "@/llm/formatting/types";

// Partial type
export type { DeepPartial } from "@/llm/formatting/partial";

// OutputParser
export type {
  OutputParser,
  OutputParserArgs,
  AnyResponse,
} from "@/llm/formatting/output-parser";
export {
  defineOutputParser,
  isOutputParser,
  OUTPUT_PARSER_TYPE,
} from "@/llm/formatting/output-parser";

// Format
export type { Format, DefineFormatOptions } from "@/llm/formatting/format";
export {
  defineFormat,
  resolveFormat,
  isFormat,
  extractSchemaFromZod,
  FORMAT_TYPE,
  FORMAT_TOOL_NAME,
  TOOL_MODE_INSTRUCTIONS,
  JSON_MODE_INSTRUCTIONS,
} from "@/llm/formatting/format";
