/**
 * @fileoverview The `llm.content` module.
 */

import type { Audio } from './audio.js';
import type { Document } from './document.js';
import type { Image } from './image.js';
import type { Thinking } from './thinking.js';
import type { ToolCall } from './tool-call.js';
import type { ToolOutput } from './tool-output.js';
import type { Video } from './video.js';

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

export type { Audio } from './audio.js';
export type { Document } from './document.js';
export type { Image } from './image.js';
export type { Thinking } from './thinking.js';
export type { ToolCall } from './tool-call.js';
export type { ToolOutput } from './tool-output.js';
export type { Video } from './video.js';
