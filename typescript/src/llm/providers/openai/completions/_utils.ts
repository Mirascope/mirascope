/**
 * OpenAI Completions API utilities for encoding requests and decoding responses.
 */

import type {
  ChatCompletion,
  ChatCompletionAssistantMessageParam,
  ChatCompletionContentPart,
  ChatCompletionContentPartImage,
  ChatCompletionContentPartInputAudio,
  ChatCompletionContentPartText,
  ChatCompletionCreateParamsNonStreaming,
  ChatCompletionMessageParam,
  ChatCompletionToolMessageParam,
} from "openai/resources/chat/completions";

import type {
  AssistantContentPart,
  Audio,
  AudioMimeType,
  Document,
  Image,
  Text,
  ToolCall,
} from "@/llm/content";
import type { Format } from "@/llm/formatting";
import type { AssistantMessage, Message } from "@/llm/messages";
import type { Params } from "@/llm/models";
import type { CompletionsModelFeatureInfo } from "@/llm/providers/openai/completions/_utils/feature-info";
import type { OpenAIModelId } from "@/llm/providers/openai/model-id";
import type { Usage } from "@/llm/responses/usage";
import type { ToolSchema, Tools } from "@/llm/tools";

import { FeatureNotSupportedError } from "@/llm/exceptions";
import { ParamHandler } from "@/llm/providers/base";
import { modelName } from "@/llm/providers/openai/model-id";
import { FinishReason } from "@/llm/responses/finish-reason";
import { createUsage } from "@/llm/responses/usage";
import { isProviderTool } from "@/llm/tools";

// ============================================================================
// Content Part Encoding
// ============================================================================

/**
 * Content part types for user messages.
 */
type UserContentPartOpenAI =
  | ChatCompletionContentPartText
  | ChatCompletionContentPartImage
  | ChatCompletionContentPartInputAudio
  | ChatCompletionContentPart.File;

/**
 * Encode an Image content part to OpenAI's format.
 * OpenAI accepts either a URL or a base64 data URI.
 */
function encodeImage(image: Image): ChatCompletionContentPartImage {
  let url: string;
  if (image.source.type === "url_image_source") {
    url = image.source.url;
  } else {
    url = `data:${image.source.mimeType};base64,${image.source.data}`;
  }
  return {
    type: "image_url",
    image_url: { url, detail: "auto" },
  };
}

/**
 * OpenAI-supported audio formats for input.
 */
type OpenAIAudioFormat = "wav" | "mp3";

/**
 * Extract the audio format from a MIME type.
 *
 * @throws FeatureNotSupportedError if the format is not supported by OpenAI
 */
function toOpenAIAudioFormat(mimeType: AudioMimeType): OpenAIAudioFormat {
  const format = mimeType.split("/")[1];
  if (format === "wav" || format === "mp3") {
    return format;
  }
  throw new FeatureNotSupportedError(
    `audio format: ${mimeType}`,
    "openai",
    null,
    `OpenAI only supports 'wav' and 'mp3' audio formats, got '${format}'.`,
  );
}

/**
 * Encode an Audio content part to OpenAI's format.
 *
 * @throws FeatureNotSupportedError if the model doesn't support audio or format is unsupported
 */
function encodeAudio(
  audio: Audio,
  modelId: OpenAIModelId | undefined,
  featureInfo?: CompletionsModelFeatureInfo,
): ChatCompletionContentPartInputAudio {
  // Check if model supports audio using feature info
  if (featureInfo?.audioSupport === false) {
    throw new FeatureNotSupportedError(
      "audio input",
      "openai",
      modelId ?? null,
      `Model '${modelId}' does not support audio inputs.`,
    );
  }

  const format = toOpenAIAudioFormat(audio.source.mimeType);
  return {
    type: "input_audio",
    input_audio: {
      data: audio.source.data,
      format,
    },
  };
}

/**
 * Encode a Document content part to OpenAI Completions API format.
 *
 * @throws FeatureNotSupportedError if the document uses a URL source
 */
