/**
 * Utilities for parsing LLM responses.
 *
 * Provides functions for extracting and parsing JSON from LLM text responses,
 * including support for partial JSON parsing during streaming.
 */

import { parse as parsePartialJson } from "partial-json";

import type { ZodLike } from "@/llm/tools";

/**
 * Strip preamble text before JSON content.
 *
 * Handles common patterns like:
 * - "Sure thing! Here's the JSON:\n{..."
 * - "```json\n[..."
 * - Plain text followed by JSON
 *
 * @param text - The text that may contain a JSON preamble.
 * @returns The text starting from the first '{' or '[', or null if neither found.
 */
function stripJsonPreamble(text: string): string | null {
  // Handle markdown code blocks
  const codeBlockStart = text.indexOf("```json");
  if (codeBlockStart > -1) {
    // Skip past the ```json marker
    text = text.slice(codeBlockStart + 7);
    // Also handle closing ``` if present
    const codeBlockEnd = text.indexOf("```");
    if (codeBlockEnd > -1) {
      text = text.slice(0, codeBlockEnd);
    }
  }

  // Find the start of the JSON object or array
  const objectStart = text.indexOf("{");
  const arrayStart = text.indexOf("[");

  let jsonStart: number;
  if (objectStart === -1 && arrayStart === -1) {
    return null;
  } else if (objectStart === -1) {
    jsonStart = arrayStart;
  } else if (arrayStart === -1) {
    jsonStart = objectStart;
  } else {
    jsonStart = Math.min(objectStart, arrayStart);
  }

  return text.slice(jsonStart);
}

/**
 * Extract the serialized JSON string from text that may contain extra content.
 *
 * This function handles cases where the LLM includes explanatory text before
 * or after the JSON object. It finds the complete JSON object by matching
 * opening and closing braces.
 *
 * @param text - The text containing JSON, possibly with extra content.
 * @returns The extracted JSON string.
 * @throws SyntaxError if no valid JSON object is found.
 *
 * @example
 * ```typescript
 * const text = 'Here is the book:\n{"title": "1984", "author": "Orwell"}\nHope this helps!';
 * const json = extractSerializedJson(text);
 * // json = '{"title": "1984", "author": "Orwell"}'
 * ```
 */
export function extractSerializedJson(text: string): string {
  const stripped = stripJsonPreamble(text);
  if (!stripped) {
    throw new SyntaxError("No JSON found in response: missing '{' or '['");
  }

  // Determine if we're parsing an object or array
  const isArray = stripped[0] === "[";
  const openChar = isArray ? "[" : "{";
  const closeChar = isArray ? "]" : "}";

  // Find matching closing delimiter
  let depth = 0;
  let inString = false;
  let escaped = false;

  for (let i = 0; i < stripped.length; i++) {
    const char = stripped[i];

    if (escaped) {
      escaped = false;
      continue;
    }

    if (char === "\\") {
      escaped = true;
      continue;
    }

    if (char === '"' && !escaped) {
      inString = !inString;
      continue;
    }

    if (!inString) {
      if (char === openChar) {
        depth++;
      } else if (char === closeChar) {
        depth--;
        if (depth === 0) {
          return stripped.slice(0, i + 1);
        }
      }
    }
  }

  throw new SyntaxError(`No JSON found in response: missing '${closeChar}'`);
}

/**
 * Parse potentially incomplete JSON into a partial object.
 *
 * This function uses the `partial-json` library to handle incomplete JSON
 * that may arrive during streaming. It gracefully handles:
 * - Unclosed braces/brackets
 * - Incomplete strings
 * - Trailing content
 *
 * @template T - The expected type of the parsed output.
 * @param jsonText - The potentially incomplete JSON text.
 * @param validator - Optional Zod schema for validation (best effort).
 * @returns The parsed partial object, or null if parsing fails.
 *
 * @example
 * ```typescript
 * // During streaming, we might receive:
 * const partial1 = parsePartial('{"title": "19');        // { title: "19" }
 * const partial2 = parsePartial('{"title": "1984", "au'); // { title: "1984" }
 * const partial3 = parsePartial('{"title": "1984", "author": "Orwell"}'); // Complete
 * ```
 */
export function parsePartial<T>(
  jsonText: string,
  validator?: ZodLike,
  unwrapKey?: string,
): T | null {
  const stripped = stripJsonPreamble(jsonText);
  if (!stripped) {
    return null;
  }

  try {
    // Use partial-json library for robust partial parsing
    // The library returns `any`, so we cast to `unknown` for type safety
    let parsed: unknown = parsePartialJson(stripped);

    // Unwrap if schema was wrapped (non-object types like arrays)
    if (unwrapKey && typeof parsed === "object" && parsed !== null) {
      parsed = (parsed as Record<string, unknown>)[unwrapKey];
      if (parsed === undefined) {
        return null;
      }
    }

    // If no validator, return parsed directly
    if (!validator) {
      return parsed as T;
    }

    // Try to validate with Zod
    // For partial parsing, we use safeParse and accept whatever succeeds
    // since the data may be incomplete
    const result = validator.safeParse(parsed);
    if (result.success) {
      return result.data as T;
    }

    // If validation fails on partial data, still return the parsed value
    // This is expected during streaming when not all fields are present yet
    return parsed as T;
    /* v8 ignore start -- defensive: partial-json library is designed to not throw */
  } catch {
    // Parsing failed - likely JSON is too incomplete
    return null;
  }
  /* v8 ignore stop */
}
