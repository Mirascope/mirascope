/**
 * The `Message` types and utility constructors.
 */

import type { AssistantContentPart, UserContentPart } from "@/llm/content";
import type { Text } from "@/llm/content/text";
import type { ModelId, ProviderId } from "@/llm/providers";
import type { Jsonable } from "@/llm/types";

/**
 * A system message that sets context and instructions for the conversation.
 */
export type SystemMessage = {
  /** The role of this message. Always "system". */
  readonly role: "system";

  /** The content of this SystemMessage. */
  readonly content: Text;
};

/**
 * A user message containing input from the user.
 */
export type UserMessage = {
  /** The role of this message. Always "user". */
  readonly role: "user";

  /** The content of the user message. */
  readonly content: readonly UserContentPart[];

  /** A name identifying the creator of this message. */
  readonly name: string | null;
};

/**
 * An assistant message containing the model's response.
 */
export type AssistantMessage = {
  /** The role of this message. Always "assistant". */
  readonly role: "assistant";

  /** The content of the assistant message. */
  readonly content: readonly AssistantContentPart[];

  /** A name identifying the creator of this message. */
  readonly name: string | null;

  /** The LLM provider that generated this assistant message, if available. */
  readonly providerId: ProviderId | null;

  /** The model identifier of the LLM that generated this assistant message, if available. */
  readonly modelId: ModelId | null;

  /** The provider-specific model identifier (e.g. "gpt-5:responses"), if available. */
  readonly providerModelName: string | null;

  /**
   * The provider-specific raw representation of this assistant message, if available.
   *
   * If raw_content is truthy, then it may be used for provider-specific behavior when
   * resuming an LLM interaction that included this assistant message. For example, we can
   * reuse the provider-specific raw encoding rather than re-encoding the message from it's
   * Mirascope content representation. This may also take advantage of server-side provider
   * context, e.g. identifiers of reasoning context tokens that the provider generated.
   *
   * If present, the content should be encoded as JSON-serializable data, and in a format
   * that matches representation the provider expects representing the Mirascope data.
   *
   * Raw content is not required, as the Mirascope content can also be used to generate
   * a valid input to the provider (potentially without taking advantage of provider-specific
   * reasoning caches, etc). In that case raw content should be left empty.
   */
  readonly rawMessage: Jsonable | null;
};

/**
 * A message in an LLM interaction.
 *
 * Messages have a role (system, user, or assistant) and content that is a sequence
 * of content parts. The content can include text, images, audio, documents, and
 * tool interactions.
 *
 * For most use cases, prefer the convenience functions `system()`, `user()`, and
 * `assistant()` instead of directly creating `Message` objects.
 *
 * @example
 * ```typescript
 * import { messages } from 'mirascope/llm';
 *
 * const msgs = [
 *   messages.system("You are a helpful assistant."),
 *   messages.user("Hello, how are you?"),
 * ];
 * ```
 */
export type Message = SystemMessage | UserMessage | AssistantMessage;

/**
 * Type alias for content that can fit into a `UserMessage`.
 */
export type UserContent =
  | string
  | UserContentPart
  | readonly (string | UserContentPart)[];

/**
 * Type alias for content that can fit into an `AssistantMessage`.
 */
export type AssistantContent =
  | string
  | AssistantContentPart
  | readonly (string | AssistantContentPart)[];

/**
 * Type alias for content that can fit into a `SystemMessage`.
 */
export type SystemContent = string | Text;

/**
 * Creates a system message.
 *
 * @param content - The content of the message, which must be a string or Text content.
 * @returns A SystemMessage.
 */
export function system(content: SystemContent): SystemMessage {
  const promotedContent: Text =
    typeof content === "string" ? { type: "text", text: content } : content;
  return {
    role: "system",
    content: promotedContent,
  };
}

/**
 * Creates a user message.
 *
 * @param content - The content of the message, which can be a string or any UserContent,
 *   or a sequence of such user content pieces.
 * @param options - Optional parameters.
 * @param options.name - Optional name to identify a specific user in multi-party conversations.
 * @returns A UserMessage.
 */
export function user(
  content: UserContent,
  options?: { name?: string | null },
): UserMessage {
  const contentArray: readonly (string | UserContentPart)[] =
    typeof content === "string" || !Array.isArray(content)
      ? [content as string | UserContentPart]
      : content;

  const promotedContent: readonly UserContentPart[] = contentArray.map((part) =>
    typeof part === "string" ? { type: "text" as const, text: part } : part,
  );

  return {
    role: "user",
    content: promotedContent,
    name: options?.name ?? null,
  };
}

/**
 * Creates an assistant message.
 *
 * @param content - The content of the message, which can be a string or any AssistantContent,
 *   or a sequence of assistant content pieces.
 * @param options - Required and optional parameters.
 * @param options.modelId - Optional id of the model that produced this message.
 * @param options.providerId - Optional identifier of the provider that produced this message.
 * @param options.providerModelName - Optional provider-specific model name.
 * @param options.rawMessage - Optional Jsonable object with provider-specific raw data.
 * @param options.name - Optional name to identify a specific assistant in multi-party conversations.
 * @returns An AssistantMessage.
 */
export function assistant(
  content: AssistantContent,
  options: {
    modelId: ModelId | null;
    providerId: ProviderId | null;
    providerModelName?: string | null;
    rawMessage?: Jsonable | null;
    name?: string | null;
  },
): AssistantMessage {
  const contentArray: readonly (string | AssistantContentPart)[] =
    typeof content === "string" || !Array.isArray(content)
      ? [content as string | AssistantContentPart]
      : content;

  const promotedContent: readonly AssistantContentPart[] = contentArray.map(
    (part) =>
      typeof part === "string" ? { type: "text" as const, text: part } : part,
  );

  return {
    role: "assistant",
    content: promotedContent,
    name: options.name ?? null,
    providerId: options.providerId,
    modelId: options.modelId,
    providerModelName: options.providerModelName ?? null,
    rawMessage: options.rawMessage ?? null,
  };
}
