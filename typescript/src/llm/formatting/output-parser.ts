/**
 * Output parser for custom format parsing.
 *
 * Provides OutputParser type and defineOutputParser function for creating
 * custom parsers for non-JSON formats like XML, YAML, CSV, or any custom
 * text structure.
 */

import type { RootResponse } from '@/llm/responses/root-response';

/**
 * Type discriminator symbol for OutputParser.
 * Used at runtime to distinguish OutputParsers from other format types.
 */
export const OUTPUT_PARSER_TYPE = Symbol('OUTPUT_PARSER_TYPE');

/**
 * Any response type that can be passed to an OutputParser.
 * Uses RootResponse as the base type.
 */
export type AnyResponse = RootResponse;

/**
 * Represents a custom output parser for non-JSON formats.
 *
 * OutputParser wraps a parsing function and stores formatting instructions.
 * Unlike structured outputs (JSON schema, tools, strict mode), OutputParser
 * works with raw text responses and custom parsing logic.
 *
 * @template T - The type of the parsed output.
 *
 * @example
 * ```typescript
 * const xmlParser = defineOutputParser({
 *   formattingInstructions: 'Return XML: <book><title>...</title></book>',
 *   parser: (response) => {
 *     const text = response.text();
 *     // Parse XML and return Book
 *     return { title: '...', author: '...' };
 *   },
 * });
 *
 * const response = await model.call('Recommend a book', { format: xmlParser });
 * const book = response.parse(); // Returns parsed Book
 * ```
 */
export interface OutputParser<T = unknown> {
  /**
   * Type discriminator for runtime identification.
   */
  readonly __outputParserType: typeof OUTPUT_PARSER_TYPE;

  /**
   * The name of the output parser (derived from parser function name).
   */
  readonly name: string;

  /**
   * Instructions for the LLM on how to format its output.
   * These are added to the system prompt.
   */
  readonly formattingInstructions: string;

  /**
   * Parse the response using the wrapped function.
   *
   * @param response - The response from the LLM call.
   * @returns The parsed output of type T.
   */
  (response: AnyResponse): T;
}

/**
 * Arguments for defining an output parser.
 *
 * @template T - The type of the parsed output.
 */
export interface OutputParserArgs<T> {
  /**
   * Instructions for the LLM on how to format the output.
   * These will be added to the system prompt.
   */
  formattingInstructions: string;

  /**
   * The parsing function that takes a Response and returns the parsed output.
   *
   * @param response - The response from the LLM call.
   * @returns The parsed output of type T.
   */
  parser: (response: AnyResponse) => T;
}

/**
 * Create an output parser for custom format parsing.
 *
 * Use this function to create custom parsers for non-JSON formats like
 * XML, YAML, CSV, or any custom text structure. The parser function
 * receives the full Response object and returns the parsed output.
 *
 * @template T - The type of the parsed output.
 * @param args - The output parser arguments.
 * @returns An OutputParser instance.
 *
 * @example XML parsing
 * ```typescript
 * interface Book {
 *   title: string;
 *   author: string;
 * }
 *
 * const bookXmlParser = defineOutputParser<Book>({
 *   formattingInstructions: `
 *     Return the book information in this XML structure:
 *     <book>
 *       <title>Book Title</title>
 *       <author>Author Name</author>
 *     </book>
 *   `,
 *   parser: (response) => {
 *     const text = response.text();
 *     // Parse XML (example using regex, use proper parser in production)
 *     const titleMatch = text.match(/<title>([^<]+)<\/title>/);
 *     const authorMatch = text.match(/<author>([^<]+)<\/author>/);
 *     return {
 *       title: titleMatch?.[1] ?? '',
 *       author: authorMatch?.[1] ?? '',
 *     };
 *   },
 * });
 *
 * const response = await model.call('Recommend a fantasy book', {
 *   format: bookXmlParser,
 * });
 * const book = response.parse(); // Type: Book
 * ```
 *
 * @example CSV parsing
 * ```typescript
 * interface Book {
 *   title: string;
 *   author: string;
 *   rating: number;
 * }
 *
 * const booksCsvParser = defineOutputParser<Book[]>({
 *   formattingInstructions: `
 *     Return book information as CSV format with header:
 *     title,author,rating
 *     Book 1,Author 1,5
 *     Book 2,Author 2,4
 *   `,
 *   parser: (response) => {
 *     const text = response.text();
 *     const lines = text.trim().split('\n').slice(1); // Skip header
 *     return lines.map((line) => {
 *       const [title, author, rating] = line.split(',').map((s) => s.trim());
 *       return { title, author, rating: parseInt(rating, 10) };
 *     });
 *   },
 * });
 * ```
 */
export function defineOutputParser<T>(
  args: OutputParserArgs<T>
): OutputParser<T> {
  const { formattingInstructions, parser } = args;

  // Create the callable function
  const outputParser = ((response: AnyResponse): T => {
    return parser(response);
  }) as OutputParser<T>;

  // Add OutputParser properties
  Object.defineProperty(outputParser, '__outputParserType', {
    value: OUTPUT_PARSER_TYPE,
    enumerable: false,
    writable: false,
  });
  Object.defineProperty(outputParser, 'name', {
    /* v8 ignore next */ // Fallback name rarely needed with named functions
    value: parser.name || 'outputParser',
    enumerable: true,
    writable: false,
  });
  Object.defineProperty(outputParser, 'formattingInstructions', {
    value: formattingInstructions,
    enumerable: true,
    writable: false,
  });

  return outputParser;
}

/**
 * Check if an object is an OutputParser.
 *
 * This is a type guard function that narrows the type of `obj` to
 * `OutputParser<unknown>` when it returns true.
 *
 * @param obj - The object to check.
 * @returns True if the object is an OutputParser, false otherwise.
 */
export function isOutputParser(obj: unknown): obj is OutputParser<unknown> {
  return (
    typeof obj === 'function' &&
    '__outputParserType' in obj &&
    (obj as OutputParser).__outputParserType === OUTPUT_PARSER_TYPE
  );
}