function encodeDocument(doc: Document): ChatCompletionContentPart.File {
  const { source } = doc;
  switch (source.type) {
    case "base64_document_source":
      return {
        type: "file",
        file: {
          file_data: `data:${source.mediaType};base64,${source.data}`,
          filename: "document.pdf",
        },
      };
    case "text_document_source":
      return {
        type: "file",
        file: {
          file_data: `data:${source.mediaType};base64,${btoa(source.data)}`,
          filename: "document.txt",
        },
      };
    case "url_document_source":
      throw new FeatureNotSupportedError(
        "url_document_source",
        "openai:completions",
        null,
        "OpenAI Completions API does not support URL-referenced documents. Use `Document.fromFile(...)` or `Document.fromBytes(...)` instead.",
      );
  }
}

// ============================================================================
// Tool Encoding
// ============================================================================

/* v8 ignore start - tool encoding will be tested via e2e */
/**
 * Convert a ToolSchema to OpenAI's ChatCompletionTool format.
 */
export function encodeToolSchema(
  tool: ToolSchema,
): ChatCompletionCreateParamsNonStreaming["tools"] extends
  | (infer T)[]
  | undefined
  ? T
  : never {
  return {
    type: "function",
    function: {
      name: tool.name,
      description: tool.description,
      parameters: {
        type: "object",
        properties: tool.parameters.properties,
        required: tool.parameters.required,
      },
      strict: tool.strict,
    },
  };
}

/**
 * Encode an array of tool schemas to OpenAI's format.
 */
export function encodeTools(
  tools: readonly ToolSchema[],
): NonNullable<ChatCompletionCreateParamsNonStreaming["tools"]> {
  return tools.map(encodeToolSchema);
}
/* v8 ignore stop */

// ============================================================================
// Message Encoding
// ============================================================================

/**
 * Encode Mirascope messages to OpenAI Chat Completions API format.
 *
 * @param messages - The messages to encode
 * @param encodeThoughtsAsText - Whether to encode thoughts as text in assistant messages
 * @param modelId - The model ID (used for checking audio support and raw message reuse)
 * @param featureInfo - Feature info for the model (used for capability checks)
 */
export function encodeMessages(
  messages: readonly Message[],
  encodeThoughtsAsText: boolean = false,
  modelId?: OpenAIModelId,
  featureInfo?: CompletionsModelFeatureInfo,
): ChatCompletionMessageParam[] {
  const openaiMessages: ChatCompletionMessageParam[] = [];
  const expectedProviderModelName = modelId
    ? modelName(modelId, "completions")
    : null;

  for (const message of messages) {
    if (message.role === "system") {
      openaiMessages.push({
        role: "system",
        content: message.content.text,
      });
    } else if (message.role === "user") {
      /* v8 ignore start - tool encoding will be tested via e2e */
      // First add any tool output messages (OpenAI uses separate "tool" role)
      const toolMessages = encodeToolOutputs(message);
      openaiMessages.push(...toolMessages);
      /* v8 ignore stop */

      // Then add the user message if it has non-tool content
      const userMessage = encodeUserMessage(message, modelId, featureInfo);
      if (userMessage) {
        openaiMessages.push(userMessage);
      }
    } else if (message.role === "assistant") {
      // Check if we can reuse the raw message (from same provider/model)
      if (
        message.providerId === "openai" &&
        expectedProviderModelName &&
        message.providerModelName === expectedProviderModelName &&
        message.rawMessage &&
        typeof message.rawMessage === "object" &&
        "role" in message.rawMessage &&
        !encodeThoughtsAsText
      ) {
        // Reuse the serialized message directly
        openaiMessages.push(
          message.rawMessage as unknown as ChatCompletionAssistantMessageParam,
        );
      } else {
        // Otherwise, encode from content parts
        openaiMessages.push(
          encodeAssistantMessage(message, encodeThoughtsAsText),
        );
      }
    }
  }

  return openaiMessages;
}

/**
 * Encode a Mirascope user message to OpenAI format.
 *
 * Iterates over content parts and builds the appropriate content structure.
 * Single text part is simplified to string, multiple parts become an array.
 * Returns null if the message only contains tool outputs (which are handled separately).
 */
