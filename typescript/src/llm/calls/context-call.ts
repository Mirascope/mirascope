/**
 * Context-aware call definition and creation utilities.
 *
 * A ContextCall is a ContextPrompt with a bundled Model - it can be invoked
 * directly with just a Context argument (no model needed).
 */

import type { Context } from '@/llm/context';
import type { Format, FormatSpec, OutputParser } from '@/llm/formatting';
import { Model, useModel } from '@/llm/models';
import type { Params } from '@/llm/models/params';
import {
  defineContextPrompt,
  type ContextPrompt,
  type ContextTemplateFunc,
} from '@/llm/prompts';
import type { ModelId } from '@/llm/providers/model-id';
import type { ContextResponse } from '@/llm/responses/context-response';
import type { ContextStreamResponse } from '@/llm/responses/context-stream-response';
import type { ContextTools, ZodLike } from '@/llm/tools';
import type { NoVars } from '@/llm/types';

/**
 * Arguments for defining a context call.
 *
 * @template T - The type of variables the template accepts. Defaults to NoVars.
 * @template DepsT - The type of dependencies in the context.
 * @template F - The type of the formatted output when using structured outputs.
 */
export interface ContextCallArgs<T = NoVars, DepsT = unknown, F = unknown>
  extends Params {
  /** The model to use, either a Model instance or model ID string. */
  model: Model | ModelId;
  /** Optional tools to make available to the model. */
  tools?: ContextTools<DepsT>;
  /**
   * Optional format specification for structured output.
   * Can be a Zod schema, Format, FormatSpec, or OutputParser.
   */
  format?: Format<F> | FormatSpec<F> | ZodLike | OutputParser<F> | null;
  /** A function that generates message content from context (and optionally variables). */
  template: ContextTemplateFunc<T, DepsT>;
}

/**
 * A context-aware call that can be invoked directly with a context to generate a response.
 *
 * Created by `defineContextCall()`. Unlike a `ContextPrompt`, a `ContextCall` has a
 * model bundled in, so it can be invoked without passing a model argument.
 *
 * @template T - The type of variables the call accepts. Defaults to empty object.
 * @template DepsT - The type of dependencies in the context.
 * @template F - The type of the formatted output when using structured outputs.
 *
 * @example With variables
 * ```typescript
 * interface MyDeps { userId: string; }
 *
 * const greetUser = defineContextCall<{ greeting: string }, MyDeps>({
 *   model: 'anthropic/claude-sonnet-4-20250514',
 *   template: ({ ctx, greeting }) => `${greeting}, user ${ctx.deps.userId}!`,
 * });
 *
 * const ctx = createContext<MyDeps>({ userId: '123' });
 * const response = await greetUser(ctx, { greeting: 'Hello' });
 * ```
 *
 * @example Without variables
 * ```typescript
 * interface MyDeps { userId: string; }
 *
 * const sayHello = defineContextCall<NoVars, MyDeps>({
 *   model: 'anthropic/claude-sonnet-4-20250514',
 *   template: ({ ctx }) => `Hello, user ${ctx.deps.userId}!`,
 * });
 *
 * const ctx = createContext<MyDeps>({ userId: '123' });
 * const response = await sayHello(ctx);
 * ```
 */
export interface ContextCall<T = NoVars, DepsT = unknown, F = unknown> {
  /**
   * Call directly with context to generate a response (model is bundled).
   *
   * @param ctx - The context containing dependencies.
   * @param vars - The variables to pass to the template.
   * @returns A promise that resolves to the LLM response.
   */
  (
    ctx: Context<DepsT>,
    ...args: keyof T extends never ? [] : [vars: T]
  ): Promise<ContextResponse<DepsT, F>>;

  /**
   * Call directly with context to generate a response (model is bundled).
   * This is the method form of the callable interface.
   *
   * @param ctx - The context containing dependencies.
   * @param vars - The variables to pass to the template.
   * @returns A promise that resolves to the LLM response.
   */
  call(
    ctx: Context<DepsT>,
    ...args: keyof T extends never ? [] : [vars: T]
  ): Promise<ContextResponse<DepsT, F>>;

  /**
   * Stream directly with context to generate a streaming response (model is bundled).
   *
   * @param ctx - The context containing dependencies.
   * @param vars - The variables to pass to the template.
   * @returns A promise that resolves to the streaming LLM response.
   *
   * @example
   * ```typescript
   * const response = await call.stream(ctx, { greeting: 'Hello' });
   * for await (const text of response.textStream()) {
   *   process.stdout.write(text);
   * }
   * ```
   */
  stream(
    ctx: Context<DepsT>,
    ...args: keyof T extends never ? [] : [vars: T]
  ): Promise<ContextStreamResponse<DepsT, F>>;

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
  readonly tools: ContextTools<DepsT> | undefined;

