/**
 * @fileoverview The model context manager for the `llm` module.
 */

import type { BaseClient } from "../clients";
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
import type { Anthropic, Google, OpenAI } from "../models";
import { LLM } from "./base";
import type { BaseParams } from '../clients';

// Global context variable to store the current model
// NOTE: this is not threadsafe and will likely need an update
let MODEL_CONTEXT: LLM | null = null;

/**
 * Context manager for setting the model context with automatic cleanup.
 * 
 * Since TypeScript doesn't have context managers like Python, we implement this
 * as a function that takes a callback and automatically handles cleanup.
 * 
 * ```typescript
 * await useModel("openai:gpt-4", { temperature: 0.7 }, async (model) => {
 *   // Use the model here - it's automatically set in the global context
 *   const response = await someFunction();
 *   return response;
 * }); // Context is automatically restored when this completes
 * ```
 */

// Overloads for type safety
export async function useModelAsync<T>(
  id: ANTHROPIC_REGISTERED_LLMS,
  options: {
    client?: AnthropicClient | null;
  } & Partial<AnthropicParams>,
  fn: (model: Anthropic) => Promise<T>
): Promise<T>;

export async function useModelAsync<T>(
  id: GOOGLE_REGISTERED_LLMS,
  options: {
    client?: GoogleClient | null;
  } & Partial<GoogleParams>,
  fn: (model: Google) => Promise<T>
): Promise<T>;

export async function useModelAsync<T>(
  id: OPENAI_REGISTERED_LLMS,
  options: {
    client?: OpenAIClient | null;
  } & Partial<OpenAIParams>,
  fn: (model: OpenAI) => Promise<T>
): Promise<T>;

// Convenience overloads without options
export async function useModelAsync<T>(
  id: ANTHROPIC_REGISTERED_LLMS,
  fn: (model: Anthropic) => Promise<T>
): Promise<T>;

export async function useModelAsync<T>(
  id: GOOGLE_REGISTERED_LLMS,
  fn: (model: Google) => Promise<T>
): Promise<T>;

export async function useModelAsync<T>(
  id: OPENAI_REGISTERED_LLMS,
  fn: (model: OpenAI) => Promise<T>
): Promise<T>;

export async function useModelAsync<T>(
  id: REGISTERED_LLMS,
  fn: (model: LLM) => Promise<T>
): Promise<T>;

/**
 * Set the model context with the model of the given id and automatically handle cleanup.
 *
 * Any call to a function decorated with `@llm.call` will attempt to use the model
 * that's set in the model context first. If no model is set in the context, the
 * default model will be used.
 *
 * This is useful for overriding the default model at runtime.
 *
 * @param id The id of the model in format "provider:name" (e.g., "openai:gpt-4").
 * @param optionsOrFn Either options object or the function to execute (when options are omitted).
 * @param fn Function to execute with the model context set (when options are provided).
 * @returns Promise that resolves to the function's return value.
 *
 * @example
 * ```typescript
 * // With options
 * const result = await useModel("anthropic:claude-3-5-sonnet-latest", {
 *   temperature: 0.7
 * }, async (model) => {
 *   const response = await answerQuestion("What is the capital of France?");
 *   console.log(response.content);
 *   return response;
 * });
 * 
 * // Without options
 * const result = await useModel("openai:gpt-4", async (model) => {
 *   const response = await answerQuestion("What is the capital of France?");
 *   return response;
 * });
 * ```
 */
export async function useModelAsync<T>(
  id: REGISTERED_LLMS,
  optionsOrFn: 
    | ({ client?: BaseClient | null } & Partial<BaseParams>)
    | ((model: LLM) => Promise<T>),
  fn?: (model: LLM) => Promise<T>
): Promise<T> {
  throw new Error('Not implemented');
}

/**
 * Set the model context with the model of the given id and automatically handle cleanup.
 *
 * Any call to a function defined with `llm.defineCall` will attempt to use the model
 * that's set in the model context first. If no model is set in the context, the
 * default model will be used.
 *
 * This is useful for overriding the default model at runtime.
 *
 * @param id The id of the model in format "provider:name" (e.g., "openai:gpt-4").
 * @param optionsOrFn Either options object or the function to execute (when options are omitted).
 * @param fn Function to execute with the model context set (when options are provided).
 * @returns Promise that resolves to the function's return value.
 *
 * @example
 * ```typescript
 * // With options
 * const result = useModel("anthropic:claude-3-5-sonnet-latest", {
 *   temperature: 0.7
 * }, (model) => {
 *   const response = answerQuestion("What is the capital of France?");
 *   console.log(response.content);
 *   return response;
 * });
 * 
 * // Without options
 * const result = useModel("openai:gpt-4", (model) => {
 *   const response = answerQuestion("What is the capital of France?");
 *   return response;
 * });
 * ```
 */

// Overloads for type safety
export function useModel<T>(
  id: ANTHROPIC_REGISTERED_LLMS,
  options: {
    client?: AnthropicClient | null;
  } & Partial<AnthropicParams>,
  fn: (model: Anthropic) => T
): T;

export function useModel<T>(
  id: GOOGLE_REGISTERED_LLMS,
  options: {
    client?: GoogleClient | null;
  } & Partial<GoogleParams>,
  fn: (model: Google) => T
): T;

export function useModel<T>(
  id: OPENAI_REGISTERED_LLMS,
  options: {
    client?: OpenAIClient | null;
  } & Partial<OpenAIParams>,
  fn: (model: OpenAI) => T
): T;

// Convenience overloads without options
export function useModel<T>(
  id: ANTHROPIC_REGISTERED_LLMS,
  fn: (model: Anthropic) => T
): T;

export function useModel<T>(
  id: GOOGLE_REGISTERED_LLMS,
  fn: (model: Google) => T
): T;

export function useModel<T>(
  id: OPENAI_REGISTERED_LLMS,
  fn: (model: OpenAI) => T
): T;

export function useModel<T>(
  id: REGISTERED_LLMS,
  fn: (model: LLM) => T
): T;

export function useModel<T>(
  id: REGISTERED_LLMS,
  optionsOrFn: 
    | ({ client?: BaseClient | null } & Partial<BaseParams>)
    | ((model: LLM) => T),
  fn?: (model: LLM) => T
): T {
  throw new Error("Not implemented")
}

/**
 * Get the current model from context.
 */
export function getCurrentModel(): LLM | null {
  return MODEL_CONTEXT;
}
