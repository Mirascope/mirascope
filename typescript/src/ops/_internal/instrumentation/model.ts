/**
 * OpenTelemetry GenAI instrumentation for Model class methods.
 *
 * Provides wrapper functions to instrument LLM calls with tracing.
 */

import type { Context } from "@/llm/context";
import type { Format } from "@/llm/formatting";
import type { Message, UserContent } from "@/llm/messages";
import type { Response } from "@/llm/responses";
import type { ContextResponse } from "@/llm/responses/context-response";
import type { ContextStreamResponse } from "@/llm/responses/context-stream-response";
import type { RootResponse } from "@/llm/responses/root-response";
import type { StreamResponse } from "@/llm/responses/stream-response";
import type { Tools, ContextTools } from "@/llm/tools";
import type { BaseToolkit } from "@/llm/tools/toolkit";

import { promoteToMessages, user } from "@/llm/messages";
import { Model } from "@/llm/models";
import {
  startModelSpan,
  attachResponse,
  recordException,
  recordDroppedParams,
  withSpanContext,
} from "@/ops/_internal/instrumentation/common";

// =============================================================================
// Original method references and wrapped state flags
// =============================================================================

// call methods
const _ORIGINAL_MODEL_CALL = Model.prototype.call;
let _MODEL_CALL_WRAPPED = false;

// stream methods
const _ORIGINAL_MODEL_STREAM = Model.prototype.stream;
let _MODEL_STREAM_WRAPPED = false;

// contextCall methods
const _ORIGINAL_MODEL_CONTEXT_CALL = Model.prototype.contextCall;
let _MODEL_CONTEXT_CALL_WRAPPED = false;

// contextStream methods
const _ORIGINAL_MODEL_CONTEXT_STREAM = Model.prototype.contextStream;
let _MODEL_CONTEXT_STREAM_WRAPPED = false;

// resume methods
const _ORIGINAL_MODEL_RESUME = Model.prototype.resume;
let _MODEL_RESUME_WRAPPED = false;

// resumeStream methods
const _ORIGINAL_MODEL_RESUME_STREAM = Model.prototype.resumeStream;
let _MODEL_RESUME_STREAM_WRAPPED = false;

// contextResume methods
const _ORIGINAL_MODEL_CONTEXT_RESUME = Model.prototype.contextResume;
let _MODEL_CONTEXT_RESUME_WRAPPED = false;

// contextResumeStream methods
const _ORIGINAL_MODEL_CONTEXT_RESUME_STREAM =
  Model.prototype.contextResumeStream;
let _MODEL_CONTEXT_RESUME_STREAM_WRAPPED = false;

// =============================================================================
// Model.call instrumentation
// =============================================================================

/**
 * Instrumented version of Model.call.
 */
/* v8 ignore start - requires actual LLM calls, tested in E2E */
async function _instrumentedModelCall(
  this: Model,
  content: UserContent | readonly Message[],
  options?: { tools?: Tools; format?: Format | null },
): Promise<Response> {
  const messages = promoteToMessages(content);
  const spanCtx = startModelSpan({
    modelId: this.modelId,
    providerId: this.providerId,
    messages,
    tools: options?.tools,
    format: options?.format,
    params: this.params,
  });

  try {
    const response = await withSpanContext(spanCtx.span, () =>
      _ORIGINAL_MODEL_CALL.call(this, content, options),
    );

    if (spanCtx.span) {
      attachResponse(spanCtx.span, response, messages);
      recordDroppedParams(spanCtx.span, spanCtx.droppedParams);
    }

    return response;
  } catch (error) {
    if (spanCtx.span && error instanceof Error) {
      recordException(spanCtx.span, error);
    }
    throw error;
  } finally {
    spanCtx.span?.end();
  }
}
/* v8 ignore end */

/**
 * Replace Model.call with the instrumented wrapper.
 */
export function wrapModelCall(): void {
  if (_MODEL_CALL_WRAPPED) {
    return;
  }
  Model.prototype.call = _instrumentedModelCall;
  _MODEL_CALL_WRAPPED = true;
}

/**
 * Restore the original Model.call implementation.
 */
