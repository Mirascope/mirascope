/**
 * Call definition and creation utilities.
 *
 * A Call is a Prompt with a bundled Model - it can be invoked directly
 * without passing a model argument.
 *
 * This module provides a unified `defineCall` function that automatically
 * detects whether a call is context-aware based on the template type parameter.
 * If T includes `ctx: Context<DepsT>`, a ContextCall is returned; otherwise
 * a regular Call is returned.
 */

import type {
  AnyFormatInput,
  ExtractFormatType,
  FormatInput,
  Format,
  FormatSpec,
  OutputParser,
} from "@/llm/formatting";
import type { Params } from "@/llm/models/params";
import type { ModelId } from "@/llm/providers/model-id";
import type { Response } from "@/llm/responses";
import type { ContextResponse } from "@/llm/responses/context-response";
import type { ContextStreamResponse } from "@/llm/responses/context-stream-response";
import type { StreamResponse } from "@/llm/responses/stream-response";
import type { ContextTools, Tools, ZodLike } from "@/llm/tools";
import type { NoVars } from "@/llm/types";

import { type Context, isContext } from "@/llm/context";
import { Model, useModel } from "@/llm/models";
import {
  definePrompt,
  type ContextPrompt,
  type ContextTemplateFunc,
  type ExtractDeps,
  type ExtractVars,
  type Prompt,
  type PromptArgs,
  type TemplateFunc,
} from "@/llm/prompts";

// ============================================================================
// Call Args Types
// ============================================================================

/**
 * Arguments for defining a call.
 *
 * @template T - The type of variables the template accepts. Defaults to NoVars.
 * @template F - The format input type. The output type F is derived via ExtractFormatType<F>.
 */
export interface CallArgs<
  T = NoVars,
  F extends AnyFormatInput = undefined,
> extends Params {
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
 * Arguments for defining a context-aware call.
 * Used when T includes `ctx: Context<DepsT>`.
 *
 * @template T - The full template parameter type including ctx.
 * @template F - The format input type.
 */
export interface ContextCallArgs<
  T = NoVars,
  F extends AnyFormatInput = undefined,
> extends Params {
  /** The model to use, either a Model instance or model ID string. */
  model: Model | ModelId;
  /** Optional tools to make available to the model. */
  tools?: ExtractDeps<T> extends never ? Tools : ContextTools<ExtractDeps<T>>;
  /**
   * Optional format specification for structured output.
   * Can be a Zod schema, Format, FormatSpec, or OutputParser.
   */
  format?: F;
  /** A function that generates message content from context (and optionally variables). */
  template: TemplateFunc<T>;
}

// ============================================================================
// Call Interface (Non-Context)
// ============================================================================

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

// ============================================================================
// Context Call Interface
// ============================================================================

/**
 * A context-aware call that can be invoked directly with a context to generate a response.
 *
 * Created by `defineCall()` when the template type includes `ctx: Context<DepsT>`.
 * Unlike a `ContextPrompt`, a `ContextCall` has a model bundled in, so it can be
 * invoked without passing a model argument.
 *
 * @template T - The type of variables the call accepts. Defaults to empty object.
 * @template DepsT - The type of dependencies in the context.
 * @template F - The format input type. The output type is derived via ExtractFormatType<F>.
 *
 * @example With variables
 * ```typescript
 * interface MyDeps { userId: string; }
 *
 * const greetUser = defineCall<{ ctx: Context<MyDeps>; greeting: string }>({
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
 * const sayHello = defineCall<{ ctx: Context<MyDeps> }>({
 *   model: 'anthropic/claude-sonnet-4-20250514',
 *   template: ({ ctx }) => `Hello, user ${ctx.deps.userId}!`,
 * });
 *
 * const ctx = createContext<MyDeps>({ userId: '123' });
 * const response = await sayHello(ctx);
 * ```
 */
export interface ContextCall<
  T = NoVars,
  DepsT = unknown,
  F extends AnyFormatInput = undefined,
> {
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
  ): Promise<ContextResponse<DepsT, ExtractFormatType<F>>>;

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
  ): Promise<ContextResponse<DepsT, ExtractFormatType<F>>>;

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
  ): Promise<ContextStreamResponse<DepsT, ExtractFormatType<F>>>;

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
    | Format<ExtractFormatType<F>>
    | FormatSpec<ExtractFormatType<F>>
    | ZodLike
    | OutputParser<ExtractFormatType<F>>
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

