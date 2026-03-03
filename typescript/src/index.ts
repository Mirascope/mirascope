/**
 * Mirascope - LLM abstractions that aren't obstructions.
 *
 * @example
 * ```typescript
 * import { llm, ops } from 'mirascope';
 *
 * // Configure tracing
 * ops.configure({ tracerProvider: provider });
 *
 * // Enable LLM instrumentation
 * ops.instrumentLLM();
 *
 * const recommendBook = llm.defineCall({
 *   model: 'anthropic/claude-haiku-4-5',
 *   maxTokens: 1024,
 *   template: ({ genre }) => `Please recommend a book in ${genre}.`,
 * });
 *
 * const response = await recommendBook({ genre: 'fantasy' });
 * console.log(response.text());
 * ```
 */
import * as llm from "./llm";
import * as ops from "./ops";

export { llm, ops };
