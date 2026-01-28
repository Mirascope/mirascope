export type { Jsonable } from '@/llm/types';

export type {
  AnthropicModelId,
  GoogleModelId,
  OpenAIModelId,
  ApiMode,
  KnownProviderId,
  ModelId,
  ProviderId,
} from '@/llm/providers';
export { KNOWN_PROVIDER_IDS } from '@/llm/providers';

export { type Context, createContext } from '@/llm/context';

export type {
  AssistantContentPart,
  ContentPart,
  UserContentPart,
} from '@/llm/content';

export type { Text, Thought, ToolCall } from '@/llm/content';

export {
  Audio,
  type AudioMimeType,
  type Base64AudioSource,
} from '@/llm/content';

export {
  Document,
  type Base64DocumentSource,
  type DocumentBase64MimeType,
  type DocumentTextMimeType,
  type TextDocumentSource,
  type URLDocumentSource,
} from '@/llm/content';

export {
  Image,
  type Base64ImageSource,
  type ImageMimeType,
  type URLImageSource,
} from '@/llm/content';

export { ToolOutput } from '@/llm/content';

export type {
  AssistantContent,
  AssistantMessage,
  Message,
  SystemContent,
  SystemMessage,
  UserContent,
  UserMessage,
} from '@/llm/messages';

import * as messages from '@/llm/messages';
export { messages };

export {
  MirascopeError,
  ProviderError,
  APIError,
  AuthenticationError,
  PermissionError,
  BadRequestError,
  NotFoundError,
  RateLimitError,
  ServerError,
  ConnectionError,
  TimeoutError,
  ResponseValidationError,
  ToolError,
  ToolExecutionError,
  ToolNotFoundError,
  ParseError,
  FeatureNotSupportedError,
  NoRegisteredProviderError,
  MissingAPIKeyError,
} from '@/llm/exceptions';

export type { Params, ThinkingConfig, ThinkingLevel } from '@/llm/models';
export { Model, model } from '@/llm/models';

export {
  definePrompt,
  type MessageTemplate,
  type Prompt,
  type PromptArgs,
  type TemplateFunc,
  defineContextPrompt,
  type ContextMessageTemplate,
  type ContextPrompt,
  type ContextPromptArgs,
  type ContextTemplateFunc,
} from '@/llm/prompts';

export {
  defineCall,
  type Call,
  type CallArgs,
  defineContextCall,
  type ContextCall,
  type ContextCallArgs,
} from '@/llm/calls';

export {
  getProviderForModel,
  registerProvider,
  resetProviderRegistry,
} from '@/llm/providers';

export {
  FinishReason,
  RootResponse,
  BaseResponse,
  Response,
  ContextResponse,
  StreamResponse,
  ContextStreamResponse,
  createUsage,
  totalTokens,
} from '@/llm/responses';
export type {
  FinishReasonType,
  Usage,
  BaseResponseInit,
  ResponseInit,
  ContextResponseInit,
  StreamResponseInit,
  ContextStreamResponseInit,
  // Streaming chunk types
  TextStartChunk,
  TextChunk,
  TextEndChunk,
  ThoughtStartChunk,
  ThoughtChunk,
  ThoughtEndChunk,
  FinishReasonChunk,
  UsageDeltaChunk,
  RawStreamEventChunk,
  RawMessageChunk,
  AssistantContentChunk,
  StreamResponseChunk,
} from '@/llm/responses';