export function unwrapModelCall(): void {
  if (!_MODEL_CALL_WRAPPED) {
    return;
  }
  Model.prototype.call = _ORIGINAL_MODEL_CALL;
  _MODEL_CALL_WRAPPED = false;
}

// =============================================================================
// Model.stream instrumentation
// =============================================================================

/**
 * Instrumented version of Model.stream.
 *
 * Note: For streaming, we create the span but can't attach full response
 * until the stream is consumed. The span covers the initial request.
 */
/* v8 ignore start - requires actual LLM calls, tested in E2E */
async function _instrumentedModelStream(
  this: Model,
  content: UserContent | readonly Message[],
  options?: { tools?: Tools; format?: Format | null },
): Promise<StreamResponse> {
  const messages = promoteToMessages(content);
  const spanCtx = startModelSpan({
    modelId: this.modelId,
    providerId: this.providerId,
    messages,
    tools: options?.tools,
    format: options?.format,
    params: this.params,
  });

  try {
    const response = await withSpanContext(spanCtx.span, () =>
      _ORIGINAL_MODEL_STREAM.call(this, content, options),
    );

    if (spanCtx.span) {
      // For streaming, set basic attributes now
      // Full response attributes will be available after stream consumption
      spanCtx.span.setAttribute("gen_ai.response.model", this.modelId);
      recordDroppedParams(spanCtx.span, spanCtx.droppedParams);
    }

    return response;
  } catch (error) {
    if (spanCtx.span && error instanceof Error) {
      recordException(spanCtx.span, error);
    }
    throw error;
  } finally {
    spanCtx.span?.end();
  }
}
/* v8 ignore end */

/**
 * Replace Model.stream with the instrumented wrapper.
 */
export function wrapModelStream(): void {
  if (_MODEL_STREAM_WRAPPED) {
    return;
  }
  Model.prototype.stream = _instrumentedModelStream;
  _MODEL_STREAM_WRAPPED = true;
}

/**
 * Restore the original Model.stream implementation.
 */
export function unwrapModelStream(): void {
  if (!_MODEL_STREAM_WRAPPED) {
    return;
  }
  Model.prototype.stream = _ORIGINAL_MODEL_STREAM;
  _MODEL_STREAM_WRAPPED = false;
}

// =============================================================================
// Model.contextCall instrumentation
// =============================================================================

/**
 * Instrumented version of Model.contextCall.
 */
/* v8 ignore start - requires actual LLM calls, tested in E2E */
async function _instrumentedModelContextCall<DepsT>(
  this: Model,
  ctx: Context<DepsT>,
  content: UserContent | readonly Message[],
  options?: { tools?: ContextTools<DepsT>; format?: Format | null },
): Promise<ContextResponse<DepsT>> {
  const messages = promoteToMessages(content);
  const spanCtx = startModelSpan({
    modelId: this.modelId,
    providerId: this.providerId,
    messages,
    tools: options?.tools as Tools | undefined,
    format: options?.format,
    params: this.params,
  });

  try {
    const response = await withSpanContext(spanCtx.span, () =>
      _ORIGINAL_MODEL_CONTEXT_CALL.call(this, ctx, content, options),
    );

    if (spanCtx.span) {
      attachResponse(spanCtx.span, response, messages);
      recordDroppedParams(spanCtx.span, spanCtx.droppedParams);
    }

    return response;
  } catch (error) {
    if (spanCtx.span && error instanceof Error) {
      recordException(spanCtx.span, error);
    }
    throw error;
  } finally {
    spanCtx.span?.end();
  }
}
/* v8 ignore end */

/**
 * Replace Model.contextCall with the instrumented wrapper.
 */
export function wrapModelContextCall(): void {
  if (_MODEL_CONTEXT_CALL_WRAPPED) {
    return;
  }
  Model.prototype.contextCall = _instrumentedModelContextCall;
  _MODEL_CONTEXT_CALL_WRAPPED = true;
}

/**
 * Restore the original Model.contextCall implementation.
 */
