/**
 * Shared utilities for OpenTelemetry GenAI instrumentation.
 *
 * Provides common helpers for creating spans, building attributes,
 * and attaching response data following GenAI semantic conventions.
 */

import {
  type Span as OtelSpan,
  SpanKind,
  SpanStatusCode,
  trace,
  context as otelContext,
} from "@opentelemetry/api";

import type { Format } from "@/llm/formatting";
import type { Message } from "@/llm/messages";
import type { Params } from "@/llm/models/params";
import type { ModelId, ProviderId } from "@/llm/providers";
import type { RootResponse } from "@/llm/responses/root-response";
import type { Tools, BaseTool } from "@/llm/tools";
import type { ProviderTool } from "@/llm/tools/provider-tool";
import type { BaseToolkit } from "@/llm/tools/toolkit";
import type { Jsonable } from "@/ops/_internal/types";

import { getTracer } from "@/ops/_internal/configuration";
import { jsonStringify } from "@/ops/_internal/utils";

/**
 * GenAI semantic convention attribute names.
 *
 * Based on OpenTelemetry Semantic Conventions for GenAI.
 * @see https://opentelemetry.io/docs/specs/semconv/gen-ai/
 */
export const GenAIAttributes = {
  // Operation
  OPERATION_NAME: "gen_ai.operation.name",
  PROVIDER_NAME: "gen_ai.system",

  // Request attributes
  REQUEST_MODEL: "gen_ai.request.model",
  REQUEST_TEMPERATURE: "gen_ai.request.temperature",
  REQUEST_MAX_TOKENS: "gen_ai.request.max_tokens",
  REQUEST_TOP_P: "gen_ai.request.top_p",
  REQUEST_TOP_K: "gen_ai.request.top_k",
  REQUEST_FREQUENCY_PENALTY: "gen_ai.request.frequency_penalty",
  REQUEST_PRESENCE_PENALTY: "gen_ai.request.presence_penalty",
  REQUEST_SEED: "gen_ai.request.seed",
  REQUEST_STOP_SEQUENCES: "gen_ai.request.stop_sequences",
  REQUEST_CHOICE_COUNT: "gen_ai.request.choice_count",

  // Message attributes
  SYSTEM_INSTRUCTIONS: "gen_ai.system_instructions",
  INPUT_MESSAGES: "gen_ai.input_messages",
  OUTPUT_MESSAGES: "gen_ai.output_messages",

  // Tool attributes
  TOOL_DEFINITIONS: "gen_ai.tool.definitions",

  // Response attributes
  RESPONSE_MODEL: "gen_ai.response.model",
  RESPONSE_FINISH_REASONS: "gen_ai.response.finish_reasons",
  RESPONSE_ID: "gen_ai.response.id",

  // Usage attributes
  USAGE_INPUT_TOKENS: "gen_ai.usage.input_tokens",
  USAGE_OUTPUT_TOKENS: "gen_ai.usage.output_tokens",

  // Output type
  OUTPUT_TYPE: "gen_ai.output_type",
} as const;

/**
 * Mapping of Params keys to GenAI attribute names.
 */
const PARAM_ATTRIBUTE_MAP: Record<string, string> = {
  temperature: GenAIAttributes.REQUEST_TEMPERATURE,
  maxTokens: GenAIAttributes.REQUEST_MAX_TOKENS,
  max_tokens: GenAIAttributes.REQUEST_MAX_TOKENS,
  topP: GenAIAttributes.REQUEST_TOP_P,
  top_p: GenAIAttributes.REQUEST_TOP_P,
  topK: GenAIAttributes.REQUEST_TOP_K,
  top_k: GenAIAttributes.REQUEST_TOP_K,
  frequencyPenalty: GenAIAttributes.REQUEST_FREQUENCY_PENALTY,
  frequency_penalty: GenAIAttributes.REQUEST_FREQUENCY_PENALTY,
  presencePenalty: GenAIAttributes.REQUEST_PRESENCE_PENALTY,
  presence_penalty: GenAIAttributes.REQUEST_PRESENCE_PENALTY,
  seed: GenAIAttributes.REQUEST_SEED,
  stopSequences: GenAIAttributes.REQUEST_STOP_SEQUENCES,
  stop_sequences: GenAIAttributes.REQUEST_STOP_SEQUENCES,
  stop: GenAIAttributes.REQUEST_STOP_SEQUENCES,
  n: GenAIAttributes.REQUEST_CHOICE_COUNT,
  choiceCount: GenAIAttributes.REQUEST_CHOICE_COUNT,
};

/**
 * Context for a GenAI span including dropped parameters.
 */