  /**
   * The format specification for structured output, if any.
   */
  readonly format:
    | Format<F>
    | FormatSpec<F>
    | ZodLike
    | OutputParser<F>
    | null
    | undefined;

  /**
   * The underlying context prompt.
   */
  readonly prompt: ContextPrompt<T, DepsT, F>;

  /**
   * The underlying template function.
   */
  readonly template: ContextTemplateFunc<T, DepsT>;
}

/**
 * Define a context call without variables.
 *
 * @template DepsT - The type of dependencies in the context.
 * @param args - The call arguments including model, template, and optional parameters.
 * @returns A callable that can be invoked directly with a context.
 *
 * @example
 * ```typescript
 * interface MyDeps { userId: string; }
 *
 * const sayHello = defineContextCall<MyDeps>({
 *   model: 'anthropic/claude-sonnet-4-20250514',
 *   template: ({ ctx }) => `Hello, user ${ctx.deps.userId}!`,
 * });
 *
 * const ctx = createContext<MyDeps>({ userId: '123' });
 * const response = await sayHello(ctx);
 * ```
 */
export function defineContextCall<DepsT>(
  args: ContextCallArgs<NoVars, DepsT>
): ContextCall<NoVars, DepsT>;

/**
 * Define a context call with variables that can be invoked directly with a context to generate a response.
 *
 * @template T - The type of variables the template accepts.
 * @template DepsT - The type of dependencies in the context.
 * @template F - The type of the formatted output when using structured outputs.
 * @param args - The call arguments including model, template, and optional parameters.
 * @returns A callable that can be invoked directly with a context and variables.
 *
 * @example Simple string template
 * ```typescript
 * interface MyDeps { userId: string; }
 *
 * const greetUser = defineContextCall<{ greeting: string }, MyDeps>({
 *   model: 'anthropic/claude-sonnet-4-20250514',
 *   template: ({ ctx, greeting }) => `${greeting}, user ${ctx.deps.userId}!`,
 * });
 *
 * const ctx = createContext<MyDeps>({ userId: '123' });
 * const response = await greetUser(ctx, { greeting: 'Hello' });
 * ```
 *
 * @example With model parameters
 * ```typescript
 * interface MyDeps { userId: string; }
 *
 * const greetUser = defineContextCall<{ greeting: string }, MyDeps>({
 *   model: 'anthropic/claude-sonnet-4-20250514',
 *   temperature: 0.7,
 *   maxTokens: 1000,
 *   template: ({ ctx, greeting }) => `${greeting}, user ${ctx.deps.userId}!`,
 * });
 * ```
 *
 * @example With message array
 * ```typescript
 * import { system, user } from 'mirascope/llm/messages';
 *
 * interface MyDeps { systemPrompt: string; }
 *
 * const chatBot = defineContextCall<{ question: string }, MyDeps>({
 *   model: 'anthropic/claude-sonnet-4-20250514',
 *   template: ({ ctx, question }) => [
 *     system(ctx.deps.systemPrompt),
 *     user(question),
 *   ],
 * });
 * ```
 */
export function defineContextCall<
  T extends Record<string, unknown>,
  DepsT = unknown,
  F = unknown,
>(args: ContextCallArgs<T, DepsT, F>): ContextCall<T, DepsT, F>;

// Implementation
export function defineContextCall<T, DepsT, F>({
  model,
  tools,
  format,
  template,
  ...params
}: ContextCallArgs<T, DepsT, F>): ContextCall<T, DepsT, F> {
  if (typeof model !== 'string' && Object.keys(params).length > 0) {
    throw new Error(
      'Cannot pass params when model is a Model instance. Use new Model(id, params) instead.'
    );
  }

  // Resolve the default model at definition time (bakes in params)
  const defaultModel: Model =
    typeof model === 'string' ? new Model(model, params) : model;

  const prompt = defineContextPrompt<T, DepsT, F>({ tools, format, template });

  const call = async (
    ctx: Context<DepsT>,
    ...vars: keyof T extends never ? [] : [vars: T]
  ): Promise<ContextResponse<DepsT, F>> => {
    return prompt.call(useModel(defaultModel), ctx, ...vars);
  };

  const callable = async (
    ctx: Context<DepsT>,
    ...vars: keyof T extends never ? [] : [vars: T]
  ): Promise<ContextResponse<DepsT, F>> => {
    return call(ctx, ...vars);
  };

  const stream = async (
    ctx: Context<DepsT>,
    ...vars: keyof T extends never ? [] : [vars: T]
  ): Promise<ContextStreamResponse<DepsT, F>> => {
    return prompt.stream(useModel(defaultModel), ctx, ...vars);
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

  return definedCall as ContextCall<T, DepsT, F>;
}
