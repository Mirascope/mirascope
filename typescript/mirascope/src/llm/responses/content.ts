/**
 * @fileoverview The content types for specific response types.
 */

import type { Audio, Image, Thinking, Video } from "../content";

/**
 * Base content response types that do not vary based on context.
 */
export type BaseResponseContent = 
  | string 
  | Image 
  | Audio 
  | Video 
  | Thinking;

/**
 * Content types that can be returned in a SimpleResponse (non-context).
 */
export type ResponseContent = BaseResponseContent;