function encodeUserMessage(
  message: Extract<Message, { role: "user" }>,
  modelId?: OpenAIModelId,
  featureInfo?: CompletionsModelFeatureInfo,
): ChatCompletionMessageParam | null {
  const contentParts: UserContentPartOpenAI[] = [];

  for (const part of message.content) {
    switch (part.type) {
      case "text":
        contentParts.push({ type: "text", text: part.text });
        break;

      case "image":
        contentParts.push(encodeImage(part));
        break;

      case "audio":
        contentParts.push(encodeAudio(part, modelId, featureInfo));
        break;

      case "document":
        contentParts.push(encodeDocument(part));
        break;

      /* v8 ignore start - tool encoding will be tested via e2e */
      case "tool_output":
        // tool_output is handled separately in encodeMessages
        // by creating tool role messages
        break;
      /* v8 ignore stop */
    }
  }

  /* v8 ignore start - tool encoding will be tested via e2e */
  // If no content parts (only tool_outputs), return null
  if (contentParts.length === 0) {
    return null;
  }
  /* v8 ignore stop */

  // Simplify to string if only a single text part
  let content: string | UserContentPartOpenAI[] = contentParts;
  if (contentParts.length === 1 && contentParts[0]?.type === "text") {
    content = contentParts[0].text;
  }

  return {
    role: "user",
    content,
    ...(message.name && { name: message.name }),
  };
}

/* v8 ignore start - tool encoding will be tested via e2e */
/**
 * Extract tool outputs from a user message and encode as tool role messages.
 */
function encodeToolOutputs(
  message: Extract<Message, { role: "user" }>,
): ChatCompletionToolMessageParam[] {
  const toolMessages: ChatCompletionToolMessageParam[] = [];

  for (const part of message.content) {
    if (part.type === "tool_output") {
      toolMessages.push({
        role: "tool",
        tool_call_id: part.id,
        content:
          typeof part.result === "string"
            ? part.result
            : JSON.stringify(part.result),
      });
    }
  }

  return toolMessages;
}
/* v8 ignore stop */

/**
 * Encode a Mirascope assistant message to OpenAI format.
 *
 * Iterates over content parts and builds text content.
 * Single text part is simplified to string, multiple parts become an array.
 * Tool calls are encoded as a separate array on the message.
 */
function encodeAssistantMessage(
  message: AssistantMessage,
  encodeThoughtsAsText: boolean,
): ChatCompletionAssistantMessageParam {
  const textParts: ChatCompletionContentPartText[] = [];
  const toolCalls: ChatCompletionAssistantMessageParam["tool_calls"] = [];

  for (const part of message.content) {
    switch (part.type) {
      case "text":
        textParts.push({ type: "text", text: part.text });
        break;

      case "thought":
        // Encode thoughts as text when requested, otherwise drop
        if (encodeThoughtsAsText) {
          textParts.push({
            type: "text",
            text: "**Thinking:** " + part.thought,
          });
        }
        break;

      /* v8 ignore start - tool encoding will be tested via e2e */
      case "tool_call": {
        toolCalls.push({
          id: part.id,
          type: "function",
          function: {
            name: part.name,
            arguments: part.args,
          },
        });
        break;
      }
      /* v8 ignore stop */
    }
  }

  // Simplify to string if single text part, otherwise keep as list
  // Empty content becomes null
  let content: string | ChatCompletionContentPartText[] | null = null;
  if (textParts.length === 1) {
    content = textParts[0]!.text;
  } else if (textParts.length > 1) {
    content = textParts;
  }

  const result: ChatCompletionAssistantMessageParam = {
    role: "assistant",
    content,
    ...(message.name && { name: message.name }),
  };

  /* v8 ignore start - tool encoding will be tested via e2e */
  if (toolCalls.length > 0) {
    result.tool_calls = toolCalls;
  }
  /* v8 ignore stop */

  return result;
}

