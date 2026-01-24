/**
 * Utility functions for message handling.
 */

import type { Message, UserContent } from '@/llm/messages/message';
import { user } from '@/llm/messages/message';

/**
 * Type guard that checks if the content is a sequence of Messages.
 *
 * @param content - Either user content or a sequence of messages.
 * @returns True if content is a sequence of Messages, false otherwise.
 * @throws Error if an empty array is provided.
 */
export function isMessages(
  content: UserContent | readonly Message[]
): content is readonly Message[] {
  if (Array.isArray(content)) {
    if (content.length === 0) {
      throw new Error('Empty array may not be used as message content');
    }
    const first: unknown = content[0];
    return (
      typeof first === 'object' &&
      first !== null &&
      'role' in first &&
      typeof (first as { role: unknown }).role === 'string' &&
      ((first as { role: string }).role === 'system' ||
        (first as { role: string }).role === 'user' ||
        (first as { role: string }).role === 'assistant')
    );
  }
  return false;
}

/**
 * Promote a prompt result to a list of messages.
 *
 * If the result is already a list of Messages, returns it as-is.
 * If the result is str/UserContentPart/Sequence of content parts, wraps it in a user message.
 *
 * @param content - Either user content or a sequence of messages.
 * @returns A sequence of Messages.
 */
export function promoteToMessages(
  content: UserContent | readonly Message[]
): readonly Message[] {
  if (isMessages(content)) {
    return content;
  }
  return [user(content)];
}
