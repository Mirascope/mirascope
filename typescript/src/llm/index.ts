export type { Jsonable } from "@/llm/types";

export type {
  AnthropicModelId,
  GoogleModelId,
  OpenAIModelId,
  ApiMode,
  KnownProviderId,
  ModelId,
  Provider,
  ProviderId,
} from "@/llm/providers";
export { KNOWN_PROVIDER_IDS } from "@/llm/providers";

export {
  type Context,
  createContext,
  isContext,
  CONTEXT_MARKER,
} from "@/llm/context";

export type {
  AssistantContentPart,
  AssistantContentChunk,
  ContentPart,
  UserContentPart,
} from "@/llm/content";

export type { Text, Thought, ToolCall } from "@/llm/content";

// Content chunk types (from content module, like Python)
export type {
  TextStartChunk,
  TextChunk,
  TextEndChunk,
  ThoughtStartChunk,
  ThoughtChunk,
  ThoughtEndChunk,
  ToolCallStartChunk,
  ToolCallChunk,
  ToolCallEndChunk,
} from "@/llm/content";

// Content chunk factory functions
export {
  textStart,
  textChunk,
  textEnd,
  thoughtStart,
  thoughtChunk,
  thoughtEnd,
  toolCallStart,
  toolCallChunk,
  toolCallEnd,
} from "@/llm/content";

export {
  Audio,
  type AudioMimeType,
  type Base64AudioSource,
} from "@/llm/content";

export {
  Document,
  type Base64DocumentSource,
  type DocumentBase64MimeType,
  type DocumentTextMimeType,
  type TextDocumentSource,
  type URLDocumentSource,
} from "@/llm/content";

export {
  Image,
  type Base64ImageSource,
  type ImageMimeType,
  type URLImageSource,
} from "@/llm/content";

export { ToolOutput } from "@/llm/content";

export {
  defineTool,
  defineContextTool,
  isZodLike,
  isContextTool,
  Toolkit,
  ContextToolkit,
  createToolkit,
  createContextToolkit,
  TOOL_TYPE,
  CONTEXT_TOOL_TYPE,
  ProviderTool,
  isProviderTool,
  WebSearchTool,
  isWebSearchTool,
} from "@/llm/tools";

export type {
  JsonSchemaProperty,
  ToolParameterSchema,
  ToolSchema,
  ZodLike,
  InferZod,
  ToolArgs,
  ContextToolArgs,
  ZodToolArgs,
  ZodContextToolArgs,
  BaseTool,
  BaseContextTool,
  Tool,
  ContextTool,
  AnyTool,
  AnyContextTool,
  Tools,
  ContextTools,
  ToolFn,
  ContextToolFn,
  AnyToolFn,
} from "@/llm/tools";

export type {
  AssistantContent,
  AssistantMessage,
  Message,
  SystemContent,
  SystemMessage,
  UserContent,
  UserMessage,
} from "@/llm/messages";

import * as messages from "@/llm/messages";
export { messages };

import * as mcp from "@/llm/mcp";
export { mcp };

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
  RetriesExhausted,
  StreamRestarted,
} from "@/llm/exceptions";
export type { RetryFailure } from "@/llm/retries/utils";

export type { Params, ThinkingConfig, ThinkingLevel } from "@/llm/models";

export {
  defineFormat,
  defineOutputParser,
  isFormat,
  isOutputParser,
  resolveFormat,
  FORMAT_TOOL_NAME,
  TOOL_MODE_INSTRUCTIONS,
  JSON_MODE_INSTRUCTIONS,
} from "@/llm/formatting";

export type {
  Format,
  FormatSpec,
  FormattingMode,
  OutputParser,
  OutputParserArgs,
  DeepPartial,
} from "@/llm/formatting";
export {
  Model,
  model,
  modelFromContext,
  useModel,
  withModel,
} from "@/llm/models";

export {
  definePrompt,
  type MessageTemplate,
  type Prompt,
  type PromptArgs,
  type TemplateFunc,
  // Context-aware types (unified API)
  type ContextMessageTemplate,
  type ContextPrompt,
  type ContextPromptArgs,
  type ContextTemplateFunc,
  // Type utilities
  type ExtractDeps,
  type ExtractVars,
  type UnifiedPrompt,
} from "@/llm/prompts";

export {
  defineCall,
  type Call,
  type CallArgs,
  // Context-aware types (unified API)
  type ContextCall,
  type ContextCallArgs,
  // Type utilities
  type UnifiedCall,
} from "@/llm/calls";

export {
  getProviderForModel,
  registerProvider,
  resetProviderRegistry,
} from "@/llm/providers";

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
} from "@/llm/responses";
export type { AnyResponse } from "@/llm/responses";
export type {
  FinishReasonType,
  Usage,
  BaseResponseInit,
  ResponseInit,
  ContextResponseInit,
  StreamResponseInit,
  ContextStreamResponseInit,
  // Metadata streaming chunk types (content chunks exported from content above)
  FinishReasonChunk,
  UsageDeltaChunk,
  RawStreamEventChunk,
  RawMessageChunk,
  StreamResponseChunk,
  AsyncChunkIterator,
} from "@/llm/responses";

// Retry module
export {
  RetryConfig,
  RetryModel,
  retryModel,
  getRetryModelFromContext,
  RetryResponse,
  ContextRetryResponse,
  RetryStreamResponse,
  ContextRetryStreamResponse,
  DEFAULT_RETRYABLE_ERRORS,
  DEFAULT_MAX_RETRIES,
  DEFAULT_INITIAL_DELAY,
  DEFAULT_MAX_DELAY,
  DEFAULT_BACKOFF_MULTIPLIER,
  DEFAULT_JITTER,
  calculateDelay,
  isRetryableError,
  sleep,
} from "@/llm/retries";

export type {
  RetryArgs,
  RetryModelParams,
  ErrorConstructor,
  RetryFailure as RetryFailureInfo,
} from "@/llm/retries";
