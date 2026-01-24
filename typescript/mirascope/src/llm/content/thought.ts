/**
 * Thought content from an assistant's extended thinking.
 *
 * Represents the reasoning or thinking process of an assistant model
 * that supports extended thinking (e.g., Claude with thinking enabled).
 */
export type Thought = {
  readonly type: 'thought';

  /** The thoughts or reasoning of the assistant. */
  readonly thought: string;
};