export interface SpanContext {
  /** The active span, or null if no tracer configured */
  span: OtelSpan | null;
  /** Parameters that couldn't be recorded as span attributes */
  droppedParams: Record<string, Jsonable>;
}

/**
 * Record an exception on a span following OpenTelemetry semantic conventions.
 */
export function recordException(span: OtelSpan, error: Error): void {
  span.recordException(error);
  span.setAttribute("error.type", error.name);
  if (error.message) {
    span.setAttribute("error.message", error.message);
  }
  span.setStatus({ code: SpanStatusCode.ERROR, message: error.message });
}

/**
 * Infer the GenAI output type from the format parameter.
 */
function inferOutputType(format: Format | null | undefined): string {
  if (!format) {
    return "text";
  }
  return "json";
}

/**
 * Check if a value can be recorded as an OpenTelemetry attribute.
 */
function isSupportedParamValue(
  value: unknown,
): value is string | number | boolean | string[] | null | undefined {
  if (
    value === null ||
    value === undefined ||
    typeof value === "string" ||
    typeof value === "number" ||
    typeof value === "boolean"
  ) {
    return true;
  }
  if (Array.isArray(value)) {
    return value.every((item) => typeof item === "string");
  }
  return false;
}

/**
 * Normalize an unsupported value to a JSON-safe representation.
 */
function normalizeDroppedValue(value: unknown): Jsonable {
  if (
    value === null ||
    value === undefined ||
    typeof value === "string" ||
    typeof value === "number" ||
    typeof value === "boolean"
  ) {
    return value ?? null;
  }
  if (typeof value === "object" && value !== null) {
    if (Array.isArray(value)) {
      return value.map(normalizeDroppedValue);
    }
    const normalized: Record<string, Jsonable> = {};
    for (const [k, v] of Object.entries(value)) {
      normalized[k] = normalizeDroppedValue(v);
    }
    return normalized;
  }
  try {
    return String(value);
    /* v8 ignore next 3 - defensive: String() very rarely throws */
  } catch {
    return `<${typeof value}>`;
  }
}

/**
 * Split params into supported attributes and dropped params.
 */
function paramsAsMapping(
  params: Params,
): [
  Record<string, string | number | boolean | string[]>,
  Record<string, Jsonable>,
] {
  const supported: Record<string, string | number | boolean | string[]> = {};
  const dropped: Record<string, Jsonable> = {};

  for (const [key, value] of Object.entries(params)) {
    if (isSupportedParamValue(value)) {
      if (value !== null && value !== undefined) {
        supported[key] = value;
      }
    } else {
      dropped[key] = normalizeDroppedValue(value);
    }
  }

  return [supported, dropped];
}

/**
 * Apply model parameters as span attributes.
 */
function applyParamAttributes(
  attrs: Record<string, unknown>,
  params: Record<string, string | number | boolean | string[]>,
): void {
  for (const [key, attrKey] of Object.entries(PARAM_ATTRIBUTE_MAP)) {
    if (!(key in params)) {
      continue;
    }
    const value = params[key];
    /* v8 ignore next 3 - defensive: undefined values filtered upstream */
    if (value === undefined) {
      continue;
    }
    // Normalize stop to array if it's a string
    if (
      (key === "stop" || key === "stopSequences" || key === "stop_sequences") &&
      typeof value === "string"
    ) {
      attrs[attrKey] = [value];
    } else {
      attrs[attrKey] = value;
    }
  }
}

/**
 * Convert a Message to a GenAI message format.
 */
function messageToGenAI(message: Message): {
  role: string;
  content: string | object[];
} {
  const role = message.role;

  // For simple text content
  if (typeof message.content === "string") {
    return { role, content: message.content };
  }

  // For array content
  if (Array.isArray(message.content)) {
    const parts: object[] = [];
    for (const part of message.content) {
      if (typeof part === "string") {
        parts.push({ type: "text", text: part });
      } else if ("type" in part) {
        if (part.type === "text") {
          parts.push({ type: "text", text: part.text });
        } else if (part.type === "image") {
          parts.push({ type: "image", source: "...(omitted)" });
        } else if (part.type === "tool_call") {
          parts.push({
            type: "tool_use",
            id: part.id,
            name: part.name,
            args: part.args,
          });
        } else if (part.type === "tool_result") {
          parts.push({
            type: "tool_result",
            id: part.id,
            result: part.result,
          });
        } else {
          parts.push(part as object);
        }
      }
    }
    return { role, content: parts };
  }

  return { role, content: String(message.content) };
}

/**
 * Split request messages into system instructions and input messages.
 */
