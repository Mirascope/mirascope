/**
 * The messages module for LLM interactions.
 *
 * This module defines the message types used in LLM interactions. Messages are represented
 * as a unified `Message` type with different roles (system, user, assistant) and flexible
 * content arrays that can include text, images, audio, documents, and tool interactions.
 */

export type {
  AssistantContent,
  AssistantMessage,
  Message,
  SystemContent,
  SystemMessage,
  UserContent,
  UserMessage,
} from '@/llm/messages/message';

export { assistant, system, user } from '@/llm/messages/message';

export { isMessages, promoteToMessages } from '@/llm/messages/utils';
