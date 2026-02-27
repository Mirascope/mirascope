/**
 * Mirascope-specific instrumentation for Response.resume methods.
 *
 * Provides wrapper functions to instrument Response resume calls with tracing,
 * matching the Python implementation pattern.
 */

import { context as otelContext, trace as otelTrace } from "@opentelemetry/api";

import type { Context } from "@/llm/context";
import type { UserContent } from "@/llm/messages";
import type { RootResponse } from "@/llm/responses/root-response";

import { ContextResponse } from "@/llm/responses/context-response";
import { ContextStreamResponse } from "@/llm/responses/context-stream-response";
import { Response } from "@/llm/responses/response";
import { StreamResponse } from "@/llm/responses/stream-response";
import { Span } from "@/ops/_internal/spans";
import { jsonStringify } from "@/ops/_internal/utils";

// =============================================================================
// Helper to attach response attributes
// =============================================================================

/**
 * Attach Mirascope-specific response attributes to a span.
 */
/* v8 ignore start - called from instrumented functions, tested in E2E */
function attachResponseAttributes(span: Span, response: RootResponse): void {
  span.set({
    "mirascope.trace.output": response.pretty(),
    "mirascope.response.messages": jsonStringify(
      response.messages
        .slice(0, -1)
        .map((m) => ({ role: m.role, content: m.content })),
    ),
    "mirascope.response.content": jsonStringify(response.content),
  });

  if (response.usage) {
    span.set({
      "mirascope.response.usage": jsonStringify({
        inputTokens: response.usage.inputTokens,
        outputTokens: response.usage.outputTokens,
        cacheReadTokens: response.usage.cacheReadTokens,
        cacheWriteTokens: response.usage.cacheWriteTokens,
        reasoningTokens: response.usage.reasoningTokens,
      }),
    });
  }
}
/* v8 ignore end */

// =============================================================================
// Original method references and wrapped state flags
// =============================================================================

// Response.resume
const _ORIGINAL_RESPONSE_RESUME = Response.prototype.resume;
let _RESPONSE_RESUME_WRAPPED = false;

// StreamResponse.resume
const _ORIGINAL_STREAM_RESPONSE_RESUME = StreamResponse.prototype.resume;
let _STREAM_RESPONSE_RESUME_WRAPPED = false;

// ContextResponse.resume
const _ORIGINAL_CONTEXT_RESPONSE_RESUME = ContextResponse.prototype.resume;
let _CONTEXT_RESPONSE_RESUME_WRAPPED = false;

// ContextStreamResponse.resume
const _ORIGINAL_CONTEXT_STREAM_RESPONSE_RESUME =
  ContextStreamResponse.prototype.resume;
let _CONTEXT_STREAM_RESPONSE_RESUME_WRAPPED = false;

// =============================================================================
// Response.resume instrumentation
// =============================================================================

/**
 * Instrumented version of Response.resume.
 */
/* v8 ignore start - requires actual LLM calls, tested in E2E */
async function _instrumentedResponseResume<F>(
  this: Response<F>,
  content: UserContent,
): Promise<Response<F>> {
  const span = new Span(`Response.resume ${this.modelId}`);
  span.start();

  span.set({
    "mirascope.type": "response_resume",
    "mirascope.response.model_id": this.modelId,
    "mirascope.response.provider_id": this.providerId,
  });

  const otelSpan = span.otelSpan;

  const execute = async (): Promise<Response<F>> => {
    try {
      const result = await _ORIGINAL_RESPONSE_RESUME.call(this, content);
      attachResponseAttributes(span, result);
      return result;
    } catch (error) {
      if (error instanceof Error) {
        span.recordException(error);
      } else {
        span.error(String(error));
      }
      throw error;
    } finally {
      span.finish();
    }
  };

  // Run within the span's context so child spans are properly linked
  return otelSpan
    ? otelContext.with(
        otelTrace.setSpan(otelContext.active(), otelSpan),
        execute,
      )
    : execute();
}
/* v8 ignore end */

/**
 * Replace Response.resume with the instrumented wrapper.
 */
