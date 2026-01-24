/**
 * Text content for a message.
 *
 * Represents plain text content in a message. This is the most common
 * content type for both user and assistant messages.
 */
export type Text = {
  readonly type: 'text';

  /** The text content. */
  readonly text: string;
};