/**
 * Build the request parameters for the OpenAI Chat Completions API.
 *
 * This function performs strict param checking - any unhandled params will
 * cause an error to ensure we don't silently ignore user configuration.
 *
 * @param modelId - The model ID to use
 * @param messages - The messages to send
 * @param tools - Optional tools to make available to the model
 * @param format - Optional format for structured output
 * @param params - Optional parameters (temperature, maxTokens, etc.)
 * @param featureInfo - Optional feature info for model capability detection
 */
export function buildRequestParams(
  modelId: OpenAIModelId,
  messages: readonly Message[],
  tools?: Tools,
  format?: Format | null,
  params: Params = {},
  featureInfo?: CompletionsModelFeatureInfo,
): ChatCompletionCreateParamsNonStreaming {
  return ParamHandler.with(params, "openai", modelId, (p) => {
    const thinkingConfig = p.get("thinking");
    const encodeThoughtsAsText = thinkingConfig?.encodeThoughtsAsText ?? false;

    // Determine if this is a reasoning model (skip temperature/topP/stop)
    const isReasoningModel = featureInfo?.isReasoningModel === true;

    const openaiMessages = encodeMessages(
      messages,
      encodeThoughtsAsText,
      modelId,
      featureInfo,
    );

    const requestParams: ChatCompletionCreateParamsNonStreaming = {
      model: modelName(modelId, null),
      messages: openaiMessages,
    };

    // Collect all tools (explicit tools + format tool)
    const allEncodedTools: ChatCompletionCreateParamsNonStreaming["tools"] = [];

    /* v8 ignore start - tool encoding will be tested via e2e */
    if (tools !== undefined && tools.length > 0) {
      // Filter out provider tools (not supported by Completions API)
      const regularTools: ToolSchema[] = [];
      for (const tool of tools) {
        if (isProviderTool(tool)) {
          throw new FeatureNotSupportedError(
            `Provider tool ${tool.name}`,
            "openai:completions",
            modelId,
            `Provider tool '${tool.name}' is not supported by OpenAI Completions API. Try using the Responses API instead (append ':responses' to your model ID).`,
          );
        }
        regularTools.push(tool);
      }
      if (regularTools.length > 0) {
        allEncodedTools.push(...encodeTools(regularTools));
      }
    }

    // Handle format-based tool and instructions
    if (format) {
      if (format.mode === "tool") {
        const formatToolSchema = format.createToolSchema();
        allEncodedTools.push(encodeToolSchema(formatToolSchema));

        // Set tool_choice to force the format tool
        if (tools && tools.length > 0) {
          // When we have other tools, use 'required' to require a tool call
          requestParams.tool_choice = "required";
        } else {
          // When only format tool, force that specific tool
          requestParams.tool_choice = {
            type: "function",
            function: { name: formatToolSchema.name },
          };
        }
      }

      // Add formatting instructions as a system message
      if (format.formattingInstructions) {
        openaiMessages.unshift({
          role: "system",
          content: format.formattingInstructions,
        });
      }
    }

    if (allEncodedTools.length > 0) {
      requestParams.tools = allEncodedTools;
    }
    /* v8 ignore stop */

    const maxTokens = p.get("maxTokens");
    if (maxTokens !== undefined) {
      // max_completion_tokens is the preferred parameter (max_tokens is deprecated)
      requestParams.max_completion_tokens = maxTokens;
    }

    const temperature = p.get("temperature");
    if (temperature !== undefined) {
      if (isReasoningModel) {
        p.warnUnsupported(
          "temperature",
          "Reasoning models do not support the temperature parameter",
        );
      } else {
        requestParams.temperature = temperature;
      }
    }

    const topP = p.get("topP");
    if (topP !== undefined) {
      if (isReasoningModel) {
        p.warnUnsupported(
          "topP",
          "Reasoning models do not support the top_p parameter",
        );
      } else {
        requestParams.top_p = topP;
      }
    }

    const seed = p.get("seed");
    if (seed !== undefined) {
      requestParams.seed = seed;
    }

    const stopSequences = p.get("stopSequences");
    if (stopSequences !== undefined) {
      if (isReasoningModel) {
        p.warnUnsupported(
          "stopSequences",
          "Reasoning models do not support stop sequences",
        );
      } else {
        requestParams.stop = stopSequences;
      }
    }

    // OpenAI doesn't support topK
    p.warnUnsupported("topK", "OpenAI does not support the top_k parameter");

    return requestParams;
  });
}

