/**
 * Call definition and creation utilities.
 *
 * A Call is a Prompt with a bundled Model - it can be invoked directly
 * without passing a model argument.
 */

import { Model, useModel } from '@/llm/models';
import type { Params } from '@/llm/models/params';
import { definePrompt, type Prompt, type TemplateFunc } from '@/llm/prompts';
import type { ModelId } from '@/llm/providers/model-id';
import type { Response } from '@/llm/responses';
import type { StreamResponse } from '@/llm/responses/stream-response';
import type { Tools } from '@/llm/tools';
import type { NoVars } from '@/llm/types';

/**
 * Arguments for defining a call.
 *
 * @template T - The type of variables the template accepts. Defaults to NoVars.
 */
export interface CallArgs<T = NoVars> extends Params {
  /** The model to use, either a Model instance or model ID string. */
  model: Model | ModelId;
  /** Optional tools to make available to the model. */
  tools?: Tools;
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
   * Call directly to generate a response (model is bundled).
   * This is the method form of the callable interface.
   *
   * @param vars - The variables to pass to the template.
   * @returns A promise that resolves to the LLM response.
   */
  call(...args: keyof T extends never ? [] : [vars: T]): Promise<Response>;

  /**
   * Stream directly to generate a streaming response (model is bundled).
   *
   * @param vars - The variables to pass to the template.
   * @returns A promise that resolves to the streaming LLM response.
   *
   * @example
   * ```typescript
   * const response = await call.stream({ genre: 'fantasy' });
   * for await (const text of response.textStream()) {
   *   process.stdout.write(text);
   * }
   * ```
   */
  stream(
    ...args: keyof T extends never ? [] : [vars: T]
  ): Promise<StreamResponse>;

  /**
   * The model used for generating responses.
   * Returns the context model if one is set via `withModel`, otherwise returns `defaultModel`.
   */
  readonly model: Model;

  /**
   * The default model configured when defining this call.
   * Use `model` to get the effective model (which respects context).
   */
  readonly defaultModel: Model;

  /**
   * The tools available to this call.
   */
  readonly tools: Tools | undefined;

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
  tools,
  template,
  ...params
}: CallArgs<T>): Call<T> {
  if (typeof model !== 'string' && Object.keys(params).length > 0) {
    throw new Error(
      'Cannot pass params when model is a Model instance. Use new Model(id, params) instead.'
    );
  }

  // Resolve the default model at definition time (bakes in params)
  const defaultModel: Model =
    typeof model === 'string' ? new Model(model, params) : model;

  const prompt = definePrompt<T>({ tools, template });

  const call = async (
    ...vars: keyof T extends never ? [] : [vars: T]
  ): Promise<Response> => {
    return prompt.call(useModel(defaultModel), ...vars);
  };

  const callable = async (
    ...vars: keyof T extends never ? [] : [vars: T]
  ): Promise<Response> => {
    return call(...vars);
  };

  const stream = async (
    ...vars: keyof T extends never ? [] : [vars: T]
  ): Promise<StreamResponse> => {
    return prompt.stream(useModel(defaultModel), ...vars);
  };

  const definedCall = Object.assign(callable, {
    defaultModel,
    call,
    stream,
    tools,
    prompt,
    template,
  });

  Object.defineProperty(definedCall, 'model', {
    get: () => useModel(defaultModel),
    enumerable: true,
  });

  return definedCall as Call<T>;
}
