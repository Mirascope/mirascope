/**
 * @fileoverview The `promptTemplate` decorator for promoting "promptables" into prompt templates.
 */
/**
 * The `promptTemplate` decorator for writing messages as string templates.
 */

import type { Content } from '../content';
import type { Context } from '../context';
import type { Message } from '../messages/message';

type PromptParams = Record<string, unknown>;

type PromptTemplate<P extends PromptParams> = (params: P) => Message[];
type ContentPromptable<P extends PromptParams> = (params: P) => Content;
type ContentSequencePromptable<P extends PromptParams> = (
  params: P
) => Content[];

/**
 * A function that can be promoted to a prompt.
 *
 * A `Promptable` function takes input arguments `P` and returns one of:
 *   - A single `Content` part that will be rendered as a single user message
 *   - A sequence of `Content` parts that will be rendered as a single user message
 *   - A list of `Message` objects that will be rendered as-is
 */
type Promptable<P extends PromptParams> =
  | ContentPromptable<P>
  | ContentSequencePromptable<P>
  | PromptTemplate<P>;

type AsyncContentPromptable<P extends PromptParams> = (
  params: P
) => Promise<Content>;
type AsyncContentSequencePromptable<P extends PromptParams> = (
  params: P
) => Promise<Content[]>;
type AsyncPromptTemplate<P extends PromptParams> = (
  params: P
) => Promise<Message[]>;

/**
 * An asynchronous promptable function.
 *
 * An `AsyncPromptable` function takes input arguments `P` and returns one of:
 *   - A single `Content` part that will be rendered as a single user message
 *   - A sequence of `Content` parts that will be rendered as a single user message
 *   - A list of `Message` objects that will be rendered as-is
 */
type AsyncPromptable<P extends PromptParams> =
  | AsyncContentPromptable<P>
  | AsyncContentSequencePromptable<P>
  | AsyncPromptTemplate<P>;

type ContextContentPromptable<P extends PromptParams, DepsT = undefined> = (
  ctx: Context<DepsT>,
  params: P
) => Content;

type ContextContentSequencePromptable<
  P extends PromptParams,
  DepsT = undefined,
> = (ctx: Context<DepsT>, params: P) => Content[];

type ContextPromptTemplate<P extends PromptParams, DepsT = undefined> = (
  ctx: Context<DepsT>,
  params: P
) => Message[];

/**
 * A context promptable function.
 *
 * A `ContextPromptable` function takes input arguments `Context[DepsT]` and `P` and
 * returns one of:
 *   - A single `Content` part that will be rendered as a single user message
 *   - A sequence of `Content` parts that will be rendered as a single user message
 *   - A list of `Message` objects that will be rendered as-is
 */
type ContextPromptable<P extends PromptParams, DepsT = undefined> =
  | ContextContentPromptable<P, DepsT>
  | ContextContentSequencePromptable<P, DepsT>
  | ContextPromptTemplate<P, DepsT>;

type AsyncContextContentPromptable<
  P extends PromptParams,
  DepsT = undefined,
> = (ctx: Context<DepsT>, params: P) => Promise<Content>;

type AsyncContextContentSequencePromptable<
  P extends PromptParams,
  DepsT = undefined,
> = (ctx: Context<DepsT>, params: P) => Promise<Content[]>;

type AsyncContextPromptTemplate<P extends PromptParams, DepsT = undefined> = (
  ctx: Context<DepsT>,
  params: P
) => Promise<Message[]>;

/**
 * An asynchronous context promptable function.
 *
 * An `AsyncContextPromptable` function takes input arguments `Context[DepsT]` and `P`
 * and returns one of:
 *   - A single `Content` part that will be rendered as a single user message
 *   - A sequence of `Content` parts that will be rendered as a single user message
 *   - A list of `Message` objects that will be rendered as-is
 */
type AsyncContextPromptable<P extends PromptParams, DepsT = undefined> =
  | AsyncContextContentPromptable<P, DepsT>
  | AsyncContextContentSequencePromptable<P, DepsT>
  | AsyncContextPromptTemplate<P, DepsT>;

// Spec Prompt Template Overload
function promptTemplate<P extends PromptParams>(
  strings: TemplateStringsArray,
  ...values: any[]
): PromptTemplate<P>;

// Functional Prompt Template Overloads
function promptTemplate<P extends PromptParams>(
  fn: Promptable<P>
): PromptTemplate<P>;
function promptTemplate<P extends PromptParams>(
  fn: AsyncPromptable<P>
): AsyncPromptTemplate<P>;
function promptTemplate<P extends PromptParams>(
  fn: ContextPromptable<P>
): ContextPromptTemplate<P>;
function promptTemplate<P extends PromptParams, DepsT>(
  fn: ContextPromptable<P, DepsT>
): ContextPromptTemplate<P, DepsT>;
function promptTemplate<P extends PromptParams>(
  fn: AsyncContextPromptable<P>
): AsyncContextPromptTemplate<P>;
function promptTemplate<P extends PromptParams, DepsT>(
  fn: AsyncContextPromptable<P, DepsT>
): AsyncContextPromptTemplate<P, DepsT>;

/**
 * Prompt decorator for turning functions into prompts.
 *
 * This decorator transforms a function into a PromptTemplate, i.e. a function that
 * returns `Message[]`. Its behavior depends on whether it's called with a spec
 * string.
 *
 * With a spec string, it returns a PromptTemplateSpecDecorator, in which case it uses
 * the provided spec to decorate a function with an empty body, and uses arguments
 * to the function for variable substitution in the spec. The resulting PromptTemplate
 * returns messages based on the spec.
 *
 * Without a spec string, it returns a PromptTemplateFunctionalDecorator, which
 * transforms a Promptable (a function returning either content, content sequence,
 * or messages) into a PromptTemplate. The resulting prompt template either promotes
 * the content / content sequence into an array containing a single user message with
 * that content, or passes along the messages returned by the decorated function.
 *
 * @param spec A string spec with placeholders using `{{ variable_name }}`
 *             and optional role markers like [SYSTEM], [USER], and [ASSISTANT].
 *
 * @returns A PromptTemplateSpecDecorator or PromptTemplateFunctionalDecorator that converts
 *          the decorated function into a prompt.
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
 * class Prompts {
 *   @promptTemplate(`
 *     [SYSTEM] You are a helpful assistant specializing in {{ domain }}.
 *     [USER] {{ question }}
 *   `)
 *   static domainQuestion(domain: string, question: string): {} {
 *     return {};
 *   }
 *
 *   @promptTemplate()
 *   static answerQuestion(question: string): string {
 *     return `Answer: ${question}`;
 *   }
 * }
 * ```
 */
function promptTemplate<P extends PromptParams, DepsT = unknown>(
  stringsOrFn:
    | TemplateStringsArray
    | Promptable<P>
    | AsyncPromptable<P>
    | ContextPromptable<P>
    | ContextPromptable<P, DepsT>
    | AsyncContextPromptable<P>
    | AsyncContextPromptable<P, DepsT>,
  ...values: any[]
):
  | PromptTemplate<P>
  | AsyncPromptTemplate<P>
  | ContextPromptTemplate<P>
  | ContextPromptTemplate<P, DepsT>
  | AsyncContextPromptTemplate<P>
  | AsyncContextPromptTemplate<P, DepsT> {
  throw new Error('Not implemented');
}

export { promptTemplate };
