/**
 * @fileoverview The `llm.content` module.
 */

import type { Audio } from './audio';
import type { Document } from './document';
import type { Image } from './image';
import type { Thinking } from './thinking';
import type { ToolCall } from './tool-call';
import type { ToolOutput } from './tool-output';
import type { Video } from './video';

/* Content types that can be included in messages. */
export type Content =
  | string
  | Image
  | Audio
  | Video
  | Document
  | ToolCall
  | ToolOutput
  | Thinking;

export type { Audio } from './audio';
export type { Document } from './document';
export type { Image } from './image';
export type { Thinking } from './thinking';
export type { ToolCall } from './tool-call';
export type { ToolOutput } from './tool-output';
export type { Video } from './video';
