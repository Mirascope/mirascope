/**
 * Prompt definition and creation utilities.
 */

import type { Message, UserContent } from '@/llm/messages';
import { promoteToMessages } from '@/llm/messages';
import { Model, useModel } from '@/llm/models';
import type { ModelId } from '@/llm/providers/model-id';
import type { Response } from '@/llm/responses';
import type { StreamResponse } from '@/llm/responses/stream-response';
import type { Tools } from '@/llm/tools';
import type { NoVars } from '@/llm/types';

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
 * Arguments for defining a prompt.
 *
 * @template T - The type of variables the template accepts. Defaults to NoVars.
 */
export interface PromptArgs<T = NoVars> {
  /** Optional tools to make available to the model. */
  tools?: Tools;
  /** A function that generates message content (optionally from variables). */
  template: TemplateFunc<T>;
}

/**
 * A prompt that can be called with a model to generate a response.
 *
 * Created by `definePrompt()`. The prompt is callable and also has a
 * `messages()` method for getting the raw messages without calling the LLM.
 *
 * @template T - The type of variables the prompt accepts. Defaults to empty object.
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
export interface Prompt<T = NoVars> {
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
  ): Promise<Response>;

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
  ): Promise<Response>;

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
  ): Promise<StreamResponse>;

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
   * The underlying template function.
   */
  readonly template: TemplateFunc<T>;
}

/**
 * Define a prompt without variables.
 *
 * @param args - The prompt arguments including the template.
 * @returns A callable prompt that can be invoked with just a model.
 *
 * @example
 * ```typescript
 * const sayHello = definePrompt({
 *   template: () => 'Hello!',
 * });
 * const response = await sayHello(model);
 * ```
 */
export function definePrompt(args: PromptArgs<NoVars>): Prompt<NoVars>;

/**
 * Define a prompt with variables that can be called with a model to generate a response.
 *
 * The template function receives variables and returns either a string
 * (converted to a user message), UserContent, or a sequence of Messages.
 *
 * @template T - The type of variables the template accepts.
 * @param args - The prompt arguments including the template.
 * @returns A callable prompt that can be invoked with a model and variables.
 *
 * @example Simple string template
 * ```typescript
 * const recommendBook = definePrompt<{ genre: string }>({
 *   template: ({ genre }) => `Recommend a ${genre} book`,
 * });
 *
 * const response = await recommendBook(model, { genre: 'fantasy' });
 * console.log(response.text());
 * ```
 *
 * @example With message array
 * ```typescript
 * import { system, user } from 'mirascope/llm/messages';
 *
 * const chatBot = definePrompt<{ question: string }>({
 *   template: ({ question }) => [
 *     system('You are a helpful assistant.'),
 *     user(question),
 *   ],
 * });
 *
 * const response = await chatBot(model, { question: 'What is TypeScript?' });
 * ```
 *
 * @example With model ID string
 * ```typescript
 * const response = await recommendBook(
 *   'anthropic/claude-sonnet-4-20250514',
 *   { genre: 'sci-fi' }
 * );
 * ```
 */
export function definePrompt<T extends Record<string, unknown>>(
  args: PromptArgs<T>
): Prompt<T>;

/**
 * Generic overload for internal use (e.g., from defineCall).
 * Accepts any T without constraints.
 * @internal
 */
export function definePrompt<T>(args: PromptArgs<T>): Prompt<T>;

// Implementation
export function definePrompt<T>({ tools, template }: PromptArgs<T>): Prompt<T> {
  const messages = (vars?: T): readonly Message[] => {
    const content =
      template.length === 0
        ? (template as () => UserContent | readonly Message[])()
        : (template as (vars: T) => UserContent | readonly Message[])(
            vars as T
          );
    return promoteToMessages(content);
  };

  const call = async (model: Model | ModelId, vars?: T): Promise<Response> => {
    return useModel(model).call(messages(vars), tools);
  };

  const callable = async (
    model: Model | ModelId,
    vars?: T
  ): Promise<Response> => {
    return call(model, vars);
  };

  const stream = async (
    model: Model | ModelId,
    vars?: T
  ): Promise<StreamResponse> => {
    return useModel(model).stream(messages(vars), tools);
  };

  return Object.assign(callable, {
    call,
    stream,
    messages,
    tools,
    template,
  }) as Prompt<T>;
}
