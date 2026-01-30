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

/**
 * Signals the start of a thought content block in the stream.
 */
export type ThoughtStartChunk = {
  readonly type: 'thought_start_chunk';
  readonly contentType: 'thought';
};

/**
 * Contains incremental thought content.
 */
export type ThoughtChunk = {
  readonly type: 'thought_chunk';
  readonly contentType: 'thought';
  /** The incremental thought text added in this chunk. */
  readonly delta: string;
};

/**
 * Signals the end of a thought content block in the stream.
 */
export type ThoughtEndChunk = {
  readonly type: 'thought_end_chunk';
  readonly contentType: 'thought';
};

/** Create a ThoughtStartChunk */
export function thoughtStart(): ThoughtStartChunk {
  return { type: 'thought_start_chunk', contentType: 'thought' };
}

/** Create a ThoughtChunk */
export function thoughtChunk(delta: string): ThoughtChunk {
  return { type: 'thought_chunk', contentType: 'thought', delta };
}

/** Create a ThoughtEndChunk */
export function thoughtEnd(): ThoughtEndChunk {
  return { type: 'thought_end_chunk', contentType: 'thought' };
}
