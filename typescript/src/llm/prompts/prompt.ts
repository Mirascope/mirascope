/**
 * Prompt definition and creation utilities.
 *
 * This module provides a unified `definePrompt` function that automatically
 * detects whether a prompt is context-aware based on the template type parameter.
 * If T includes `ctx: Context<DepsT>`, a ContextPrompt is returned; otherwise
 * a regular Prompt is returned.
 */

import type { Message, UserContent } from "@/llm/messages";
import type { ModelId } from "@/llm/providers/model-id";
import type { Response } from "@/llm/responses";
import type { StreamResponse } from "@/llm/responses/stream-response";
import type { ContextTools, Tools, ZodLike } from "@/llm/tools";
import type { NoVars } from "@/llm/types";

import { type Context, isContext } from "@/llm/context";
import {
  resolveFormat,
  type AnyFormatInput,
  type ExtractFormatType,
  type FormatInput,
  type Format,
  type FormatSpec,
  type OutputParser,
} from "@/llm/formatting";
import { promoteToMessages } from "@/llm/messages";
import { Model, useModel } from "@/llm/models";
import { ContextResponse } from "@/llm/responses/context-response";
import { ContextStreamResponse } from "@/llm/responses/context-stream-response";

// ============================================================================
// Type Utilities for Context Detection
// ============================================================================

/**
 * Extract DepsT from T if T has a `ctx: Context<DepsT>` property.
 * Returns `never` if T doesn't have a context property.
 */
export type ExtractDeps<T> = T extends { ctx: Context<infer D> } ? D : never;

/**
 * Extract the variables type from T by removing the `ctx` property.
 */
export type ExtractVars<T> = Omit<T, "ctx">;

// ============================================================================
// Template Types
// ============================================================================

/**
 * A template function that generates message content from variables.
 *
 * @template T - The type of variables the template accepts.
 */
export type MessageTemplate<T> = (vars: T) => UserContent | readonly Message[];

/**
 * Template function type - either takes no args or takes vars of type T.
 */
export type TemplateFunc<T> =
  | (() => UserContent | readonly Message[])
  | ((vars: T) => UserContent | readonly Message[]);

/**
 * The combined context and variables object passed to context template functions.
 *
 * @template T - The type of variables the template accepts.
 * @template DepsT - The type of dependencies in the context.
 */
export type ContextMessageTemplate<T, DepsT> = { ctx: Context<DepsT> } & T;

/**
 * Context template function type - takes an object with ctx and vars.
 *
 * @template T - The type of variables the template accepts.
 * @template DepsT - The type of dependencies in the context.
 */
export type ContextTemplateFunc<T, DepsT> = (
  args: ContextMessageTemplate<T, DepsT>,
) => UserContent | readonly Message[];

// ============================================================================
// Prompt Args Types
// ============================================================================

/**
 * Arguments for defining a prompt.
 *
 * @template T - The type of variables the template accepts. Defaults to NoVars.
 * @template F - The format input type. The output type F is derived via ExtractFormatType<F>.
 */