function splitRequestMessages(
  messages: readonly Message[],
): [object[], object[]] {
  const systemInstructions: object[] = [];
  const inputMessages: object[] = [];

  for (const message of messages) {
    const genAIMessage = messageToGenAI(message);
    if (message.role === "system") {
      systemInstructions.push(genAIMessage);
    } else {
      inputMessages.push(genAIMessage);
    }
  }

  return [systemInstructions, inputMessages];
}

/**
 * Check if a value is a BaseToolkit.
 */
function isToolkit(
  tools: Tools | BaseToolkit | undefined | null,
): tools is BaseToolkit {
  return (
    tools !== null &&
    tools !== undefined &&
    typeof tools === "object" &&
    "tools" in tools &&
    Array.isArray((tools as BaseToolkit).tools)
  );
}

/**
 * Serialize tools for GenAI attributes.
 */
function serializeTools(
  tools: Tools | BaseToolkit | undefined | null,
): string | null {
  if (!tools) {
    return null;
  }

  // If it's a Toolkit, get the tools array
  const toolArray: readonly (BaseTool | ProviderTool)[] = isToolkit(tools)
    ? tools.tools
    : tools;

  if (!toolArray || toolArray.length === 0) {
    return null;
  }

  // Extract tool schemas
  const schemas = toolArray.map((tool: BaseTool | ProviderTool) => {
    if ("__schema" in tool && tool.__schema) {
      return tool.__schema;
    }
    if ("name" in tool) {
      return {
        name: (tool as { name: string }).name,
        description: (tool as { description?: string }).description,
      };
    }
    return tool;
  });

  return jsonStringify(schemas);
}

/**
 * Map FinishReason to GenAI finish reason string.
 */
function mapFinishReason(reason: string | null): string {
  if (!reason) {
    return "stop"; // Normal completion
  }
  // Map known finish reasons to GenAI semantic conventions
  switch (reason) {
    case "max_tokens":
    case "length":
      return "length";
    case "refusal":
    case "content_filter":
      return "content_filter";
    case "context_length_exceeded":
      return "length";
    default:
      return reason;
  }
}

/**
 * Build GenAI request attributes for a span.
 */
function buildRequestAttributes(options: {
  operation: string;
  providerId: ProviderId;
  modelId: ModelId;
  messages: readonly Message[];
  tools: Tools | BaseToolkit | undefined | null;
  format: Format | undefined | null;
  params: Record<string, string | number | boolean | string[]>;
}): Record<string, unknown> {
  const { operation, providerId, modelId, messages, tools, format, params } =
    options;

  const attrs: Record<string, unknown> = {
    [GenAIAttributes.OPERATION_NAME]: operation,
    [GenAIAttributes.PROVIDER_NAME]: providerId,
    [GenAIAttributes.REQUEST_MODEL]: modelId,
    [GenAIAttributes.OUTPUT_TYPE]: inferOutputType(format),
  };

  // Apply parameter attributes
  applyParamAttributes(attrs, params);

  // Split and assign message attributes
  const [systemInstructions, inputMessages] = splitRequestMessages(messages);
  if (systemInstructions.length > 0) {
    attrs[GenAIAttributes.SYSTEM_INSTRUCTIONS] =
      jsonStringify(systemInstructions);
  }
  if (inputMessages.length > 0) {
    attrs[GenAIAttributes.INPUT_MESSAGES] = jsonStringify(inputMessages);
  }

  // Serialize tools
  const toolPayload = serializeTools(tools);
  if (toolPayload) {
    attrs[GenAIAttributes.TOOL_DEFINITIONS] = toolPayload;
  }

  return attrs;
}

/**
 * Extract response ID from raw response data.
 */
function extractResponseId(raw: unknown): string | null {
  if (typeof raw === "object" && raw !== null) {
    const obj = raw as Record<string, unknown>;
    for (const key of ["id", "response_id", "responseId"]) {
      const value = obj[key];
      if (typeof value === "string") {
        return value;
      }
    }
  }
  return null;
}

/**
 * Attach response attributes to a GenAI span.
 */