// ============================================================================
// Unified Call Type
// ============================================================================

/**
 * Unified call type that returns either Call or ContextCall
 * based on whether T includes `ctx: Context<DepsT>`.
 */
export type UnifiedCall<T, F extends AnyFormatInput = undefined> =
  ExtractDeps<T> extends never
    ? Call<T, F>
    : ContextCall<ExtractVars<T>, ExtractDeps<T>, F>;

/**
 * A builder function returned when defineCall is called with only a type parameter.
 * Allows specifying the variables type explicitly while inferring the format type.
 *
 * @template T - The type of variables the call accepts (may include ctx for context calls).
 */
export interface CallBuilder<T extends Record<string, unknown>> {
  <F extends AnyFormatInput = undefined>(
    args: CallArgs<T, F> | ContextCallArgs<T, F>,
  ): UnifiedCall<T, F>;
}

// ============================================================================
// Core Implementation
// ============================================================================

// Core implementation - separated to avoid overload matching issues with curried calls
function createCall<T, F extends AnyFormatInput>({
  model,
  tools,
  format,
  template,
  ...params
}: CallArgs<T, F> | ContextCallArgs<T, F>): UnifiedCall<T, F> {
  if (typeof model !== "string" && Object.keys(params).length > 0) {
    throw new Error(
      "Cannot pass params when model is a Model instance. Use new Model(id, params) instead.",
    );
  }

  // Resolve the default model at definition time (bakes in params)
  const defaultModel: Model =
    typeof model === "string" ? new Model(model, params) : model;

  // Create the unified prompt (it handles both context and non-context cases)
  const prompt = definePrompt({ tools, format, template } as PromptArgs<
    T & Record<string, unknown>,
    F
  >);

  // Create call function that handles both context and non-context cases
  // We use type assertions here because the unified prompt handles runtime detection
  const callImpl = async (
    ...args: unknown[]
  ): Promise<
    | Response<ExtractFormatType<F>>
    | ContextResponse<unknown, ExtractFormatType<F>>
  > => {
    const firstArg = args[0];

    if (isContext(firstArg)) {
      // Context case: call(ctx, vars?)
      const ctx = firstArg;
      const vars = args[1] as ExtractVars<T> | undefined;
      // Use the prompt's internal implementation which handles both cases
      const contextPrompt = prompt as unknown as {
        call(
          model: Model,
          ctx: Context<unknown>,
          vars?: ExtractVars<T>,
        ): Promise<ContextResponse<unknown, ExtractFormatType<F>>>;
      };
      return contextPrompt.call(useModel(defaultModel), ctx, vars);
    } else {
      // Non-context case: call(vars?)
      const vars = firstArg as T | undefined;
      const regularPrompt = prompt as unknown as {
        call(model: Model, vars?: T): Promise<Response<ExtractFormatType<F>>>;
      };
      return regularPrompt.call(useModel(defaultModel), vars);
    }
  };

  // Create callable wrapper
  const callable = async (
    ...args: unknown[]
  ): Promise<
    | Response<ExtractFormatType<F>>
    | ContextResponse<unknown, ExtractFormatType<F>>
  > => {
    return callImpl(...args);
  };

  // Create stream function
  const streamImpl = async (
    ...args: unknown[]
  ): Promise<
    | StreamResponse<ExtractFormatType<F>>
    | ContextStreamResponse<unknown, ExtractFormatType<F>>
  > => {
    const firstArg = args[0];

    if (isContext(firstArg)) {
      // Context case: stream(ctx, vars?)
      const ctx = firstArg;
      const vars = args[1] as ExtractVars<T> | undefined;
      const contextPrompt = prompt as unknown as {
        stream(
          model: Model,
          ctx: Context<unknown>,
          vars?: ExtractVars<T>,
        ): Promise<ContextStreamResponse<unknown, ExtractFormatType<F>>>;
      };
      return contextPrompt.stream(useModel(defaultModel), ctx, vars);
    } else {
      // Non-context case: stream(vars?)
      const vars = firstArg as T | undefined;
      const regularPrompt = prompt as unknown as {
        stream(
          model: Model,
          vars?: T,
        ): Promise<StreamResponse<ExtractFormatType<F>>>;
      };
      return regularPrompt.stream(useModel(defaultModel), vars);
    }
  };

  const definedCall = Object.assign(callable, {
    defaultModel,
    call: callImpl,
    stream: streamImpl,
    tools,
    format,
    prompt,
    template,
  });

  Object.defineProperty(definedCall, "model", {
    get: () => useModel(defaultModel),
    enumerable: true,
  });

  return definedCall as unknown as UnifiedCall<T, F>;
}

