/**
 * OpenAI Responses API utilities for encoding requests and decoding responses.
 */

import type OpenAI from 'openai';
import type {
  Response as OpenAIResponse,
  ResponseCreateParamsNonStreaming,
  FunctionTool,
  ResponseFunctionToolCall,
  ResponseInputContent,
  ResponseInputImage,
  ResponseInputItem,
  ResponseOutputItem,
} from 'openai/resources/responses/responses';
import type { Reasoning, ReasoningEffort } from 'openai/resources/shared';

import type {
  AssistantContentPart,
  Image,
  Text,
  Thought,
  ToolCall,
} from '@/llm/content';
import type { ToolSchema } from '@/llm/tools';
import { FeatureNotSupportedError } from '@/llm/exceptions';
import type { AssistantMessage, Message } from '@/llm/messages';
import type { Params } from '@/llm/models';
import type { ThinkingLevel } from '@/llm/models/thinking-config';
import { ParamHandler } from '@/llm/providers/base';
import type { OpenAIModelId } from '@/llm/providers/openai/model-id';
import { modelName } from '@/llm/providers/openai/model-id';
import { FinishReason } from '@/llm/responses/finish-reason';
import type { Usage } from '@/llm/responses/usage';
import { createUsage } from '@/llm/responses/usage';

/**
 * Maps ThinkingLevel to OpenAI ReasoningEffort.
 */
const THINKING_LEVEL_TO_EFFORT: Record<ThinkingLevel, ReasoningEffort> = {
  default: 'medium',
  none: 'none',
  minimal: 'minimal',
  low: 'low',
  medium: 'medium',
  high: 'high',
  max: 'xhigh',
};

/**
 * Compute OpenAI Reasoning config from ThinkingConfig.
 *
 * @param level - The thinking level
 * @param includeThoughts - Whether to include reasoning summary
 * @returns OpenAI Reasoning configuration
 */
export function computeReasoning(
  level: ThinkingLevel,
  includeThoughts: boolean
): Reasoning {
  const reasoning: Reasoning = {
    /* v8 ignore next - all ThinkingLevel values are covered in the map */
    effort: THINKING_LEVEL_TO_EFFORT[level] ?? 'medium',
  };

  if (includeThoughts) {
    reasoning.summary = 'auto';
  }

  return reasoning;
}

/**
 * Simple message type for easy input (user, assistant, developer roles).
 */
type EasyInputMessage = OpenAI.Responses.EasyInputMessage;

// ============================================================================
// Content Part Encoding
// ============================================================================

/**
 * Encode an Image to the Responses API format.
 */
function encodeImage(image: Image): ResponseInputImage {
  let imageUrl: string;
  if (image.source.type === 'url_image_source') {
    imageUrl = image.source.url;
  } else {
    imageUrl = `data:${image.source.mimeType};base64,${image.source.data}`;
  }
  return { type: 'input_image', image_url: imageUrl, detail: 'auto' };
}

// ============================================================================
// Tool Encoding
// ============================================================================

/* v8 ignore start - tool encoding will be tested via e2e */
/**
 * Encode a tool schema to OpenAI Responses API tool format.
 */
export function encodeToolSchema(tool: ToolSchema): FunctionTool {
  return {
    type: 'function',
    name: tool.name,
    description: tool.description,
    parameters: {
      type: 'object',
      properties: tool.parameters.properties as Record<string, unknown>,
      required: tool.parameters.required as string[] | undefined,
    },
    strict: tool.strict ?? null,
  };
}

/**
 * Encode multiple tool schemas for OpenAI Responses API.
 */
export function encodeTools(tools: readonly ToolSchema[]): FunctionTool[] {
  return tools.map(encodeToolSchema);
}
/* v8 ignore stop */

// ============================================================================
// Message Encoding
// ============================================================================

/**
 * Encode Mirascope messages to OpenAI Responses API format.
 *
 * Key differences from Completions API:
 * - System messages use role: 'developer' (not 'system')
 * - Uses EasyInputMessageParam for simple message format
 * - Returns flat array of input items (not nested messages)
 * - Assistant messages with multiple text parts are encoded as separate messages
 * - Tool outputs are encoded as function_call_output items
 *
 * @param messages - The messages to encode
 * @param modelId - The model ID for the request (used to check if raw message can be reused)
 * @param encodeThoughtsAsText - Whether to encode thoughts as text in assistant messages
 */