export function attachResponse(
  span: OtelSpan,
  response: RootResponse,
  requestMessages: readonly Message[],
): void {
  // Response model
  span.setAttribute(GenAIAttributes.RESPONSE_MODEL, response.modelId);

  // Finish reason
  span.setAttribute(GenAIAttributes.RESPONSE_FINISH_REASONS, [
    mapFinishReason(response.finishReason),
  ]);

  // Response ID if available
  const responseId = extractResponseId(response.raw);
  if (responseId) {
    span.setAttribute(GenAIAttributes.RESPONSE_ID, responseId);
  }

  // Output messages - extract from response
  const outputMessages: object[] = [];
  if ("messages" in response && Array.isArray(response.messages)) {
    // Get assistant message (last message)
    const messages = response.messages as readonly Message[];
    const assistantMessage = messages[messages.length - 1];
    if (assistantMessage && assistantMessage.role === "assistant") {
      outputMessages.push(messageToGenAI(assistantMessage));
    }
  }
  if (outputMessages.length > 0) {
    span.setAttribute(
      GenAIAttributes.OUTPUT_MESSAGES,
      jsonStringify(outputMessages),
    );
  }

  // Usage attributes
  if (response.usage) {
    span.setAttribute(
      GenAIAttributes.USAGE_INPUT_TOKENS,
      response.usage.inputTokens,
    );
    span.setAttribute(
      GenAIAttributes.USAGE_OUTPUT_TOKENS,
      response.usage.outputTokens,
    );
  }

  // Mirascope-specific attributes
  span.setAttribute(
    "mirascope.response.messages",
    jsonStringify(
      requestMessages.map((m) => ({ role: m.role, content: m.content })),
    ),
  );

  if ("content" in response) {
    span.setAttribute(
      "mirascope.response.content",
      jsonStringify(response.content),
    );
  }

  if (response.usage) {
    span.setAttribute(
      "mirascope.response.usage",
      jsonStringify({
        inputTokens: response.usage.inputTokens,
        outputTokens: response.usage.outputTokens,
        cacheReadTokens: response.usage.cacheReadTokens,
        cacheWriteTokens: response.usage.cacheWriteTokens,
        reasoningTokens: response.usage.reasoningTokens,
      }),
    );
  }
}

/**
 * Record dropped parameters as an event on the span.
 */
export function recordDroppedParams(
  span: OtelSpan,
  droppedParams: Record<string, Jsonable>,
): void {
  if (Object.keys(droppedParams).length === 0) {
    return;
  }

  span.addEvent("gen_ai.request.params.untracked", {
    "gen_ai.untracked_params.count": Object.keys(droppedParams).length,
    "gen_ai.untracked_params.keys": Object.keys(droppedParams),
    "gen_ai.untracked_params.json": jsonStringify(droppedParams),
  });
}

/**
 * Options for starting a model span.
 */
export interface StartModelSpanOptions {
  modelId: ModelId;
  providerId: ProviderId;
  messages: readonly Message[];
  tools?: Tools | BaseToolkit | null;
  format?: Format | null;
  params: Params;
  /** Whether to activate the span as current context (default: true) */
  activate?: boolean;
}

/**
 * Start a GenAI span for a model call.
 *
 * Returns a SpanContext with the span and any dropped parameters.
 * The caller is responsible for ending the span.
 *
 * @example
 * ```typescript
 * const spanCtx = startModelSpan({
 *   modelId: 'anthropic/claude-sonnet-4-20250514',
 *   providerId: 'anthropic',
 *   messages,
 *   tools,
 *   format,
 *   params: model.params,
 * });
 *
 * try {
 *   const response = await originalCall(...);
 *   if (spanCtx.span) {
 *     attachResponse(spanCtx.span, response, messages);
 *   }
 *   return response;
 * } catch (error) {
 *   if (spanCtx.span) {
 *     recordException(spanCtx.span, error);
 *   }
 *   throw error;
 * } finally {
 *   spanCtx.span?.end();
 * }
 * ```
 */
export function startModelSpan(options: StartModelSpanOptions): SpanContext {
  const {
    modelId,
    providerId,
    messages,
    tools,
    format,
    params,
    activate = true,
  } = options;

  const [supportedParams, droppedParams] = paramsAsMapping(params);
  const tracer = getTracer();

  if (!tracer) {
    return { span: null, droppedParams };
  }

  const operation = "chat";
  const attrs = buildRequestAttributes({
    operation,
    providerId,
    modelId,
    messages,
    tools,
    format,
    params: supportedParams,
  });

  const spanName = `${operation} ${modelId}`;

  const span = tracer.startSpan(
    spanName,
    {
      kind: SpanKind.CLIENT,
    },
    activate ? otelContext.active() : undefined,
  );

  // Set attributes
  for (const [key, value] of Object.entries(attrs)) {
    if (value !== undefined && value !== null) {
      span.setAttribute(
        key,
        value as string | number | boolean | string[] | number[],
      );
    }
  }

  return { span, droppedParams };
}

/**
 * Execute a function within an OpenTelemetry span context.
 *
 * This ensures child spans are properly linked to the parent span.
 */
export async function withSpanContext<T>(
  span: OtelSpan | null,
  fn: () => Promise<T>,
): Promise<T> {
  if (!span) {
    return fn();
  }

  return otelContext.with(trace.setSpan(otelContext.active(), span), fn);
}
