/**
 * Context-aware prompt definition and creation utilities.
 *
 * A ContextPrompt is a Prompt that receives a Context as its first argument,
 * enabling dependency injection for prompts and (in the future) tools.
 */

import type { Context } from '@/llm/context';
import type { Message, UserContent } from '@/llm/messages';
import { promoteToMessages } from '@/llm/messages';
import { Model, useModel } from '@/llm/models';
import type { ModelId } from '@/llm/providers/model-id';
import type { ContextResponse } from '@/llm/responses/context-response';
import type { ContextStreamResponse } from '@/llm/responses/context-stream-response';
import type { ToolSchema } from '@/llm/tools';
import type { NoVars } from '@/llm/types';

/**
 * The combined context and variables object passed to template functions.
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
 *
 * @example
 * ```typescript
 * // With variables
 * template: ({ ctx, greeting }) => `${greeting}, user ${ctx.deps.userId}!`
 *
 * // Without variables
 * template: ({ ctx }) => `Hello, user ${ctx.deps.userId}!`
 * ```
 */
export type ContextTemplateFunc<T, DepsT> = (
  args: ContextMessageTemplate<T, DepsT>
) => UserContent | readonly Message[];

/**
 * Arguments for defining a context prompt.
 *
 * @template T - The type of variables the template accepts. Defaults to NoVars.
 * @template DepsT - The type of dependencies in the context.
 */
export interface ContextPromptArgs<T = NoVars, DepsT = unknown> {
  /** Optional tools to make available to the model. */
  tools?: readonly ToolSchema[];
  /** A function that generates message content from context (and optionally variables). */
  template: ContextTemplateFunc<T, DepsT>;
}

/**
 * A context-aware prompt that can be called with a model and context to generate a response.
 *
 * Created by `defineContextPrompt()`. The prompt is callable and also has a
 * `messages()` method for getting the raw messages without calling the LLM.
 *
 * @template T - The type of variables the prompt accepts. Defaults to empty object.
 * @template DepsT - The type of dependencies in the context.
 *
 * @example With variables
 * ```typescript
 * interface MyDeps { userId: string; }
 *
 * const greetUser = defineContextPrompt<{ greeting: string }, MyDeps>({
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
 * const sayHello = defineContextPrompt<NoVars, MyDeps>({
 *   template: ({ ctx }) => `Hello, user ${ctx.deps.userId}!`,
 * });
 *
 * const response = await sayHello(model, ctx);
 * ```
 */
export interface ContextPrompt<T = NoVars, DepsT = unknown> {
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
  ): Promise<ContextResponse<DepsT>>;

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
  ): Promise<ContextResponse<DepsT>>;

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
  ): Promise<ContextStreamResponse<DepsT>>;

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
  readonly tools: readonly ToolSchema[] | undefined;

  /**
   * The underlying template function.
   */
  readonly template: ContextTemplateFunc<T, DepsT>;
}

/**
 * Define a context prompt without variables.
 *
 * @template DepsT - The type of dependencies in the context.
 * @param args - The prompt arguments including the template.
 * @returns A callable context prompt that can be invoked with a model and context.
 *
 * @example
 * ```typescript
 * interface MyDeps { userId: string; }
 *
 * const sayHello = defineContextPrompt<NoVars, MyDeps>({
 *   template: ({ ctx }) => `Hello, user ${ctx.deps.userId}!`,
 * });
 *
 * const ctx = createContext<MyDeps>({ userId: '123' });
 * const response = await sayHello(model, ctx);
 * ```
 */
export function defineContextPrompt<DepsT>(
  args: ContextPromptArgs<NoVars, DepsT>
): ContextPrompt<NoVars, DepsT>;

/**
 * Define a context prompt with variables that can be called with a model and context to generate a response.
 *
 * The template function receives context and variables and returns either a string
 * (converted to a user message), UserContent, or a sequence of Messages.
 *
 * @template T - The type of variables the template accepts.
 * @template DepsT - The type of dependencies in the context.
 * @param args - The prompt arguments including the template.
 * @returns A callable context prompt that can be invoked with a model, context, and variables.
 *
 * @example Simple string template
 * ```typescript
 * interface MyDeps { userId: string; }
 *
 * const greetUser = defineContextPrompt<{ greeting: string }, MyDeps>({
 *   template: ({ ctx, greeting }) => `${greeting}, user ${ctx.deps.userId}!`,
 * });
 *
 * const ctx = createContext<MyDeps>({ userId: '123' });
 * const response = await greetUser(model, ctx, { greeting: 'Hello' });
 * console.log(response.text());
 * ```
 *
 * @example With message array
 * ```typescript
 * import { system, user } from 'mirascope/llm/messages';
 *
 * interface MyDeps { systemPrompt: string; }
 *
 * const chatBot = defineContextPrompt<{ question: string }, MyDeps>({
 *   template: ({ ctx, question }) => [
 *     system(ctx.deps.systemPrompt),
 *     user(question),
 *   ],
 * });
 *
 * const ctx = createContext<MyDeps>({ systemPrompt: 'You are helpful.' });
 * const response = await chatBot(model, ctx, { question: 'What is TypeScript?' });
 * ```
 */
export function defineContextPrompt<
  T extends Record<string, unknown>,
  DepsT = unknown,
>(args: ContextPromptArgs<T, DepsT>): ContextPrompt<T, DepsT>;

/**
 * Generic overload for internal use (e.g., from defineContextCall).
 * Accepts any T without constraints.
 * @internal
 */
export function defineContextPrompt<T, DepsT>(
  args: ContextPromptArgs<T, DepsT>
): ContextPrompt<T, DepsT>;

// Implementation
export function defineContextPrompt<T, DepsT>({
  tools,
  template,
}: ContextPromptArgs<T, DepsT>): ContextPrompt<T, DepsT> {
  const messages = (ctx: Context<DepsT>, vars?: T): readonly Message[] => {
    const content = template({ ctx, ...(vars as T) });
    return promoteToMessages(content);
  };

  const call = async (
    modelOrId: Model | ModelId,
    ctx: Context<DepsT>,
    vars?: T
  ): Promise<ContextResponse<DepsT>> => {
    return useModel(modelOrId).contextCall(ctx, messages(ctx, vars), tools);
  };

  const callable = async (
    modelOrId: Model | ModelId,
    ctx: Context<DepsT>,
    vars?: T
  ): Promise<ContextResponse<DepsT>> => {
    return call(modelOrId, ctx, vars);
  };

  const stream = async (
    modelOrId: Model | ModelId,
    ctx: Context<DepsT>,
    vars?: T
  ): Promise<ContextStreamResponse<DepsT>> => {
    return useModel(modelOrId).contextStream(ctx, messages(ctx, vars), tools);
  };

  return Object.assign(callable, {
    call,
    stream,
    messages,
    tools,
    template,
  }) as ContextPrompt<T, DepsT>;
}