export function unwrapModelContextCall(): void {
  if (!_MODEL_CONTEXT_CALL_WRAPPED) {
    return;
  }
  Model.prototype.contextCall = _ORIGINAL_MODEL_CONTEXT_CALL;
  _MODEL_CONTEXT_CALL_WRAPPED = false;
}

// =============================================================================
// Model.contextStream instrumentation
// =============================================================================

/**
 * Instrumented version of Model.contextStream.
 */
/* v8 ignore start - requires actual LLM calls, tested in E2E */
async function _instrumentedModelContextStream<DepsT>(
  this: Model,
  ctx: Context<DepsT>,
  content: UserContent | readonly Message[],
  options?: { tools?: ContextTools<DepsT>; format?: Format | null },
): Promise<ContextStreamResponse<DepsT>> {
  const messages = promoteToMessages(content);
  const spanCtx = startModelSpan({
    modelId: this.modelId,
    providerId: this.providerId,
    messages,
    tools: options?.tools as Tools | undefined,
    format: options?.format,
    params: this.params,
  });

  try {
    const response = await withSpanContext(spanCtx.span, () =>
      _ORIGINAL_MODEL_CONTEXT_STREAM.call(this, ctx, content, options),
    );

    if (spanCtx.span) {
      spanCtx.span.setAttribute("gen_ai.response.model", this.modelId);
      recordDroppedParams(spanCtx.span, spanCtx.droppedParams);
    }

    return response;
  } catch (error) {
    if (spanCtx.span && error instanceof Error) {
      recordException(spanCtx.span, error);
    }
    throw error;
  } finally {
    spanCtx.span?.end();
  }
}
/* v8 ignore end */

/**
 * Replace Model.contextStream with the instrumented wrapper.
 */
export function wrapModelContextStream(): void {
  if (_MODEL_CONTEXT_STREAM_WRAPPED) {
    return;
  }
  Model.prototype.contextStream = _instrumentedModelContextStream;
  _MODEL_CONTEXT_STREAM_WRAPPED = true;
}

/**
 * Restore the original Model.contextStream implementation.
 */
export function unwrapModelContextStream(): void {
  if (!_MODEL_CONTEXT_STREAM_WRAPPED) {
    return;
  }
  Model.prototype.contextStream = _ORIGINAL_MODEL_CONTEXT_STREAM;
  _MODEL_CONTEXT_STREAM_WRAPPED = false;
}

// =============================================================================
// Model.resume instrumentation
// =============================================================================

/**
 * Get toolkit from a response if available.
 */
/* v8 ignore start - used by instrumented functions */
function getResponseToolkit(
  response: RootResponse,
): BaseToolkit | Tools | undefined {
  // Check if the response has a toolkit property (BaseResponse subclasses do)
  if ("toolkit" in response && response.toolkit) {
    return response.toolkit as BaseToolkit;
  }
  return undefined;
}
/* v8 ignore end */

/**
 * Instrumented version of Model.resume.
 */
/* v8 ignore start - requires actual LLM calls, tested in E2E */
async function _instrumentedModelResume(
  this: Model,
  response: RootResponse,
  content: UserContent,
): Promise<Response> {
  // For resume, we build messages from the previous response + new content
  const userMessage = user(content);
  const messages: readonly Message[] = [...response.messages, userMessage];
  const spanCtx = startModelSpan({
    modelId: this.modelId,
    providerId: this.providerId,
    messages,
    tools: getResponseToolkit(response),
    format: response.format,
    params: this.params,
  });

  try {
    const newResponse = await withSpanContext(spanCtx.span, () =>
      _ORIGINAL_MODEL_RESUME.call(this, response, content),
    );

    if (spanCtx.span) {
      attachResponse(spanCtx.span, newResponse, messages);
      recordDroppedParams(spanCtx.span, spanCtx.droppedParams);
    }

    return newResponse;
  } catch (error) {
    if (spanCtx.span && error instanceof Error) {
      recordException(spanCtx.span, error);
    }
    throw error;
  } finally {
    spanCtx.span?.end();
  }
}
/* v8 ignore end */

/**
 * Replace Model.resume with the instrumented wrapper.
 */
