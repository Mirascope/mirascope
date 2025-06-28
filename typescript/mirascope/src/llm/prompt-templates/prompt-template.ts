/**
 * @fileoverview The `promptTemplate` method for promoting "promptables" into prompt templates.
 */
/**
 * The `promptTemplate` method for writing messages as string templates.
 */

import type { Content } from '../content';
import type { Context } from '../context';
import type { Message } from '../messages/message';

type PromptParams = Record<string, unknown>;

// Promptable function types with prompt parameters
type ContentPromptable<P extends PromptParams> = (params: P) => Content;

type ContentSequencePromptable<P extends PromptParams> = (
  params: P
) => Content[];

type PromptTemplate<P extends PromptParams> = (params: P) => Message[];

/**
 * A function with prompt parameters that can be promoted to a prompt.
 *
 * A `Promptable` function takes input arguments `P` and returns one of:
 *   - A single `Content` part that will be rendered as a single user message
 *   - A sequence of `Content` parts that will be rendered as a single user message
 *   - A list of `Message` objects that will be rendered as-is
 */
type Promptable<P extends PromptParams> =
  | PromptTemplate<P>
  | ContentPromptable<P>
  | ContentSequencePromptable<P>;

// Promptable function types with positional arguments
type PositionalContentPromptable<Args extends readonly unknown[] = unknown[]> =
  (...args: Args) => Content;

type PositionalContentSequencePromptable<
  Args extends readonly unknown[] = unknown[],
> = (...args: Args) => Content[];

type PositionalPromptTemplate<Args extends readonly unknown[] = unknown[]> = (
  ...args: Args
) => Message[];

/**
 * A function with positional arguments that can be promoted to a prompt.
 *
 * A `Promptable` function takes input arguments `P` and returns one of:
 *   - A single `Content` part that will be rendered as a single user message
 *   - A sequence of `Content` parts that will be rendered as a single user message
 *   - A list of `Message` objects that will be rendered as-is
 */
type PositionalPromptable<Args extends readonly unknown[] = unknown[]> =
  | PositionalPromptTemplate<Args>
  | PositionalContentPromptable<Args>
  | PositionalContentSequencePromptable<Args>;

// Async promptable function types with prompt parameters
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
 * An asynchronous promptable with prompt parameters.
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

// Async promptable function types with positional arguments
type AsyncPositionalContentPromptable<
  Args extends readonly unknown[] = unknown[],
> = (...args: Args) => Promise<Content>;

type AsyncPositionalContentSequencePromptable<
  Args extends readonly unknown[] = unknown[],
> = (...args: Args) => Promise<Content[]>;

type AsyncPositionalPromptTemplate<
  Args extends readonly unknown[] = unknown[],
> = (...args: Args) => Promise<Message[]>;

/**
 * An asynchronous promptable with positional arguments.
 *
 * An `AsyncPromptable` function takes input arguments `P` and returns one of:
 *   - A single `Content` part that will be rendered as a single user message
 *   - A sequence of `Content` parts that will be rendered as a single user message
 *   - A list of `Message` objects that will be rendered as-is
 */
type AsyncPositionalPromptable<Args extends readonly unknown[] = unknown[]> =
  | AsyncPositionalPromptTemplate<Args>
  | AsyncPositionalContentPromptable<Args>
  | AsyncPositionalContentSequencePromptable<Args>;

// Context promptable function types with prompt parameters
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
 * A context promptable function with prompt parameters.
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

// Context promptable function types with positional arguments
type PositionalContextContentPromptable<
  Args extends readonly unknown[] = unknown[],
  DepsT = undefined,
> = (ctx: Context<DepsT>, ...args: Args) => Content;

type PositionalContextContentSequencePromptable<
  Args extends readonly unknown[] = unknown[],
  DepsT = undefined,
> = (ctx: Context<DepsT>, ...args: Args) => Content[];

type PositionalContextPromptTemplate<
  Args extends readonly unknown[] = unknown[],
  DepsT = undefined,
> = (ctx: Context<DepsT>, ...args: Args) => Message[];

/**
 * A context promptable function with positional arguments.
 *
 * A `PositionalContextPromptable` function takes input arguments `Context[DepsT]` and
 * `Args` and returns one of:
 *   - A single `Content` part that will be rendered as a single user message
 *   - A sequence of `Content` parts that will be rendered as a single user message
 *   - A list of `Message` objects that will be rendered as-is
 */
type PositionalContextPromptable<
  Args extends readonly unknown[] = unknown[],
  DepsT = undefined,
> =
  | PositionalContextPromptTemplate<Args, DepsT>
  | PositionalContextContentPromptable<Args, DepsT>
  | PositionalContextContentSequencePromptable<Args, DepsT>;

// Asynchronous context promptable function types with prompt parameters
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
 * An asynchronous context promptable function with prompt parameters.
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