/**
 * Serialize a message object for storage in rawMessage.
 *
 * This mirrors Python's `message.model_dump(exclude_none=True)` pattern.
 */
function serializeMessage(
  message: ChatCompletion.Choice["message"],
): Record<string, unknown> {
  const serialized: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(message)) {
    if (value !== undefined && value !== null) {
      serialized[key] = value;
    }
  }
  return serialized;
}

/**
 * Decode OpenAI Chat Completions response to Mirascope types.
 */
export function decodeResponse(
  response: ChatCompletion,
  modelId: OpenAIModelId,
): {
  assistantMessage: AssistantMessage;
  finishReason: FinishReason | null;
  usage: Usage | null;
} {
  const choice = response.choices[0];
  /* v8 ignore start - defensive check for empty choices */
  if (!choice) {
    throw new Error("No choices in response");
  }
  /* v8 ignore stop */

  const content = decodeContent(choice.message);

  // Store serialized message for round-tripping in resume operations.
  // This format matches what OpenAI expects as ChatCompletionAssistantMessageParam.
  const serializedRawMessage = serializeMessage(choice.message);

  const assistantMessage: AssistantMessage = {
    role: "assistant",
    content,
    name: null,
    providerId: "openai",
    modelId,
    providerModelName: modelName(modelId, "completions"),
    rawMessage:
      serializedRawMessage as unknown as AssistantMessage["rawMessage"],
  };

  const finishReason = decodeFinishReason(choice.finish_reason);

  /* v8 ignore next - usage is always present in API responses */
  const usage = response.usage ? decodeUsage(response.usage) : null;

  return { assistantMessage, finishReason, usage };
}

function decodeContent(
  message: ChatCompletion.Choice["message"],
): AssistantContentPart[] {
  const parts: AssistantContentPart[] = [];

  // Handle text content
  if (message.content) {
    const text: Text = { type: "text", text: message.content };
    parts.push(text);
  }

  // Handle refusal as text (OpenAI returns refusal as separate field)
  /* v8 ignore start - refusals are difficult to trigger reliably */
  if (message.refusal) {
    const text: Text = { type: "text", text: message.refusal };
    parts.push(text);
  }
  /* v8 ignore end */

  /* v8 ignore start - tool decoding will be tested via e2e */
  // Handle tool calls
  if (message.tool_calls && message.tool_calls.length > 0) {
    for (const tc of message.tool_calls) {
      // Only handle function type tool calls
      if (tc.type === "function") {
        const toolCall: ToolCall = {
          type: "tool_call",
          id: tc.id,
          name: tc.function.name,
          args: tc.function.arguments,
        };
        parts.push(toolCall);
      }
    }
  }
  /* v8 ignore stop */

  return parts;
}

function decodeFinishReason(
  finishReason: ChatCompletion.Choice["finish_reason"],
): FinishReason | null {
  switch (finishReason) {
    case "length":
      return FinishReason.MAX_TOKENS;
    /* v8 ignore start - refusals are difficult to trigger reliably */
    case "content_filter":
      return FinishReason.REFUSAL;
    /* v8 ignore end */
    case "stop":
    case "tool_calls":
    case "function_call":
      return null; // Normal completion
    /* v8 ignore next 2 - defensive default case */
    default:
      return null;
  }
}

function decodeUsage(usage: NonNullable<ChatCompletion["usage"]>): Usage {
  return createUsage({
    inputTokens: usage.prompt_tokens,
    outputTokens: usage.completion_tokens,
    cacheReadTokens: usage.prompt_tokens_details?.cached_tokens ?? 0,
    reasoningTokens: usage.completion_tokens_details?.reasoning_tokens ?? 0,
    raw: usage,
  });
}