export function wrapModelResume(): void {
  if (_MODEL_RESUME_WRAPPED) {
    return;
  }
  Model.prototype.resume = _instrumentedModelResume;
  _MODEL_RESUME_WRAPPED = true;
}

/**
 * Restore the original Model.resume implementation.
 */
export function unwrapModelResume(): void {
  if (!_MODEL_RESUME_WRAPPED) {
    return;
  }
  Model.prototype.resume = _ORIGINAL_MODEL_RESUME;
  _MODEL_RESUME_WRAPPED = false;
}

// =============================================================================
// Model.resumeStream instrumentation
// =============================================================================

/**
 * Instrumented version of Model.resumeStream.
 */
/* v8 ignore start - requires actual LLM calls, tested in E2E */
async function _instrumentedModelResumeStream(
  this: Model,
  response: RootResponse,
  content: UserContent,
): Promise<StreamResponse> {
  const userMessage = user(content);
  const messages: readonly Message[] = [...response.messages, userMessage];
  const spanCtx = startModelSpan({
    modelId: this.modelId,
    providerId: this.providerId,
    messages,
    tools: getResponseToolkit(response),
    format: response.format,
    params: this.params,
  });

  try {
    const newResponse = await withSpanContext(spanCtx.span, () =>
      _ORIGINAL_MODEL_RESUME_STREAM.call(this, response, content),
    );

    if (spanCtx.span) {
      spanCtx.span.setAttribute("gen_ai.response.model", this.modelId);
      recordDroppedParams(spanCtx.span, spanCtx.droppedParams);
    }

    return newResponse;
  } catch (error) {
    if (spanCtx.span && error instanceof Error) {
      recordException(spanCtx.span, error);
    }
    throw error;
  } finally {
    spanCtx.span?.end();
  }
}
/* v8 ignore end */

/**
 * Replace Model.resumeStream with the instrumented wrapper.
 */
export function wrapModelResumeStream(): void {
  if (_MODEL_RESUME_STREAM_WRAPPED) {
    return;
  }
  Model.prototype.resumeStream = _instrumentedModelResumeStream;
  _MODEL_RESUME_STREAM_WRAPPED = true;
}

/**
 * Restore the original Model.resumeStream implementation.
 */
export function unwrapModelResumeStream(): void {
  if (!_MODEL_RESUME_STREAM_WRAPPED) {
    return;
  }
  Model.prototype.resumeStream = _ORIGINAL_MODEL_RESUME_STREAM;
  _MODEL_RESUME_STREAM_WRAPPED = false;
}

// =============================================================================
// Model.contextResume instrumentation
// =============================================================================

/**
 * Instrumented version of Model.contextResume.
 */
/* v8 ignore start - requires actual LLM calls, tested in E2E */
async function _instrumentedModelContextResume<DepsT>(
  this: Model,
  ctx: Context<DepsT>,
  response: RootResponse,
  content: UserContent,
): Promise<ContextResponse<DepsT>> {
  const userMessage = user(content);
  const messages: readonly Message[] = [...response.messages, userMessage];
  const spanCtx = startModelSpan({
    modelId: this.modelId,
    providerId: this.providerId,
    messages,
    tools: getResponseToolkit(response),
    format: response.format,
    params: this.params,
  });

  try {
    const newResponse = await withSpanContext(spanCtx.span, () =>
      _ORIGINAL_MODEL_CONTEXT_RESUME.call(this, ctx, response, content),
    );

    if (spanCtx.span) {
      attachResponse(spanCtx.span, newResponse, messages);
      recordDroppedParams(spanCtx.span, spanCtx.droppedParams);
    }

    return newResponse;
  } catch (error) {
    if (spanCtx.span && error instanceof Error) {
      recordException(spanCtx.span, error);
    }
    throw error;
  } finally {
    spanCtx.span?.end();
  }
}
/* v8 ignore end */

/**
 * Replace Model.contextResume with the instrumented wrapper.
 */
export function wrapModelContextResume(): void {
  if (_MODEL_CONTEXT_RESUME_WRAPPED) {
    return;
  }
  Model.prototype.contextResume = _instrumentedModelContextResume;
  _MODEL_CONTEXT_RESUME_WRAPPED = true;
}

