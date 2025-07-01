/**
 * @fileoverview The `promptTemplate` method for promoting "promptables" into prompt templates.
 */

import type { Content } from '../content';
import type { Context } from '../context';
import type { Message } from '../messages/message';

/**
 * A function that can be promoted to a prompt template.
 *
 * A `Promptable` function takes any arguments and returns one of:
 *   - A single `Content` part that will be rendered as a single user message
 *   - A sequence of `Content` parts that will be rendered as a single user message
 *   - A list of `Message` objects that will be rendered as-is
 */
type Promptable<T> = T extends readonly unknown[]
  ? (...args: T) => Content | Content[] | Message[]
  : (params: T) => Content | Content[] | Message[];

/**
 * An asynchronous promptable function.
 *
 * An `AsyncPromptable` function takes any arguments and returns one of:
 *   - A single `Content` part that will be rendered as a single user message
 *   - A sequence of `Content` parts that will be rendered as a single user message
 *   - A list of `Message` objects that will be rendered as-is
 */
type AsyncPromptable<T> = T extends readonly unknown[]
  ? (...args: T) => Promise<Content | Content[] | Message[]>
  : (params: T) => Promise<Content | Content[] | Message[]>;

/**
 * A context promptable function.
 *
 * A `ContextPromptable` function takes a Context as the first argument followed by
 * any other arguments and returns one of:
 *   - A single `Content` part that will be rendered as a single user message
 *   - A sequence of `Content` parts that will be rendered as a single user message
 *   - A list of `Message` objects that will be rendered as-is
 */
type ContextPromptable<T, DepsT = undefined> = T extends readonly unknown[]
  ? (ctx: Context<DepsT>, ...args: T) => Content | Content[] | Message[]
  : (ctx: Context<DepsT>, params: T) => Content | Content[] | Message[];

/**
 * An asynchronous context promptable function.
 *
 * An `AsyncContextPromptable` function takes a Context as the first argument followed by
 * any other arguments and returns one of:
 *   - A single `Content` part that will be rendered as a single user message
 *   - A sequence of `Content` parts that will be rendered as a single user message
 *   - A list of `Message` objects that will be rendered as-is
 */
type AsyncContextPromptable<T, DepsT = undefined> = T extends readonly unknown[]
  ? (
      ctx: Context<DepsT>,
      ...args: T
    ) => Promise<Content | Content[] | Message[]>
  : (
      ctx: Context<DepsT>,
      params: T
    ) => Promise<Content | Content[] | Message[]>;

/**
 * A prompt template function that always returns Message[].
 */
type PromptTemplate<T> = T extends readonly unknown[]
  ? (...args: T) => Message[]
  : (params: T) => Message[];

/**
 * An asynchronous prompt template function that always returns Promise<Message[]>.
 */
type AsyncPromptTemplate<T> = T extends readonly unknown[]
  ? (...args: T) => Promise<Message[]>
  : (params: T) => Promise<Message[]>;

/**
 * A context prompt template function that always returns Message[].
 */
type ContextPromptTemplate<T, DepsT = undefined> = T extends readonly unknown[]
  ? (ctx: Context<DepsT>, ...args: T) => Message[]
  : (ctx: Context<DepsT>, params: T) => Message[];

/**
 * An asynchronous context prompt template function that always returns Promise<Message[]>.
 */
type AsyncContextPromptTemplate<
  T,
  DepsT = undefined,
> = T extends readonly unknown[]
  ? (ctx: Context<DepsT>, ...args: T) => Promise<Message[]>
  : (ctx: Context<DepsT>, params: T) => Promise<Message[]>;

/**
 * Prompt Template method for turning functions (or "promptables") into prompts.
 *
 * This method transforms a function into a PromptTemplate, i.e. a function that
 * returns `Message[]`. Its behavior depends on whether it's called with a spec
 * string.
 *
 * With a spec string, it uses the provided spec to decorate a function with an empty body,
 * and uses arguments to the function for variable substitution in the spec. The resulting
 * PromptTemplate returns messages based on the spec.
 *
 * Without a spec string, it transforms a Promptable (a function returning either content,
 * content sequence, or messages) into a PromptTemplate. The resulting prompt template either
 * promotes the content / content sequence into an array containing a single user message with
 * that content, or passes along the messages returned by the decorated function.
 *
 * @param stringsOrFn Either a template string (tagged template literal) or a promptable function
 * @param values Template literal values (when using tagged template syntax)
 *
 * @returns A PromptTemplate that converts the input into a prompt
 *
 * Spec substitution rules:
 * - [USER], [ASSISTANT], [SYSTEM] demarcate the start of a new message with that role
 * - [MESSAGES] indicates the next variable contains an array of messages to include
 * - `{{ variable }}` injects the variable as a string, unless annotated
 * - Annotations: `{{ variable:annotation }}` where annotation is one of:
 *      image, images, audio, audios, video, videos, document, documents
 * - Single content annotations (image, audio, video, document) expect a file path,
 *      URL, base64 string, or bytes, which becomes a content part with inferred mime-type
 * - Multiple content annotations (images, audios, videos, documents) expect an array
 *      of strings or bytes, each becoming a content part with inferred mime-type
 *
 * @example
 * ```typescript
 * // From template spec
 * const domainQuestionPromptTemplate = definePromptTemplate<{ domain: string; question: string }>`
 *   [SYSTEM] You are a helpful assistant specializing in {{ domain }}.
 *   [USER] {{ question }}
 * `;
 *
 * // Direct promptable function
 * const answerQuestionPromptTemplate = definePromptTemplate(
 *   (question: string) => `Answer this question: ${question}`
 * );
 * ```
 */
function definePromptTemplate<T>(
  strings: TemplateStringsArray,
  ...values: unknown[]
): PromptTemplate<T>;

function definePromptTemplate<T>(fn: Promptable<T>): PromptTemplate<T>;

function definePromptTemplate<T>(
  fn: AsyncPromptable<T>
): AsyncPromptTemplate<T>;

function definePromptTemplate<T, DepsT = undefined>(
  fn: ContextPromptable<T, DepsT>
): ContextPromptTemplate<T, DepsT>;

function definePromptTemplate<T, DepsT = undefined>(
  fn: AsyncContextPromptable<T, DepsT>
): AsyncContextPromptTemplate<T, DepsT>;

function definePromptTemplate<T, DepsT = undefined>(
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  _stringsOrFn:
    | TemplateStringsArray
    | Promptable<T>
    | AsyncPromptable<T>
    | ContextPromptable<T, DepsT>
    | AsyncContextPromptable<T, DepsT>,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  ..._values: unknown[]
):
  | PromptTemplate<T>
  | AsyncPromptTemplate<T>
  | ContextPromptTemplate<T, DepsT>
  | AsyncContextPromptTemplate<T, DepsT> {
  throw new Error('Not implemented');
}

export { definePromptTemplate };