// Asynchronous context promptable function types with positional arguments
type AsyncPositionalContextContentPromptable<
  Args extends readonly unknown[] = unknown[],
  DepsT = undefined,
> = (ctx: Context<DepsT>, ...args: Args) => Promise<Content>;

type AsyncPositionalContextContentSequencePromptable<
  Args extends readonly unknown[] = unknown[],
  DepsT = undefined,
> = (ctx: Context<DepsT>, ...args: Args) => Promise<Content[]>;

type AsyncPositionalContextPromptTemplate<
  Args extends readonly unknown[] = unknown[],
  DepsT = undefined,
> = (ctx: Context<DepsT>, ...args: Args) => Promise<Message[]>;

/**
 * An asynchronous context promptable function with positional arguments.
 *
 * An `AsyncPositionalContextPromptable` function takes input arguments
 * `Context[DepsT]` and `Args` and returns one of:
 *   - A single `Content` part that will be rendered as a single user message
 *   - A sequence of `Content` parts that will be rendered as a single user message
 *   - A list of `Message` objects that will be rendered as-is
 */
type AsyncPositionalContextPromptable<
  Args extends readonly unknown[] = unknown[],
  DepsT = undefined,
> =
  | AsyncPositionalContextPromptTemplate<Args, DepsT>
  | AsyncPositionalContextContentPromptable<Args, DepsT>
  | AsyncPositionalContextContentSequencePromptable<Args, DepsT>;

/**
 * Prompt Template method for turning functions (or "promptables") into prompts.
 *
 * This method transforms a function into a PromptTemplate, i.e. a function that
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
 * const domainQuestionPromptTemplate = definePromptTemplate<{ domain: string; question: string }>`
 *   [SYSTEM] You are a helpful assistant specializing in {{ domain }}.
 *   [USER] {{ question }}
 * `;
 *
 * const answerQuestionPromptTemplate = definePromptTemplate(
 *   ({ question }: { question: string }) => `Answer this question: ${question}`
 * );
 *
 * const answerQuestionPromptTemplate = definePromptTemplate(
 *   (question: string) => `Answer this question: ${question}`
 * );
 * ```
 */
function definePromptTemplate<P extends PromptParams>(
  strings: TemplateStringsArray,
  ...values: unknown[]
): PromptTemplate<P>;

function definePromptTemplate<P extends PromptParams>(
  fn: Promptable<P>
): PromptTemplate<P>;

function definePromptTemplate<Args extends readonly unknown[] = unknown[]>(
  fn: PositionalPromptable<Args>
): PositionalPromptTemplate<Args>;

function definePromptTemplate<P extends PromptParams>(
  fn: AsyncPromptable<P>
): AsyncPromptTemplate<P>;

function definePromptTemplate<Args extends readonly unknown[] = unknown[]>(
  fn: AsyncPositionalPromptable<Args>
): AsyncPositionalPromptTemplate<Args>;

function definePromptTemplate<P extends PromptParams, DepsT = undefined>(
  fn: ContextPromptable<P, DepsT>
): ContextPromptTemplate<P, DepsT>;

function definePromptTemplate<
  Args extends readonly unknown[] = unknown[],
  DepsT = undefined,
>(
  fn: PositionalContextPromptable<Args, DepsT>
): PositionalContextPromptTemplate<Args, DepsT>;

function definePromptTemplate<P extends PromptParams, DepsT = undefined>(
  fn: AsyncContextPromptable<P, DepsT>
): AsyncContextPromptTemplate<P, DepsT>;

function definePromptTemplate<
  Args extends readonly unknown[] = unknown[],
  DepsT = undefined,
>(
  fn: AsyncPositionalContextPromptable<Args, DepsT>
): AsyncPositionalContextPromptTemplate<Args, DepsT>;

function definePromptTemplate<
  P extends PromptParams,
  Args extends readonly unknown[] = unknown[],
  DepsT = undefined,
>(
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  _stringsOrFn:
    | TemplateStringsArray
    | Promptable<P>
    | PositionalPromptable<Args>
    | AsyncPromptable<P>
    | AsyncPositionalPromptable<Args>
    | ContextPromptable<P, DepsT>
    | PositionalContextPromptable<Args, DepsT>
    | AsyncContextPromptable<P, DepsT>
    | AsyncPositionalContextPromptable<Args, DepsT>,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  ..._values: unknown[]
):
  | PromptTemplate<P>
  | PositionalPromptTemplate<Args>
  | AsyncPromptTemplate<P>
  | AsyncPositionalPromptTemplate<Args>
  | ContextPromptTemplate<P, DepsT>
  | PositionalContextPromptTemplate<Args, DepsT>
  | AsyncContextPromptTemplate<P, DepsT>
  | AsyncPositionalContextPromptTemplate<Args, DepsT> {
  throw new Error('Not implemented');
}

export { definePromptTemplate };
