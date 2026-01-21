/**
 * @fileoverview The `Message` type and its utility constructors
 */

import type { Content } from '../content';

/**
 * A message in an LLM interaction.
 *
 * Messages have a role (system, user, or assistant) and content that can be
 * a simple string or a complex array of content parts. The content can include
 * text, images, audio, documents, and tool interactions.
 *
 * For most use cases, prefer the convenience functions system(), user(), and
 * assistant() instead of directly creating Message objects.
 */
export type Message = {
  /** The role of the message sender (system, user, or assistant) */
  role: 'system' | 'user' | 'assistant';
  /** The content of the message, which can be text, images, audio, etc. */
  content: Content | readonly Content[];
  /** Optional name to identify specific users or assistants in multi-party conversations */
  name?: string;
};

/** Type alias for an array of messages that form a prompt */
export type Prompt = Message[];

/**
 * Shorthand function for creating a `Message` with the system role.
 *
 * @param content - The content of the message, which can be a string, a Content-type
 *   object, or a sequence of Content-type objects.
 * @param name - Optional name to identify a specific system in multi-party conversations
 * @returns A Message with the system role
 *
 */
export function system(
  content: Content | readonly Content[],
  name?: string
): Message {
  return {
    role: 'system',
    content,
    name: name,
  };
}

/**
 * Shorthand function for creating a `Message` with the user role.
 *
 * @param content - The content of the message, which can be a string, a Content-type
 *   object, or a sequence of Content-type objects.
 * @param name - Optional name to identify a specific user in multi-party conversations
 * @returns A Message with the user role
 *
 */
export function user(
  content: Content | readonly Content[],
  name?: string
): Message {
  return {
    role: 'user',
    content,
    name,
  };
}

/**
 * Shorthand function for creating a `Message` with the assistant role.
 *
 * @param content - The content of the message, which can be a string, a Content-type
 *   object, or a sequence of Content-type objects.
 * @param name - Optional name to identify a specific assistant in multi-party conversations
 * @returns A Message with the assistant role
 *
 */
export function assistant(
  content: Content | readonly Content[],
  name?: string
): Message {
  return {
    role: 'assistant',
    content,
    name,
  };
}