export function encodeMessages(
  messages: readonly Message[],
  modelId: OpenAIModelId,
  encodeThoughtsAsText: boolean = false
): ResponseInputItem[] {
  const inputItems: ResponseInputItem[] = [];
  const expectedProviderModelName = modelName(modelId, 'responses');

  for (const message of messages) {
    if (message.role === 'system') {
      inputItems.push({
        role: 'developer',
        content: message.content.text,
      });
    } else if (message.role === 'user') {
      // Check for tool outputs first
      const toolOutputs = encodeToolOutputs(message);
      /* v8 ignore start - tool encoding will be tested via e2e */
      if (toolOutputs.length > 0) {
        inputItems.push(...toolOutputs);
      }
      /* v8 ignore stop */
      // Then encode any non-tool content as a user message
      const userMessage = encodeUserMessage(message);
      if (userMessage !== null) {
        inputItems.push(userMessage);
      }
    } else if (message.role === 'assistant') {
      // Check if we can reuse the raw message (from same provider/model)
      // Array check is needed because we spread into inputItems
      if (
        (message.providerId === 'openai' ||
          message.providerId === 'openai:responses') &&
        message.providerModelName === expectedProviderModelName &&
        message.rawMessage &&
        Array.isArray(message.rawMessage) &&
        !encodeThoughtsAsText
      ) {
        // Reuse serialized output items directly
        inputItems.push(
          ...(message.rawMessage as unknown as ResponseInputItem[])
        );
      } else {
        // Otherwise, encode from content parts
        inputItems.push(
          ...encodeAssistantMessage(message, encodeThoughtsAsText)
        );
      }
    }
  }

  return inputItems;
}

/* v8 ignore start - tool encoding will be tested via e2e */
/**
 * Encode tool outputs from a user message to function_call_output items.
 */
function encodeToolOutputs(
  message: Extract<Message, { role: 'user' }>
): ResponseInputItem.FunctionCallOutput[] {
  const outputs: ResponseInputItem.FunctionCallOutput[] = [];

  for (const part of message.content) {
    if (part.type === 'tool_output') {
      outputs.push({
        type: 'function_call_output',
        call_id: part.id,
        output:
          typeof part.result === 'string'
            ? part.result
            : JSON.stringify(part.result),
      });
    }
  }

  return outputs;
}
/* v8 ignore stop */

/**
 * Encode a Mirascope user message to OpenAI Responses API format.
 *
 * - Single text part: string content (simplified)
 * - Multiple parts or non-text content: array of content items
 * - Returns null if message contains only tool outputs (handled separately)
 */
function encodeUserMessage(
  message: Extract<Message, { role: 'user' }>
): EasyInputMessage | null {
  const contentItems: ResponseInputContent[] = [];

  for (const part of message.content) {
    switch (part.type) {
      case 'text':
        contentItems.push({ type: 'input_text', text: part.text });
        break;

      case 'image':
        contentItems.push(encodeImage(part));
        break;

      case 'audio':
        throw new FeatureNotSupportedError(
          'audio input',
          'openai',
          null,
          'OpenAI Responses API does not support audio inputs. Try appending ":completions" to your model ID instead.'
        );

      /* v8 ignore start - content types not yet fully implemented */
      case 'document':
        throw new FeatureNotSupportedError(
          'document content encoding',
          'openai',
          null,
          'Document content is not yet implemented'
        );

      case 'tool_output':
        // Tool outputs in Responses API are handled separately as function_call_output items
        // Skip here - they're processed in encodeMessages
        break;
      /* v8 ignore stop */
    }
  }

  // No content (only tool outputs) - return null
  /* v8 ignore start - tool encoding will be tested via e2e */
  if (contentItems.length === 0) {
    return null;
  }
  /* v8 ignore stop */

  // Single text part: simplify to string
  if (contentItems.length === 1 && contentItems[0]?.type === 'input_text') {
    return {
      role: 'user',
      content: contentItems[0].text,
    };
  }

  // Multiple parts or non-text content: use array format
  return {
    role: 'user',
    content: contentItems,
  };
}

/**
 * Encode a Mirascope assistant message to OpenAI Responses API format.
 *
 * Note: OpenAI does not provide any way to encode multiple pieces of assistant-generated
 * text as adjacent content within the same Message. Rather than generating fake fields,
 * we encode each text part as a separate EasyInputMessage.
 *
 * @param message - The assistant message to encode
 * @param encodeThoughtsAsText - Whether to encode thoughts as text
 * @returns Array of input items (text messages and function calls)
 */
