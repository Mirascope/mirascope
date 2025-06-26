/**
 * @fileoverview The `ToolCall` content class.
 */

import type { Jsonable } from '../types';

/**
 * Tool call content for a message.
 *
 * Represents a request from the assistant to call a tool. This is part of
 * an assistant message's content.
 */
export type ToolCall = {
  /** The content type identifier */
  type: 'tool-call';

  /** A unique identifier for this tool call. */
  id: string;

  /** The name of the tool to call. */
  name: string;

  /** The arguments to pass to the tool. */
  args: Record<string, Jsonable>;
};
