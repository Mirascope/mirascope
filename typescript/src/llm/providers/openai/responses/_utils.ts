/**
 * OpenAI Responses API utilities for encoding requests and decoding responses.
 */

import type OpenAI from 'openai';
import type {
  Response as OpenAIResponse,
  ResponseInputContent,
  ResponseInputImage,
} from 'openai/resources/responses/responses';
import type { Reasoning, ReasoningEffort } from 'openai/resources/shared';

import type { AssistantContentPart, Image, Text, Thought } from '@/llm/content';
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
 * Input item type for OpenAI Responses API.
 *
 * The Responses API uses EasyInputMessage for simple message format,
 * which supports 'user', 'assistant', and 'developer' (system) roles.
 */
type ResponseInputItem = OpenAI.Responses.EasyInputMessage;

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
 */
export function encodeMessages(
  messages: readonly Message[]
): ResponseInputItem[] {
  const inputItems: ResponseInputItem[] = [];

  for (const message of messages) {
    if (message.role === 'system') {
      inputItems.push({
        role: 'developer',
        content: message.content.text,
      });
    } else if (message.role === 'user') {
      inputItems.push(encodeUserMessage(message));
    } else if (message.role === 'assistant') {
      // Assistant messages may produce multiple items (one per text part)
      inputItems.push(...encodeAssistantMessage(message));
    }
  }

  return inputItems;
}

/**
 * Encode a Mirascope user message to OpenAI Responses API format.
 *
 * - Single text part: string content (simplified)
 * - Multiple parts or non-text content: array of content items
 */
function encodeUserMessage(
  message: Extract<Message, { role: 'user' }>
): ResponseInputItem {
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

      /* v8 ignore start - content types not yet implemented */
      case 'document':
        throw new FeatureNotSupportedError(
          'document content encoding',
          'openai',
          null,
          'Document content is not yet implemented'
        );

      case 'tool_output':
        throw new FeatureNotSupportedError(
          'tool output encoding',
          'openai',
          null,
          'Tool outputs are not yet implemented'
        );
      /* v8 ignore stop */
    }
  }

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
 * @returns Array of input items (one per text part)
 */
function encodeAssistantMessage(
  message: AssistantMessage
): ResponseInputItem[] {
  const result: ResponseInputItem[] = [];

  for (const part of message.content) {
    if (part.type === 'text') {
      result.push({
        role: 'assistant',
        content: part.text,
      });
    }
    // Note: tool_call and thought are not yet implemented
  }

  return result;
}

/**
 * Request parameters for the OpenAI Responses API.
 */
export interface ResponsesRequestParams {
  model: string;
  input: ResponseInputItem[];
  max_output_tokens?: number;
  temperature?: number;
  top_p?: number;
  reasoning?: Reasoning;
}

/**
 * Build the request parameters for the OpenAI Responses API.
 *
 * This function performs strict param checking - any unhandled params will
 * cause an error to ensure we don't silently ignore user configuration.
 */
export function buildRequestParams(
  modelId: OpenAIModelId,
  messages: readonly Message[],
  params: Params = {}
): ResponsesRequestParams {
  const inputItems = encodeMessages(messages);

  return ParamHandler.with(params, 'openai', modelId, (p) => {
    const requestParams: ResponsesRequestParams = {
      model: modelName(modelId, null),
      input: inputItems,
    };

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

    const thinkingConfig = p.get('thinking');
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

  const assistantMessage: AssistantMessage = {
    role: 'assistant',
    content,
    name: null,
    providerId: 'openai',
    modelId,
    providerModelName: response.model,
    rawMessage: response as unknown as AssistantMessage['rawMessage'],
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
      /* v8 ignore start - content types not yet implemented */
    } else if (item.type === 'function_call') {
      throw new FeatureNotSupportedError(
        'function call decoding',
        'openai',
        null,
        'Function calls in responses are not yet implemented'
      );
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