/**
 * Restore the original Model.contextResume implementation.
 */
export function unwrapModelContextResume(): void {
  if (!_MODEL_CONTEXT_RESUME_WRAPPED) {
    return;
  }
  Model.prototype.contextResume = _ORIGINAL_MODEL_CONTEXT_RESUME;
  _MODEL_CONTEXT_RESUME_WRAPPED = false;
}

// =============================================================================
// Model.contextResumeStream instrumentation
// =============================================================================

/**
 * Instrumented version of Model.contextResumeStream.
 */
/* v8 ignore start - requires actual LLM calls, tested in E2E */
async function _instrumentedModelContextResumeStream<DepsT>(
  this: Model,
  ctx: Context<DepsT>,
  response: RootResponse,
  content: UserContent,
): Promise<ContextStreamResponse<DepsT>> {
  const userMessage = user(content);
  const messages: readonly Message[] = [...response.messages, userMessage];
  const spanCtx = startModelSpan({
    modelId: this.modelId,
    providerId: this.providerId,
    messages,
    tools: getResponseToolkit(response),
    format: response.format,
    params: this.params,
  });

  try {
    const newResponse = await withSpanContext(spanCtx.span, () =>
      _ORIGINAL_MODEL_CONTEXT_RESUME_STREAM.call(this, ctx, response, content),
    );

    if (spanCtx.span) {
      spanCtx.span.setAttribute("gen_ai.response.model", this.modelId);
      recordDroppedParams(spanCtx.span, spanCtx.droppedParams);
    }

    return newResponse;
  } catch (error) {
    if (spanCtx.span && error instanceof Error) {
      recordException(spanCtx.span, error);
    }
    throw error;
  } finally {
    spanCtx.span?.end();
  }
}
/* v8 ignore end */

/**
 * Replace Model.contextResumeStream with the instrumented wrapper.
 */
export function wrapModelContextResumeStream(): void {
  if (_MODEL_CONTEXT_RESUME_STREAM_WRAPPED) {
    return;
  }
  Model.prototype.contextResumeStream = _instrumentedModelContextResumeStream;
  _MODEL_CONTEXT_RESUME_STREAM_WRAPPED = true;
}

/**
 * Restore the original Model.contextResumeStream implementation.
 */
export function unwrapModelContextResumeStream(): void {
  if (!_MODEL_CONTEXT_RESUME_STREAM_WRAPPED) {
    return;
  }
  Model.prototype.contextResumeStream = _ORIGINAL_MODEL_CONTEXT_RESUME_STREAM;
  _MODEL_CONTEXT_RESUME_STREAM_WRAPPED = false;
}

// =============================================================================
// Convenience functions to wrap/unwrap all methods
// =============================================================================

/**
 * Wrap all Model methods with instrumentation.
 */
export function wrapAllModelMethods(): void {
  wrapModelCall();
  wrapModelStream();
  wrapModelContextCall();
  wrapModelContextStream();
  wrapModelResume();
  wrapModelResumeStream();
  wrapModelContextResume();
  wrapModelContextResumeStream();
}

/**
 * Unwrap all Model methods, restoring original implementations.
 */
export function unwrapAllModelMethods(): void {
  unwrapModelCall();
  unwrapModelStream();
  unwrapModelContextCall();
  unwrapModelContextStream();
  unwrapModelResume();
  unwrapModelResumeStream();
  unwrapModelContextResume();
  unwrapModelContextResumeStream();
}

/**
 * Check if any Model method is instrumented.
 */
export function isModelInstrumented(): boolean {
  return (
    _MODEL_CALL_WRAPPED ||
    _MODEL_STREAM_WRAPPED ||
    _MODEL_CONTEXT_CALL_WRAPPED ||
    _MODEL_CONTEXT_STREAM_WRAPPED ||
    _MODEL_RESUME_WRAPPED ||
    _MODEL_RESUME_STREAM_WRAPPED ||
    _MODEL_CONTEXT_RESUME_WRAPPED ||
    _MODEL_CONTEXT_RESUME_STREAM_WRAPPED
  );
}