export function wrapResponseResume(): void {
  if (_RESPONSE_RESUME_WRAPPED) {
    return;
  }
  Response.prototype.resume = _instrumentedResponseResume;
  _RESPONSE_RESUME_WRAPPED = true;
}

/**
 * Restore the original Response.resume implementation.
 */
export function unwrapResponseResume(): void {
  if (!_RESPONSE_RESUME_WRAPPED) {
    return;
  }
  Response.prototype.resume = _ORIGINAL_RESPONSE_RESUME;
  _RESPONSE_RESUME_WRAPPED = false;
}

// =============================================================================
// StreamResponse.resume instrumentation
// =============================================================================

/**
 * Instrumented version of StreamResponse.resume.
 */
/* v8 ignore start - requires actual LLM calls, tested in E2E */
async function _instrumentedStreamResponseResume<F>(
  this: StreamResponse<F>,
  content: UserContent,
): Promise<StreamResponse<F>> {
  const span = new Span(`StreamResponse.resume ${this.modelId}`);
  span.start();

  span.set({
    "mirascope.type": "response_resume",
    "mirascope.response.model_id": this.modelId,
    "mirascope.response.provider_id": this.providerId,
  });

  const otelSpan = span.otelSpan;

  const execute = async (): Promise<StreamResponse<F>> => {
    try {
      const result = await _ORIGINAL_STREAM_RESPONSE_RESUME.call(this, content);
      // Note: StreamResponse attributes will be attached after stream is consumed
      return result;
    } catch (error) {
      if (error instanceof Error) {
        span.recordException(error);
      } else {
        span.error(String(error));
      }
      throw error;
    } finally {
      span.finish();
    }
  };

  // Run within the span's context so child spans are properly linked
  return otelSpan
    ? otelContext.with(
        otelTrace.setSpan(otelContext.active(), otelSpan),
        execute,
      )
    : execute();
}
/* v8 ignore end */

/**
 * Replace StreamResponse.resume with the instrumented wrapper.
 */
export function wrapStreamResponseResume(): void {
  if (_STREAM_RESPONSE_RESUME_WRAPPED) {
    return;
  }
  StreamResponse.prototype.resume = _instrumentedStreamResponseResume;
  _STREAM_RESPONSE_RESUME_WRAPPED = true;
}

/**
 * Restore the original StreamResponse.resume implementation.
 */
export function unwrapStreamResponseResume(): void {
  if (!_STREAM_RESPONSE_RESUME_WRAPPED) {
    return;
  }
  StreamResponse.prototype.resume = _ORIGINAL_STREAM_RESPONSE_RESUME;
  _STREAM_RESPONSE_RESUME_WRAPPED = false;
}

// =============================================================================
// ContextResponse.resume instrumentation
// =============================================================================

/**
 * Instrumented version of ContextResponse.resume.
 */
/* v8 ignore start - requires actual LLM calls, tested in E2E */
async function _instrumentedContextResponseResume<DepsT, F>(
  this: ContextResponse<DepsT, F>,
  ctx: Context<DepsT>,
  content: UserContent,
): Promise<ContextResponse<DepsT, F>> {
  const span = new Span(`ContextResponse.resume ${this.modelId}`);
  span.start();

  span.set({
    "mirascope.type": "response_resume",
    "mirascope.response.model_id": this.modelId,
    "mirascope.response.provider_id": this.providerId,
  });

  const otelSpan = span.otelSpan;

  const execute = async (): Promise<ContextResponse<DepsT, F>> => {
    try {
      const result = await _ORIGINAL_CONTEXT_RESPONSE_RESUME.call(
        this,
        ctx,
        content,
      );
      attachResponseAttributes(span, result);
      return result as ContextResponse<DepsT, F>;
    } catch (error) {
      if (error instanceof Error) {
        span.recordException(error);
      } else {
        span.error(String(error));
      }
      throw error;
    } finally {
      span.finish();
    }
  };

  // Run within the span's context so child spans are properly linked
  return otelSpan
    ? otelContext.with(
        otelTrace.setSpan(otelContext.active(), otelSpan),
        execute,
      )
    : execute();
}
/* v8 ignore end */

/**
 * Replace ContextResponse.resume with the instrumented wrapper.
 */
