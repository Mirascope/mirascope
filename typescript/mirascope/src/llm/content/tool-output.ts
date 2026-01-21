/**
 * @fileoverview The `ToolOutput` content class.
 */

import type { Jsonable } from '../types';

/**
 * Tool output content for a message.
 *
 * Represents the output from a tool call. This is part of a user message's
 * content, typically following a tool call from the assistant.
 */
export type ToolOutput<R extends Jsonable = Jsonable> = {
  /** The content type identifier */
  type: 'tool-output';

  /** The ID of the tool call that this output is for. */
  id: string;

  /** The output value from the tool call. */
  value: R;
};