function encodeAssistantMessage(
  message: AssistantMessage,
  encodeThoughtsAsText: boolean
): ResponseInputItem[] {
  const result: ResponseInputItem[] = [];

  for (const part of message.content) {
    if (part.type === 'text') {
      result.push({
        role: 'assistant',
        content: part.text,
      });
      /* v8 ignore start - thought encoding will be tested via e2e */
    } else if (part.type === 'thought') {
      // Encode thoughts as text when requested, otherwise drop
      if (encodeThoughtsAsText) {
        result.push({
          role: 'assistant',
          content: '**Thinking:** ' + part.thought,
        });
      }
      /* v8 ignore stop */
      /* v8 ignore start - tool call encoding will be tested via e2e */
    } else if (part.type === 'tool_call') {
      const toolCallItem: ResponseFunctionToolCall = {
        type: 'function_call',
        id: part.id,
        call_id: part.id, // Used to match with function_call_output
        name: part.name,
        arguments: part.args,
        status: 'completed', // Required for model to recognize tool was executed
      };
      result.push(toolCallItem);
    }
    /* v8 ignore stop */
  }

  return result;
}

/**
 * Build the request parameters for the OpenAI Responses API.
 *
 * This function performs strict param checking - any unhandled params will
 * cause an error to ensure we don't silently ignore user configuration.
 *
 * @param modelId - The model ID to use
 * @param messages - The messages to send
 * @param tools - Optional tools to make available to the model
 * @param params - Optional parameters (temperature, maxTokens, etc.)
 */
export function buildRequestParams(
  modelId: OpenAIModelId,
  messages: readonly Message[],
  tools?: readonly ToolSchema[],
  params: Params = {}
): ResponseCreateParamsNonStreaming {
  return ParamHandler.with(params, 'openai', modelId, (p) => {
    const thinkingConfig = p.get('thinking');
    const encodeThoughtsAsText = thinkingConfig?.encodeThoughtsAsText ?? false;

    const inputItems = encodeMessages(messages, modelId, encodeThoughtsAsText);

    const requestParams: ResponseCreateParamsNonStreaming = {
      model: modelName(modelId, null),
      input: inputItems,
    };

    /* v8 ignore start - tool encoding will be tested via e2e */
    if (tools && tools.length > 0) {
      requestParams.tools = encodeTools(tools);
    }
    /* v8 ignore stop */

    const maxTokens = p.get('maxTokens');
    if (maxTokens !== undefined) {
      requestParams.max_output_tokens = maxTokens;
    }

    const temperature = p.get('temperature');
    if (temperature !== undefined) {
      requestParams.temperature = temperature;
    }

    const topP = p.get('topP');
    if (topP !== undefined) {
      requestParams.top_p = topP;
    }

    // OpenAI Responses API doesn't support these params
    p.warnUnsupported('topK', 'OpenAI does not support the top_k parameter');
    p.warnUnsupported(
      'seed',
      'OpenAI Responses API does not support the seed parameter'
    );
    p.warnUnsupported(
      'stopSequences',
      'OpenAI Responses API does not support stop sequences'
    );

    if (thinkingConfig) {
      const includeThoughts = thinkingConfig.includeThoughts ?? false;
      requestParams.reasoning = computeReasoning(
        thinkingConfig.level,
        includeThoughts
      );
    }

    return requestParams;
  });
}

/**
 * Decode OpenAI Responses API response to Mirascope types.
 *
 * @param response - The raw OpenAI Responses API response
 * @param modelId - The model ID used for the request
 * @param includeThoughts - Whether to include reasoning blocks in the response (default: false)
 */
export function decodeResponse(
  response: OpenAIResponse,
  modelId: OpenAIModelId,
  includeThoughts: boolean = false
): {
  assistantMessage: AssistantMessage;
  finishReason: FinishReason | null;
  usage: Usage | null;
} {
  const content = decodeContent(response.output, includeThoughts);
  const finishReason = decodeFinishReason(response);

  // Store serialized output items for round-tripping in resume operations.
  // This allows sending the exact output back as input when resuming.
  const serializedOutput = response.output.map(serializeOutputItem);

  const assistantMessage: AssistantMessage = {
    role: 'assistant',
    content,
    name: null,
    providerId: 'openai',
    modelId,
    providerModelName: modelName(modelId, 'responses'),
    rawMessage: serializedOutput as unknown as AssistantMessage['rawMessage'],
  };

  /* v8 ignore next - usage is always present in API responses */
  const usage = response.usage ? decodeUsage(response.usage) : null;

  return { assistantMessage, finishReason, usage };
}