export function wrapContextResponseResume(): void {
  if (_CONTEXT_RESPONSE_RESUME_WRAPPED) {
    return;
  }
  ContextResponse.prototype.resume = _instrumentedContextResponseResume;
  _CONTEXT_RESPONSE_RESUME_WRAPPED = true;
}

/**
 * Restore the original ContextResponse.resume implementation.
 */
export function unwrapContextResponseResume(): void {
  if (!_CONTEXT_RESPONSE_RESUME_WRAPPED) {
    return;
  }
  ContextResponse.prototype.resume = _ORIGINAL_CONTEXT_RESPONSE_RESUME;
  _CONTEXT_RESPONSE_RESUME_WRAPPED = false;
}

// =============================================================================
// ContextStreamResponse.resume instrumentation
// =============================================================================

/**
 * Instrumented version of ContextStreamResponse.resume.
 */
/* v8 ignore start - requires actual LLM calls, tested in E2E */
async function _instrumentedContextStreamResponseResume<DepsT, F>(
  this: ContextStreamResponse<DepsT, F>,
  ctx: Context<DepsT>,
  content: UserContent,
): Promise<ContextStreamResponse<DepsT, F>> {
  const span = new Span(`ContextStreamResponse.resume ${this.modelId}`);
  span.start();

  span.set({
    "mirascope.type": "response_resume",
    "mirascope.response.model_id": this.modelId,
    "mirascope.response.provider_id": this.providerId,
  });

  const otelSpan = span.otelSpan;

  const execute = async (): Promise<ContextStreamResponse<DepsT, F>> => {
    try {
      const result = await _ORIGINAL_CONTEXT_STREAM_RESPONSE_RESUME.call(
        this,
        ctx,
        content,
      );
      // Note: StreamResponse attributes will be attached after stream is consumed
      return result as ContextStreamResponse<DepsT, F>;
    } catch (error) {
      if (error instanceof Error) {
        span.recordException(error);
      } else {
        span.error(String(error));
      }
      throw error;
    } finally {
      span.finish();
    }
  };

  // Run within the span's context so child spans are properly linked
  return otelSpan
    ? otelContext.with(
        otelTrace.setSpan(otelContext.active(), otelSpan),
        execute,
      )
    : execute();
}
/* v8 ignore end */

/**
 * Replace ContextStreamResponse.resume with the instrumented wrapper.
 */
export function wrapContextStreamResponseResume(): void {
  if (_CONTEXT_STREAM_RESPONSE_RESUME_WRAPPED) {
    return;
  }
  ContextStreamResponse.prototype.resume =
    _instrumentedContextStreamResponseResume;
  _CONTEXT_STREAM_RESPONSE_RESUME_WRAPPED = true;
}

/**
 * Restore the original ContextStreamResponse.resume implementation.
 */
export function unwrapContextStreamResponseResume(): void {
  if (!_CONTEXT_STREAM_RESPONSE_RESUME_WRAPPED) {
    return;
  }
  ContextStreamResponse.prototype.resume =
    _ORIGINAL_CONTEXT_STREAM_RESPONSE_RESUME;
  _CONTEXT_STREAM_RESPONSE_RESUME_WRAPPED = false;
}

// =============================================================================
// Convenience functions to wrap/unwrap all methods
// =============================================================================

/**
 * Wrap all Response resume methods with instrumentation.
 */
export function wrapAllResponseResumeMethods(): void {
  wrapResponseResume();
  wrapStreamResponseResume();
  wrapContextResponseResume();
  wrapContextStreamResponseResume();
}

/**
 * Unwrap all Response resume methods, restoring original implementations.
 */
export function unwrapAllResponseResumeMethods(): void {
  unwrapResponseResume();
  unwrapStreamResponseResume();
  unwrapContextResponseResume();
  unwrapContextStreamResponseResume();
}

/**
 * Check if any Response resume method is instrumented.
 */
export function isResponseResumeInstrumented(): boolean {
  return (
    _RESPONSE_RESUME_WRAPPED ||
    _STREAM_RESPONSE_RESUME_WRAPPED ||
    _CONTEXT_RESPONSE_RESUME_WRAPPED ||
    _CONTEXT_STREAM_RESPONSE_RESUME_WRAPPED
  );
}