// ============================================================================
// defineCall Function Overloads
// ============================================================================

/**
 * Define a call with explicit variables type, returning a builder that infers format.
 *
 * This overload enables specifying the variables type upfront while still allowing
 * the format type to be inferred from the `format` property.
 *
 * @template T - The type of variables the template accepts (may include ctx for context calls).
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
 *
 * @example Context-aware call with explicit type
 * ```typescript
 * interface MyDeps { userId: string; }
 *
 * const greetUser = defineCall<{ ctx: Context<MyDeps>; greeting: string }>()({
 *   model: 'anthropic/claude-sonnet-4-20250514',
 *   template: ({ ctx, greeting }) => `${greeting}, user ${ctx.deps.userId}!`,
 * });
 *
 * const ctx = createContext<MyDeps>({ userId: '123' });
 * const response = await greetUser(ctx, { greeting: 'Hello' });
 * ```
 */
export function defineCall<T extends Record<string, unknown>>(): CallBuilder<T>;

/**
 * Define a call that automatically detects context from the template type.
 *
 * When T includes `ctx: Context<DepsT>`, returns a ContextCall.
 * Otherwise returns a regular Call.
 *
 * Both the variables type and format type are inferred from the arguments.
 * Type the template parameter to enable variables inference.
 *
 * @template T - The type of variables the template accepts (may include ctx for context calls).
 * @template F - The format input type (inferred from format property).
 * @param args - The call arguments including model, template, and optional parameters.
 * @returns A callable that can be invoked directly with variables (and context if T includes ctx).
 *
 * @example Call without variables
 * ```typescript
 * const sayHello = defineCall({
 *   model: 'anthropic/claude-sonnet-4-20250514',
 *   template: () => 'Hello!',
 * });
 * const response = await sayHello();
 * ```
 *
 * @example Regular call with variables
 * ```typescript
 * const recommendBook = defineCall({
 *   model: 'anthropic/claude-sonnet-4-20250514',
 *   format: defineFormat<Book>({ mode: 'tool' }),
 *   template: ({ genre }: { genre: string }) => `Recommend a ${genre} book`,
 * });
 * const response = await recommendBook({ genre: 'fantasy' });
 * ```
 *
 * @example Context-aware call
 * ```typescript
 * interface MyDeps { userId: string; }
 *
 * const greetUser = defineCall({
 *   model: 'anthropic/claude-sonnet-4-20250514',
 *   template: ({ ctx, greeting }: { ctx: Context<MyDeps>; greeting: string }) =>
 *     `${greeting}, user ${ctx.deps.userId}!`,
 * });
 *
 * const ctx = createContext<MyDeps>({ userId: '123' });
 * const response = await greetUser(ctx, { greeting: 'Hello' });
 * ```
 */
export function defineCall<
  T extends Record<string, unknown> = NoVars,
  F extends AnyFormatInput = undefined,
>(args: CallArgs<T, F> | ContextCallArgs<T, F>): UnifiedCall<T, F>;

// ============================================================================
// Implementation
// ============================================================================

// Implementation
export function defineCall<T, F extends AnyFormatInput>(
  args?: CallArgs<T, F> | ContextCallArgs<T, F>,
): UnifiedCall<T, F> | CallBuilder<T & Record<string, unknown>> {
  // If no args provided, return a builder function for curried usage
  if (args === undefined) {
    return (<F2 extends AnyFormatInput = undefined>(
      builderArgs: CallArgs<T, F2> | ContextCallArgs<T, F2>,
    ): UnifiedCall<T, F2> => {
      return createCall(builderArgs);
    }) as CallBuilder<T & Record<string, unknown>>;
  }

  return createCall(args);
}
