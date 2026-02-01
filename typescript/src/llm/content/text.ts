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

/**
 * Signals the start of a text content block in the stream.
 */
export type TextStartChunk = {
  readonly type: 'text_start_chunk';
  readonly contentType: 'text';
};

/**
 * Contains incremental text content.
 */
export type TextChunk = {
  readonly type: 'text_chunk';
  readonly contentType: 'text';
  /** The incremental text added in this chunk. */
  readonly delta: string;
};

/**
 * Signals the end of a text content block in the stream.
 */
export type TextEndChunk = {
  readonly type: 'text_end_chunk';
  readonly contentType: 'text';
};

/** Create a TextStartChunk */
export function textStart(): TextStartChunk {
  return { type: 'text_start_chunk', contentType: 'text' };
}

/** Create a TextChunk */
export function textChunk(delta: string): TextChunk {
  return { type: 'text_chunk', contentType: 'text', delta };
}

/** Create a TextEndChunk */
export function textEnd(): TextEndChunk {
  return { type: 'text_end_chunk', contentType: 'text' };
}
