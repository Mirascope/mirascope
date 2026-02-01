import type { Audio } from '@/llm/content/audio';
import type { Document } from '@/llm/content/document';
import type { Image } from '@/llm/content/image';
import type { Text } from '@/llm/content/text';
import type { Thought } from '@/llm/content/thought';
import type { ToolCall } from '@/llm/content/tool-call';
import type { ToolOutput } from '@/llm/content/tool-output';

/**
 * All content types that can appear in messages.
 */
export type ContentPart =
  | Text
  | Image
  | Audio
  | Document
  | ToolOutput
  | ToolCall
  | Thought;

/**
 * Content types that can appear in user messages.
 */
export type UserContentPart = Text | Image | Audio | Document | ToolOutput;

/**
 * Content types that can appear in assistant messages.
 */
export type AssistantContentPart = Text | ToolCall | Thought;

/**
 * Individual content type exports
 */
export type { Text } from '@/llm/content/text';
export type { Thought } from '@/llm/content/thought';
export type { ToolCall } from '@/llm/content/tool-call';
export {
  Audio,
  type AudioMimeType,
  type Base64AudioSource,
} from '@/llm/content/audio';
export {
  Document,
  type Base64DocumentSource,
  type DocumentBase64MimeType,
  type DocumentTextMimeType,
  type TextDocumentSource,
  type URLDocumentSource,
} from '@/llm/content/document';
export {
  Image,
  type Base64ImageSource,
  type ImageMimeType,
  type URLImageSource,
} from '@/llm/content/image';
export { ToolOutput } from '@/llm/content/tool-output';
