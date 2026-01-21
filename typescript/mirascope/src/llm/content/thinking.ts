/**
 * @fileoverview The `Thinking` content class.
 */

/**
 * Thinking content for a message.
 *
 * Represents the thinking or thought process of the assistant. This is part
 * of an assistant message's content.
 */
export type Thinking = {
  /** The content type identifier */
  type: 'thinking';

  /** The ID of the thinking content. */
  id?: string;

  /** The thoughts or reasoning of the assistant. */
  thoughts: string;

  /** Whether the thinking is redacted or not. */
  redacted?: boolean;
};