export interface PromptArgs<T = NoVars, F extends AnyFormatInput = undefined> {
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
 * Arguments for defining a context-aware prompt.
 * Used when T includes `ctx: Context<DepsT>`.
 *
 * @template T - The full template parameter type including ctx.
 * @template F - The format input type.
 */
export interface ContextPromptArgs<
  T = NoVars,
  F extends AnyFormatInput = undefined,
> {
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
// Prompt Interface (Non-Context)
// ============================================================================

/**
 * A prompt that can be called with a model to generate a response.
 *
 * Created by `definePrompt()`. The prompt is callable and also has a
 * `messages()` method for getting the raw messages without calling the LLM.
 *
 * @template T - The type of variables the prompt accepts. Defaults to empty object.
 * @template F - The format input type. The output type F is derived via ExtractFormatType<F>.
 *
 * @example With variables
 * ```typescript
 * const recommendBook = definePrompt<{ genre: string }>({
 *   template: ({ genre }) => `Recommend a ${genre} book`,
 * });
 *
 * const response = await recommendBook(model, { genre: 'fantasy' });
 * const messages = recommendBook.messages({ genre: 'fantasy' });
 * ```
 *
 * @example Without variables
 * ```typescript
 * const sayHello = definePrompt({
 *   template: () => 'Hello!',
 * });
 * const response = await sayHello(model);
 * ```
 */
export interface Prompt<T = NoVars, F extends AnyFormatInput = undefined> {
  /**
   * Call the prompt with a model and variables to generate a response.
   *
   * @param model - The model to use, either a Model instance or model ID string.
   * @param vars - The variables to pass to the template.
   * @returns A promise that resolves to the LLM response.
   */
  (
    model: Model | ModelId,
    ...args: keyof T extends never ? [] : [vars: T]
  ): Promise<Response<ExtractFormatType<F>>>;

  /**
   * Call the prompt with a model and variables to generate a response.
   * This is the method form of the callable interface.
   *
   * @param model - The model to use, either a Model instance or model ID string.
   * @param vars - The variables to pass to the template.
   * @returns A promise that resolves to the LLM response.
   */
  call(
    model: Model | ModelId,
    ...args: keyof T extends never ? [] : [vars: T]
  ): Promise<Response<ExtractFormatType<F>>>;

  /**
   * Stream the prompt with a model and variables to generate a streaming response.
   *
   * @param model - The model to use, either a Model instance or model ID string.
   * @param vars - The variables to pass to the template.
   * @returns A promise that resolves to the streaming LLM response.
   *
   * @example
   * ```typescript
   * const response = await prompt.stream(model, { genre: 'fantasy' });
   * for await (const text of response.textStream()) {
   *   process.stdout.write(text);
   * }
   * ```
   */
  stream(
    model: Model | ModelId,
    ...args: keyof T extends never ? [] : [vars: T]
  ): Promise<StreamResponse<ExtractFormatType<F>>>;

  /**
   * Get the messages for this prompt without calling the LLM.
   *
   * @param vars - The variables to pass to the template.
   * @returns The messages that would be sent to the LLM.
   */
  messages(...args: keyof T extends never ? [] : [vars: T]): readonly Message[];

  /**
   * The tools available to this prompt.
   */
  readonly tools: Tools | undefined;

  /**
   * The format specification for structured output, if any.
   */
  readonly format: FormatInput<ExtractFormatType<F>>;

  /**
   * The underlying template function.
   */
  readonly template: TemplateFunc<T>;
}

// ============================================================================
// Context Prompt Interface
// ============================================================================

/**
 * A context-aware prompt that can be called with a model and context to generate a response.
 *
 * Created by `definePrompt()` when the template type includes `ctx: Context<DepsT>`.
 * The prompt is callable and also has a `messages()` method for getting the raw messages.
 *
 * @template T - The type of variables the prompt accepts. Defaults to empty object.
 * @template DepsT - The type of dependencies in the context.
 * @template F - The format input type. The output type is derived via ExtractFormatType<F>.
 *
 * @example With variables
 * ```typescript
 * interface MyDeps { userId: string; }
 *
 * const greetUser = definePrompt<{ ctx: Context<MyDeps>; greeting: string }>({
 *   template: ({ ctx, greeting }) => `${greeting}, user ${ctx.deps.userId}!`,
 * });
 *
 * const ctx = createContext<MyDeps>({ userId: '123' });
 * const response = await greetUser(model, ctx, { greeting: 'Hello' });
 * const messages = greetUser.messages(ctx, { greeting: 'Hello' });
 * ```
 *
 * @example Without variables
 * ```typescript
 * interface MyDeps { userId: string; }
 *
 * const sayHello = definePrompt<{ ctx: Context<MyDeps> }>({
 *   template: ({ ctx }) => `Hello, user ${ctx.deps.userId}!`,
 * });
 *
 * const response = await sayHello(model, ctx);
 * ```
 */
export interface ContextPrompt<
  T = NoVars,
  DepsT = unknown,
  F extends AnyFormatInput = undefined,
> {
  /**
   * Call the prompt with a model, context, and variables to generate a response.
   *
   * @param model - The model to use, either a Model instance or model ID string.
   * @param ctx - The context containing dependencies.
   * @param vars - The variables to pass to the template.
   * @returns A promise that resolves to the LLM response.
   */
  (
    model: Model | ModelId,
    ctx: Context<DepsT>,
    ...args: keyof T extends never ? [] : [vars: T]
  ): Promise<ContextResponse<DepsT, ExtractFormatType<F>>>;

  /**
   * Call the prompt with a model, context, and variables to generate a response.
   * This is the method form of the callable interface.
   *
   * @param model - The model to use, either a Model instance or model ID string.
   * @param ctx - The context containing dependencies.
   * @param vars - The variables to pass to the template.
   * @returns A promise that resolves to the LLM response.
   */
  call(
    model: Model | ModelId,
    ctx: Context<DepsT>,
    ...args: keyof T extends never ? [] : [vars: T]
  ): Promise<ContextResponse<DepsT, ExtractFormatType<F>>>;

  /**
   * Stream the prompt with a model, context, and variables to generate a streaming response.
   *
   * @param model - The model to use, either a Model instance or model ID string.
   * @param ctx - The context containing dependencies.
   * @param vars - The variables to pass to the template.
   * @returns A promise that resolves to the streaming LLM response.
   *
   * @example
   * ```typescript
   * const response = await prompt.stream(model, ctx, { greeting: 'Hello' });
   * for await (const text of response.textStream()) {
   *   process.stdout.write(text);
   * }
   * ```
   */
  stream(
    model: Model | ModelId,
    ctx: Context<DepsT>,
    ...args: keyof T extends never ? [] : [vars: T]
  ): Promise<ContextStreamResponse<DepsT, ExtractFormatType<F>>>;

  /**
   * Get the messages for this prompt without calling the LLM.
   *
   * @param ctx - The context containing dependencies.
   * @param vars - The variables to pass to the template.
   * @returns The messages that would be sent to the LLM.
   */
  messages(
    ctx: Context<DepsT>,
    ...args: keyof T extends never ? [] : [vars: T]
  ): readonly Message[];

  /**
   * The tools available to this prompt.
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
   * The underlying template function.
   */
  readonly template: ContextTemplateFunc<T, DepsT>;
}

// ============================================================================
// Unified Prompt Type
// ============================================================================

/**
 * Unified prompt type that returns either Prompt or ContextPrompt
 * based on whether T includes `ctx: Context<DepsT>`.
 */
export type UnifiedPrompt<T, F extends AnyFormatInput = undefined> =
  ExtractDeps<T> extends never
    ? Prompt<T, F>
    : ContextPrompt<ExtractVars<T>, ExtractDeps<T>, F>;

// ============================================================================
// definePrompt Function Overloads
// ============================================================================

/**
 * Define a prompt that automatically detects context from the template type.
 *
 * When T includes `ctx: Context<DepsT>`, returns a ContextPrompt.
 * Otherwise returns a regular Prompt.
 *
 * @template T - The type of the template parameter (including ctx if context-aware).
 * @template F - The format input type. The output type is derived via ExtractFormatType<F>.
 * @param args - The prompt arguments including the template.
 * @returns A callable prompt (context-aware if T includes ctx).
 *
 * @example Prompt without variables
 * ```typescript
 * const sayHello = definePrompt({
 *   template: () => 'Hello!',
 * });
 * const response = await sayHello(model);
 * ```
 *
 * @example Regular prompt with variables
 * ```typescript
 * const recommendBook = definePrompt<{ genre: string }>({
 *   template: ({ genre }) => `Recommend a ${genre} book`,
 * });
 * const response = await recommendBook(model, { genre: 'fantasy' });
 * ```
 *
 * @example Context-aware prompt
 * ```typescript
 * interface MyDeps { userId: string; }
 *
 * const greetUser = definePrompt<{ ctx: Context<MyDeps>; greeting: string }>({
 *   template: ({ ctx, greeting }) => `${greeting}, user ${ctx.deps.userId}!`,
 * });
 *
 * const ctx = createContext<MyDeps>({ userId: '123' });
 * const response = await greetUser(model, ctx, { greeting: 'Hello' });
 * ```
 */
export function definePrompt<
  T extends Record<string, unknown> = NoVars,
  F extends AnyFormatInput = undefined,
>(args: PromptArgs<T, F> | ContextPromptArgs<T, F>): UnifiedPrompt<T, F>;

// ============================================================================
// Implementation
// ============================================================================

// Implementation
export function definePrompt<T, F extends AnyFormatInput>({
  tools,
  format,
  template,
}: PromptArgs<T, F> | ContextPromptArgs<T, F>): UnifiedPrompt<T, F> {
  // Resolve format at definition time (uses 'tool' as default mode)
  const resolvedFormat = resolveFormat(format, "tool");

  // Create messages function that handles both context and non-context cases
  const messagesImpl = (...args: unknown[]): readonly Message[] => {
    const firstArg = args[0];

    // Check if first argument is a Context
    if (isContext(firstArg)) {
      // Context case: first arg is ctx, second is vars
      const ctx = firstArg;
      const vars = args[1] as ExtractVars<T> | undefined;
      const templateArgs = { ctx, ...vars } as T;
      const content =
        template.length === 0
          ? (template as () => UserContent | readonly Message[])()
          : (template as (args: T) => UserContent | readonly Message[])(
              templateArgs,
            );
      return promoteToMessages(content);
    } else {
      // Non-context case: first arg is vars (or undefined)
      const vars = firstArg as T | undefined;
      const content =
        template.length === 0
          ? (template as () => UserContent | readonly Message[])()
          : (template as (vars: T) => UserContent | readonly Message[])(
              vars as T,
            );
      return promoteToMessages(content);
    }
  };

  // Create call function
  const callImpl = async (
    ...args: unknown[]
  ): Promise<
    | Response<ExtractFormatType<F>>
    | ContextResponse<unknown, ExtractFormatType<F>>
  > => {
    const modelArg = args[0] as Model | ModelId;
    const secondArg = args[1];

    if (isContext(secondArg)) {
      // Context case: call(model, ctx, vars?)
      const ctx = secondArg;
      const vars = args[2] as ExtractVars<T> | undefined;
      const msgs = messagesImpl(ctx, vars);
      return useModel(modelArg).contextCall(ctx, msgs, {
        tools: tools as ContextTools<unknown>,
        format: resolvedFormat,
      }) as Promise<ContextResponse<unknown, ExtractFormatType<F>>>;
    } else {
      // Non-context case: call(model, vars?)
      const vars = secondArg as T | undefined;
      const msgs = messagesImpl(vars);
      return useModel(modelArg).call(msgs, {
        tools: tools as Tools,
        format: resolvedFormat,
      }) as Promise<Response<ExtractFormatType<F>>>;
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
    const modelArg = args[0] as Model | ModelId;
    const secondArg = args[1];

    if (isContext(secondArg)) {
      // Context case: stream(model, ctx, vars?)
      const ctx = secondArg;
      const vars = args[2] as ExtractVars<T> | undefined;
      const msgs = messagesImpl(ctx, vars);
      return useModel(modelArg).contextStream(ctx, msgs, {
        tools: tools as ContextTools<unknown>,
        format: resolvedFormat,
      }) as Promise<ContextStreamResponse<unknown, ExtractFormatType<F>>>;
    } else {
      // Non-context case: stream(model, vars?)
      const vars = secondArg as T | undefined;
      const msgs = messagesImpl(vars);
      return useModel(modelArg).stream(msgs, {
        tools: tools as Tools,
        format: resolvedFormat,
      }) as Promise<StreamResponse<ExtractFormatType<F>>>;
    }
  };

  return Object.assign(callable, {
    call: callImpl,
    stream: streamImpl,
    messages: messagesImpl,
    tools,
    format,
    template,
  }) as UnifiedPrompt<T, F>;
}
