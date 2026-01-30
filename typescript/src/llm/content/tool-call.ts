/**
 * Tool call content from an assistant message.
 *
 * Represents a request from the assistant to call a tool/function.
 * The args field contains the stringified JSON arguments.
 */
export type ToolCall = {
  readonly type: "tool_call";

  /** A unique identifier for this tool call. */
  readonly id: string;

  /** The name of the tool to call. */
  readonly name: string;

  /** The arguments to pass to the tool, stored as stringified JSON. */
  readonly args: string;
};

/**
 * Signals the start of a tool call in the stream.
 */
export type ToolCallStartChunk = {
  readonly type: "tool_call_start_chunk";
  readonly contentType: "tool_call";
  /** Unique identifier for this tool call. */
  readonly id: string;
  /** The name of the tool to call. */
  readonly name: string;
};

/**
 * Contains incremental tool call arguments (JSON).
 */
export type ToolCallChunk = {
  readonly type: "tool_call_chunk";
  readonly contentType: "tool_call";
  /** Unique identifier for this tool call. */
  readonly id: string;
  /** The incremental JSON args added in this chunk. */
  readonly delta: string;
};

/**
 * Signals the end of a tool call in the stream.
 */
export type ToolCallEndChunk = {
  readonly type: "tool_call_end_chunk";
  readonly contentType: "tool_call";
  /** Unique identifier for this tool call. */
  readonly id: string;
};

/** Create a ToolCallStartChunk */
export function toolCallStart(id: string, name: string): ToolCallStartChunk {
  return { type: "tool_call_start_chunk", contentType: "tool_call", id, name };
}

/** Create a ToolCallChunk */
export function toolCallChunk(id: string, delta: string): ToolCallChunk {
  return { type: "tool_call_chunk", contentType: "tool_call", id, delta };
}

/** Create a ToolCallEndChunk */
export function toolCallEnd(id: string): ToolCallEndChunk {
  return { type: "tool_call_end_chunk", contentType: "tool_call", id };
}
