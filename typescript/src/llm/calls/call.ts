/**
 * Call definition and creation utilities.
 *
 * A Call is a Prompt with a bundled Model - it can be invoked directly
 * without passing a model argument.
 */

import { Model } from '@/llm/models';
import type { Params } from '@/llm/models/params';
import { definePrompt, type Prompt, type TemplateFunc } from '@/llm/prompts';
import type { ModelId } from '@/llm/providers/model-id';
import type { Response } from '@/llm/responses';
import type { NoVars } from '@/llm/types';

/**
 * Arguments for defining a call.
 *
 * @template T - The type of variables the template accepts. Defaults to NoVars.
 */
export interface CallArgs<T = NoVars> extends Params {
  /** The model to use, either a Model instance or model ID string. */
  model: Model | ModelId;
  /** A function that generates message content (optionally from variables). */
  template: TemplateFunc<T>;
}

/**
 * A call that can be invoked directly to generate a response.
 *
 * Created by `defineCall()`. Unlike a `Prompt`, a `Call` has a model bundled in,
 * so it can be invoked without passing a model argument.
 *
 * @template T - The type of variables the call accepts. Defaults to empty object.
 *
 * @example With variables
 * ```typescript
 * const recommendBook = defineCall<{ genre: string }>({
 *   model: 'anthropic/claude-sonnet-4-20250514',
 *   template: ({ genre }) => `Recommend a ${genre} book`,
 * });
 *
 * const response = await recommendBook({ genre: 'fantasy' });
 * ```
 *
 * @example Without variables
 * ```typescript
 * const sayHello = defineCall({
 *   model: 'anthropic/claude-sonnet-4-20250514',
 *   template: () => 'Hello!',
 * });
 * const response = await sayHello();
 * ```
 */
export interface Call<T = NoVars> {
  /**
   * Call directly to generate a response (model is bundled).
   *
   * @param vars - The variables to pass to the template.
   * @returns A promise that resolves to the LLM response.
   */
  (...args: keyof T extends never ? [] : [vars: T]): Promise<Response>;

  /**
   * The bundled model.
   */
  readonly model: Model;

  /**
   * The underlying prompt.
   */
  readonly prompt: Prompt<T>;

  /**
   * The underlying template function.
   */
  readonly template: TemplateFunc<T>;
}

/**
 * Define a call without variables.
 *
 * @param args - The call arguments including model, template, and optional parameters.
 * @returns A callable that can be invoked directly.
 *
 * @example
 * ```typescript
 * const sayHello = defineCall({
 *   model: 'anthropic/claude-sonnet-4-20250514',
 *   template: () => 'Hello!',
 * });
 * const response = await sayHello();
 * ```
 */
export function defineCall(args: CallArgs<NoVars>): Call<NoVars>;

/**
 * Define a call with variables that can be invoked directly to generate a response.
 *
 * @template T - The type of variables the template accepts.
 * @param args - The call arguments including model, template, and optional parameters.
 * @returns A callable that can be invoked directly with variables.
 *
 * @example Simple string template
 * ```typescript
 * const recommendBook = defineCall<{ genre: string }>({
 *   model: 'anthropic/claude-sonnet-4-20250514',
 *   template: ({ genre }) => `Recommend a ${genre} book`,
 * });
 *
 * const response = await recommendBook({ genre: 'fantasy' });
 * ```
 *
 * @example With model parameters
 * ```typescript
 * const recommendBook = defineCall<{ genre: string }>({
 *   model: 'anthropic/claude-sonnet-4-20250514',
 *   temperature: 0.7,
 *   maxTokens: 1000,
 *   template: ({ genre }) => `Recommend a ${genre} book`,
 * });
 * ```
 *
 * @example With message array
 * ```typescript
 * import { system, user } from 'mirascope/llm/messages';
 *
 * const chatBot = defineCall<{ question: string }>({
 *   model: 'anthropic/claude-sonnet-4-20250514',
 *   template: ({ question }) => [
 *     system('You are a helpful assistant.'),
 *     user(question),
 *   ],
 * });
 * ```
 */
export function defineCall<T extends Record<string, unknown>>(
  args: CallArgs<T>
): Call<T>;

// Implementation
export function defineCall<T>({
  model,
  template,
  ...params
}: CallArgs<T>): Call<T> {
  if (typeof model !== 'string' && Object.keys(params).length > 0) {
    throw new Error(
      'Cannot pass params when model is a Model instance. Use new Model(id, params) instead.'
    );
  }

  const resolvedModel: Model =
    typeof model === 'string' ? new Model(model, params) : model;

  const prompt = definePrompt<T>({ template });

  const call = async (
    ...vars: keyof T extends never ? [] : [vars: T]
  ): Promise<Response> => {
    return prompt(resolvedModel, ...vars);
  };

  return Object.assign(call, {
    model: resolvedModel,
    prompt,
    template,
  }) as Call<T>;
}
