/**
 * Response types and utilities for LLM calls.
 */

export { FinishReason } from '@/llm/responses/finish-reason';
export type { FinishReason as FinishReasonType } from '@/llm/responses/finish-reason';

export { createUsage, totalTokens } from '@/llm/responses/usage';
export type { Usage } from '@/llm/responses/usage';

export { RootResponse } from '@/llm/responses/root-response';

export { BaseResponse } from '@/llm/responses/base-response';
export type { BaseResponseInit } from '@/llm/responses/base-response';

export { Response } from '@/llm/responses/response';
export type { ResponseInit } from '@/llm/responses/response';

export { ContextResponse } from '@/llm/responses/context-response';
export type { ContextResponseInit } from '@/llm/responses/context-response';

export { StreamResponse } from '@/llm/responses/stream-response';
export type { StreamResponseInit as StreamResponseInit } from '@/llm/responses/stream-response';

export { ContextStreamResponse } from '@/llm/responses/context-stream-response';
export type { ContextStreamResponseInit as ContextStreamResponseInit } from '@/llm/responses/context-stream-response';

// Streaming chunk types
export {
  textStart,
  textChunk,
  textEnd,
  thoughtStart,
  thoughtChunk,
  thoughtEnd,
  finishReasonChunk,
  usageDeltaChunk,
  rawStreamEventChunk,
  rawMessageChunk,
} from '@/llm/responses/chunks';

export type {
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
} from '@/llm/responses/chunks';
