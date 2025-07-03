/**
 * @fileoverview The `defineCall` function for turning `Prompt` functions into LLM calls.
 */

import type { BaseClient, BaseParams } from "../clients";
import type {
  ANTHROPIC_REGISTERED_LLMS,
  GOOGLE_REGISTERED_LLMS,
  OPENAI_REGISTERED_LLMS,
  REGISTERED_LLMS,
  AnthropicClient,
  AnthropicParams,
  GoogleClient,
  GoogleParams,
  OpenAIClient,
  OpenAIParams,
} from "../clients";
import type {
  AsyncPrompt,
  Prompt,
} from "../prompts";
import { AsyncCall } from "./async-call";
import { Call } from "./call";

// Overloads for Anthropic
export function defineCall<P extends any[]>(
  model: ANTHROPIC_REGISTERED_LLMS,
  options: {
    tools?: ToolDef[] | null;
    client?: AnthropicClient | null;
  } & Partial<AnthropicParams>,
  fn: Prompt<P>
): Call<P>;

export function defineCall<P extends any[]>(
  model: ANTHROPIC_REGISTERED_LLMS,
  options: {
    tools?: ToolDef[] | null;
    client?: AnthropicClient | null;
  } & Partial<AnthropicParams>,
  fn: AsyncPrompt<P>
): AsyncCall<P>;

export function defineCall<P extends any[]>(
  model: ANTHROPIC_REGISTERED_LLMS,
  fn: Prompt<P>
): Call<P>;

export function defineCall<P extends any[]>(
  model: ANTHROPIC_REGISTERED_LLMS,
  fn: AsyncPrompt<P>
): AsyncCall<P>;

// Overloads for Google
export function defineCall<P extends any[]>(
  model: GOOGLE_REGISTERED_LLMS,
  options: {
    tools?: ToolDef[] | null;
    client?: GoogleClient | null;
  } & Partial<GoogleParams>,
  fn: Prompt<P>
): Call<P>;

export function defineCall<P extends any[]>(
  model: GOOGLE_REGISTERED_LLMS,
  options: {
    tools?: ToolDef[] | null;
    client?: GoogleClient | null;
  } & Partial<GoogleParams>,
  fn: AsyncPrompt<P>
): AsyncCall<P>;

export function defineCall<P extends any[]>(
  model: GOOGLE_REGISTERED_LLMS,
  fn: Prompt<P>
): Call<P>;

export function defineCall<P extends any[]>(
  model: GOOGLE_REGISTERED_LLMS,
  fn: AsyncPrompt<P>
): AsyncCall<P>;

// Overloads for OpenAI
export function defineCall<P extends any[]>(
  model: OPENAI_REGISTERED_LLMS,
  options: {
    tools?: ToolDef[] | null;
    client?: OpenAIClient | null;
  } & Partial<OpenAIParams>,
  fn: Prompt<P>
): Call<P>;

export function defineCall<P extends any[]>(
  model: OPENAI_REGISTERED_LLMS,
  options: {
    tools?: ToolDef[] | null;
    client?: OpenAIClient | null;
  } & Partial<OpenAIParams>,
  fn: AsyncPrompt<P>
): AsyncCall<P>;

export function defineCall<P extends any[]>(
  model: OPENAI_REGISTERED_LLMS,
  fn: Prompt<P>
): Call<P>;

export function defineCall<P extends any[]>(
  model: OPENAI_REGISTERED_LLMS,
  fn: AsyncPrompt<P>
): AsyncCall<P>;

// Overloads for all registered models
export function defineCall<P extends any[]>(
  model: REGISTERED_LLMS,
  options: {
    tools?: ToolDef[] | null;
    client?: BaseClient | null;
  } & Partial<BaseParams>,
  fn: Prompt<P>
): Call<P>;

export function defineCall<P extends any[]>(
  model: REGISTERED_LLMS,
  options: {
    tools?: ToolDef[] | null;
    client?: BaseClient | null;
  } & Partial<BaseParams>,
  fn: AsyncPrompt<P>
): AsyncCall<P>;

export function defineCall<P extends any[]>(
  model: REGISTERED_LLMS,
  fn: Prompt<P>
): Call<P>;

export function defineCall<P extends any[]>(
  model: REGISTERED_LLMS,
  fn: AsyncPrompt<P>
): AsyncCall<P>;

/**
 * Turns a prompt template function into an LLM call.
 *
 * @param model The model identifier (e.g., "openai:gpt-4o-mini")
 * @param optionsOrFn Either configuration options or the prompt function
 * @param fn The prompt function (when options are provided)
 * @returns A Call or AsyncCall instance based on the function type
 *
 * @example
 * ```typescript
 * const answerQuestion = defineCall("openai:gpt-4o-mini", (question: string) => {
 *   return `Answer this question: ${question}`;
 * });
 * 
 * const response = answerQuestion.call("What is the capital of France?");
 * console.log(response.text);
 * ```
 * 
 * @example
 * ```typescript
 * const answerQuestion = defineCall("openai:gpt-4o-mini", {
 *   temperature: 0.7,
 *   tools: [someTool]
 * }, (question: string) => {
 *   return `Answer this question: ${question}`;
 * });
 * ```
 */
export function defineCall<P extends any[]>(
  model: REGISTERED_LLMS,
  optionsOrFn: 
    | ({ tools?: ToolDef[] | null; client?: BaseClient | null } & Partial<BaseParams>)
    | Prompt<P>
    | AsyncPrompt<P>,
  fn?: Prompt<P> | AsyncPrompt<P>
): Call<P> | AsyncCall<P> {
  // Handle overloaded parameters
  const options = typeof optionsOrFn === 'function' ? {} : optionsOrFn;
  const promptFn = typeof optionsOrFn === 'function' ? optionsOrFn : fn!;
  
  // Create the model instance from the model string
  const llmModel = createModelFromString(model, options);
  
  // Determine if it's async or sync based on the function
  const isAsync = isAsyncPrompt(promptFn);
  
  if (isAsync) {
    return new AsyncCall(llmModel, options.tools || null, promptFn as AsyncPrompt<P>);
  } else {
    return new Call(llmModel, options.tools || null, promptFn as Prompt<P>);
  }
}

/**
 * Helper function to create a model instance from a model string.
 */
function createModelFromString(
  model: REGISTERED_LLMS,
  options: { client?: BaseClient | null } & Partial<BaseParams>
): any {
  // Implementation needed - parse provider:model and create appropriate instance
  throw new Error("Not implemented");
}

/**
 * Helper function to determine if a function is async.
 */
function isAsyncPrompt<P extends any[]>(
  fn: Prompt<P> | AsyncPrompt<P>
): fn is AsyncPrompt<P> {
  return fn.constructor.name === 'AsyncFunction';
}