/**
 * Decode output items from the Responses API to Mirascope content format.
 *
 * @param output - The output items from the response
 * @param includeThoughts - Whether to include reasoning blocks as thoughts
 */
function decodeContent(
  output: OpenAIResponse['output'],
  includeThoughts: boolean
): AssistantContentPart[] {
  const parts: AssistantContentPart[] = [];

  for (const item of output) {
    if (item.type === 'message') {
      for (const contentPart of item.content) {
        if (contentPart.type === 'output_text') {
          const text: Text = { type: 'text', text: contentPart.text };
          parts.push(text);
          /* v8 ignore start - refusals are difficult to trigger reliably */
        } else if (contentPart.type === 'refusal') {
          const text: Text = { type: 'text', text: contentPart.refusal };
          parts.push(text);
        }
        /* v8 ignore stop */
      }
      /* v8 ignore start - tool decoding will be tested via e2e */
    } else if (item.type === 'function_call') {
      const toolCall: ToolCall = {
        type: 'tool_call',
        id: item.call_id,
        name: item.name,
        args: item.arguments,
      };
      parts.push(toolCall);
      /* v8 ignore stop */
    } else if (item.type === 'reasoning') {
      if (includeThoughts) {
        // Extract thoughts from summary (preferred) or content
        /* v8 ignore next - summary is always defined per types, but defensive coding */
        for (const summaryPart of item.summary ?? []) {
          if (summaryPart.type === 'summary_text') {
            const thought: Thought = {
              type: 'thought',
              thought: summaryPart.text,
            };
            parts.push(thought);
          }
        }
        /* v8 ignore start - reasoning_text content is rare, likely only in open-source models */
        if (item.content) {
          for (const contentPart of item.content) {
            if (contentPart.type === 'reasoning_text') {
              const thought: Thought = {
                type: 'thought',
                thought: contentPart.text,
              };
              parts.push(thought);
            }
          }
        }
        /* v8 ignore stop */
      }
    }
  }

  return parts;
}

/**
 * Decode finish reason from the Responses API.
 *
 * The Responses API uses `incomplete_details.reason` instead of `finish_reason`.
 */
function decodeFinishReason(response: OpenAIResponse): FinishReason | null {
  // Check for refusal in output content
  for (const item of response.output) {
    if (item.type === 'message') {
      for (const contentPart of item.content) {
        /* v8 ignore start - refusals are difficult to trigger reliably */
        if (contentPart.type === 'refusal') {
          return FinishReason.REFUSAL;
        }
        /* v8 ignore end */
      }
    }
  }

  // Check incomplete_details for finish reason
  if (response.incomplete_details) {
    const reason = response.incomplete_details.reason;
    if (reason === 'max_output_tokens') {
      return FinishReason.MAX_TOKENS;
    }
    /* v8 ignore start - refusals are difficult to trigger reliably */
    if (reason === 'content_filter') {
      return FinishReason.REFUSAL;
    }
    /* v8 ignore stop */
  }

  return null; // Normal completion
}

/**
 * Decode usage information from the Responses API.
 */
function decodeUsage(usage: NonNullable<OpenAIResponse['usage']>): Usage {
  return createUsage({
    inputTokens: usage.input_tokens,
    outputTokens: usage.output_tokens,
    cacheReadTokens: usage.input_tokens_details?.cached_tokens ?? 0,
    reasoningTokens: usage.output_tokens_details?.reasoning_tokens ?? 0,
    raw: usage,
  });
}

/**
 * Serialize an output item for storage in rawMessage.
 *
 * This is used for round-tripping assistant messages through the API.
 * The serialized items can be sent directly back as input items when
 * resuming a conversation.
 */
function serializeOutputItem(
  item: ResponseOutputItem
): Record<string, unknown> {
  // Copy all non-undefined properties from the item
  const serialized: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(item)) {
    if (value !== undefined) {
      serialized[key] = value;
    }
  }
  return serialized;
}
