/**
 * Tool call content from an assistant message.
 *
 * Represents a request from the assistant to call a tool/function.
 * The args field contains the stringified JSON arguments.
 */
export type ToolCall = {
  readonly type: 'tool_call';

  /** A unique identifier for this tool call. */
  readonly id: string;

  /** The name of the tool to call. */
  readonly name: string;

  /** The arguments to pass to the tool, stored as stringified JSON. */
  readonly args: string;
};
