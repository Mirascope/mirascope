/**
 * Call definition and creation utilities.
 *
 * A Call is a Prompt with a bundled Model - it can be invoked directly
 * without passing a model argument.
 */

import type {
  AnyFormatInput,
  ExtractFormatType,
  FormatInput,
} from '@/llm/formatting';
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
 * @template F - The format input type. The output type F is derived via ExtractFormatType<F>.
 */
export interface CallArgs<T = NoVars, F extends AnyFormatInput = undefined>
  extends Params {
  /** The model to use, either a Model instance or model ID string. */
  model: Model | ModelId;
  /** Optional tools to make available to the model. */
  tools?: Tools;
  /**
   * Optional format specification for structured output.
   * Can be a Zod schema, Format, FormatSpec, or OutputParser.
   * The output type is automatically inferred from this format.
   */
  format?: F;
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
 * @template F - The format input type. The output type F is derived via ExtractFormatType<F>.
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
export interface Call<T = NoVars, F extends AnyFormatInput = undefined> {
  /**
   * Call directly to generate a response (model is bundled).
   *
   * @param vars - The variables to pass to the template.
   * @returns A promise that resolves to the LLM response.
   */
  (
    ...args: keyof T extends never ? [] : [vars: T]
  ): Promise<Response<ExtractFormatType<F>>>;

  /**
   * Call directly to generate a response (model is bundled).
   * This is the method form of the callable interface.
   *
   * @param vars - The variables to pass to the template.
   * @returns A promise that resolves to the LLM response.
   */
  call(
    ...args: keyof T extends never ? [] : [vars: T]
  ): Promise<Response<ExtractFormatType<F>>>;

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
  ): Promise<StreamResponse<ExtractFormatType<F>>>;

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
   * The format specification for structured output, if any.
   */
  readonly format: FormatInput<ExtractFormatType<F>>;

  /**
   * The underlying prompt.
   */
  readonly prompt: Prompt<T, F>;

  /**
   * The underlying template function.
   */
  readonly template: TemplateFunc<T>;
}

/**
 * A builder function returned when defineCall is called with only a type parameter.
 * Allows specifying the variables type explicitly while inferring the format type.
 *
 * @template T - The type of variables the call accepts.
 */
export interface CallBuilder<T extends Record<string, unknown>> {
  <F extends AnyFormatInput = undefined>(args: CallArgs<T, F>): Call<T, F>;
}

// Core implementation - separated to avoid overload matching issues with curried calls
function createCall<T, F extends AnyFormatInput>({
  model,
  tools,
  format,
  template,
  ...params
}: CallArgs<T, F>): Call<T, F> {
  if (typeof model !== 'string' && Object.keys(params).length > 0) {
    throw new Error(
      'Cannot pass params when model is a Model instance. Use new Model(id, params) instead.'
    );
  }

  // Resolve the default model at definition time (bakes in params)
  const defaultModel: Model =
    typeof model === 'string' ? new Model(model, params) : model;

  const prompt = definePrompt<T, F>({ tools, format, template });

  const call = async (
    ...vars: keyof T extends never ? [] : [vars: T]
  ): Promise<Response<ExtractFormatType<F>>> => {
    return prompt.call(useModel(defaultModel), ...vars);
  };

  const callable = async (
    ...vars: keyof T extends never ? [] : [vars: T]
  ): Promise<Response<ExtractFormatType<F>>> => {
    return call(...vars);
  };

  const stream = async (
    ...vars: keyof T extends never ? [] : [vars: T]
  ): Promise<StreamResponse<ExtractFormatType<F>>> => {
    return prompt.stream(useModel(defaultModel), ...vars);
  };

  const definedCall = Object.assign(callable, {
    defaultModel,
    call,
    stream,
    tools,
    format,
    prompt,
    template,
  });

  Object.defineProperty(definedCall, 'model', {
    get: () => useModel(defaultModel),
    enumerable: true,
  });

  return definedCall as Call<T, F>;
}

/**
 * Define a call with explicit variables type, returning a builder that infers format.
 *
 * This overload enables specifying the variables type upfront while still allowing
 * the format type to be inferred from the `format` property.
 *
 * @template T - The type of variables the template accepts.
 * @returns A builder function that accepts call arguments and infers the format type.
 *
 * @example With explicit variables and inferred format
 * ```typescript
 * const recommendBook = defineCall<{ genre: string }>()({
 *   model: 'anthropic/claude-sonnet-4-20250514',
 *   format: defineFormat<Book>({ mode: 'tool' }),
 *   template: ({ genre }) => `Recommend a ${genre} book`,
 * });
 *
 * const response = await recommendBook({ genre: 'fantasy' });
 * const book = response.parse(); // Typed as Book
 * ```
 */
export function defineCall<T extends Record<string, unknown>>(): CallBuilder<T>;

/**
 * Define a call without variables.
 *
 * @template F - The format input type. The output type is derived via ExtractFormatType<F>.
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
export function defineCall<F extends AnyFormatInput = undefined>(
  args: CallArgs<NoVars, F>
): Call<NoVars, F>;

/**
 * Define a call with variables using full type inference.
 *
 * Both the variables type and format type are inferred from the arguments.
 * Type the template parameter to enable variables inference.
 *
 * @template T - The type of variables the template accepts (inferred from template).
 * @template F - The format input type (inferred from format property).
 * @param args - The call arguments including model, template, and optional parameters.
 * @returns A callable that can be invoked directly with variables.
 *
 * @example Full inference
 * ```typescript
 * const recommendBook = defineCall({
 *   model: 'anthropic/claude-sonnet-4-20250514',
 *   format: defineFormat<Book>({ mode: 'tool' }),
 *   template: ({ genre }: { genre: string }) => `Recommend a ${genre} book`,
 * });
 * ```
 *
 * @example With message array
 * ```typescript
 * import { system, user } from 'mirascope/llm/messages';
 *
 * const chatBot = defineCall({
 *   model: 'anthropic/claude-sonnet-4-20250514',
 *   template: ({ question }: { question: string }) => [
 *     system('You are a helpful assistant.'),
 *     user(question),
 *   ],
 * });
 * ```
 */
export function defineCall<
  T extends Record<string, unknown>,
  F extends AnyFormatInput = undefined,
>(args: CallArgs<T, F>): Call<T, F>;

// Implementation
export function defineCall<T, F extends AnyFormatInput>(
  args?: CallArgs<T, F>
): Call<T, F> | CallBuilder<T & Record<string, unknown>> {
  // If no args provided, return a builder function for curried usage
  if (args === undefined) {
    return (<F2 extends AnyFormatInput = undefined>(
      builderArgs: CallArgs<T, F2>
    ): Call<T, F2> => {
      return createCall(builderArgs);
    }) as CallBuilder<T & Record<string, unknown>>;
  }

  return createCall(args);
}
