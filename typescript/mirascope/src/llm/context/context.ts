/**
 * @fileoverview The `Context` type and its utility constructors
 */

import type { Message } from '../messages';

/**
 * Context for LLM calls.
 *
 * This class provides a context for LLM calls, including the model,
 * parameters, and any dependencies needed for the call.
 *
 * @property messages - The array of messages that have been sent so far (i.e. history).
 *
 * @property deps - The dependencies needed for a call.
 */
export type Context<DepsT = undefined> = DepsT extends undefined
  ? { messages: Message[] }
  : { messages: Message[]; deps: DepsT };
