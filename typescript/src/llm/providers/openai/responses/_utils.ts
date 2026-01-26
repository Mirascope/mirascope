/**
 * OpenAI Responses API utilities for encoding requests and decoding responses.
 */

import type OpenAI from 'openai';
import type { Response as OpenAIResponse } from 'openai/resources/responses/responses';

import type {
  AssistantContentPart,
  Text,
  UserContentPart,
} from '@/llm/content';
import { FeatureNotSupportedError } from '@/llm/exceptions';
import type { AssistantMessage, Message } from '@/llm/messages';
import type { Params } from '@/llm/models';
import { ParamHandler } from '@/llm/providers/base';
import type { OpenAIModelId } from '@/llm/providers/openai/model-id';
import { modelName } from '@/llm/providers/openai/model-id';
import { FinishReason } from '@/llm/responses/finish-reason';
import type { Usage } from '@/llm/responses/usage';
import { createUsage } from '@/llm/responses/usage';

/**
 * Input item type for OpenAI Responses API.
 *
 * The Responses API uses EasyInputMessage for simple message format,
 * which supports 'user', 'assistant', and 'developer' (system) roles.
 */
type ResponseInputItem = OpenAI.Responses.EasyInputMessage;

// ============================================================================
// Content Part Processing
// ============================================================================

/**
 * Result of processing content parts for the Responses API.
 * Since Responses API only accepts string content, we accumulate text strings.
 */
interface ProcessedContentParts {
  text: string[];
}

/**
 * Process content parts from either user or assistant messages.
 * Extracts text content as strings for the Responses API format.
 */
function processContentParts(
  content: readonly (UserContentPart | AssistantContentPart)[]
): ProcessedContentParts {
  const result: ProcessedContentParts = {
    text: [],
  };

  for (const part of content) {
    switch (part.type) {
      case 'text':
        result.text.push(part.text);
        break;

      /* v8 ignore start - content types not yet implemented */
      case 'image':
        throw new FeatureNotSupportedError(
          'image content encoding',
          'openai',
          null,
          'Image content is not yet implemented'
        );

      case 'audio':
        throw new FeatureNotSupportedError(
          'audio content encoding',
          'openai',
          null,
          'Audio content is not yet implemented'
        );

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

      case 'tool_call':
        throw new FeatureNotSupportedError(
          'tool call encoding',
          'openai',
          null,
          'Tool calls are not yet implemented'
        );

      case 'thought':
        throw new FeatureNotSupportedError(
          'thought encoding',
          'openai',
          null,
          'Thought content is not yet implemented'
        );
      /* v8 ignore stop */
    }
  }

  return result;
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
      inputItems.push(encodeAssistantMessage(message));
    }
  }

  return inputItems;
}

/**
 * Encode a Mirascope user message to OpenAI Responses API format.
 */
function encodeUserMessage(
  message: Extract<Message, { role: 'user' }>
): ResponseInputItem {
  const { text } = processContentParts(message.content);

  return {
    role: 'user',
    content: text.join(''),
  };
}

/**
 * Encode a Mirascope assistant message to OpenAI Responses API format.
 */
function encodeAssistantMessage(message: AssistantMessage): ResponseInputItem {
  const { text } = processContentParts(message.content);

  return {
    role: 'assistant',
    content: text.join(''),
  };
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

    // Thinking not yet implemented
    p.warnNotImplemented('thinking', 'thinking config');

    return requestParams;
  });
}

/**
 * Decode OpenAI Responses API response to Mirascope types.
 */
export function decodeResponse(
  response: OpenAIResponse,
  modelId: OpenAIModelId
): {
  assistantMessage: AssistantMessage;
  finishReason: FinishReason | null;
  usage: Usage | null;
} {
  const content = decodeContent(response.output);
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

  const usage = response.usage ? decodeUsage(response.usage) : null;

  return { assistantMessage, finishReason, usage };
}

/**
 * Decode output items from the Responses API to Mirascope content format.
 */
function decodeContent(
  output: OpenAIResponse['output']
): AssistantContentPart[] {
  const parts: AssistantContentPart[] = [];

  for (const item of output) {
    if (item.type === 'message') {
      for (const contentPart of item.content) {
        if (contentPart.type === 'output_text') {
          const text: Text = { type: 'text', text: contentPart.text };
          parts.push(text);
        } else if (contentPart.type === 'refusal') {
          const text: Text = { type: 'text', text: contentPart.refusal };
          parts.push(text);
        }
        /* v8 ignore start - content types not yet implemented */
      }
    } else if (item.type === 'function_call') {
      throw new FeatureNotSupportedError(
        'function call decoding',
        'openai',
        null,
        'Function calls in responses are not yet implemented'
      );
    } else if (item.type === 'reasoning') {
      // Reasoning blocks are internal model reasoning - skip them in output for now
      // TODO: Add support for reasoning blocks
      continue;
    }
    /* v8 ignore stop */
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
        if (contentPart.type === 'refusal') {
          return FinishReason.REFUSAL;
        }
      }
    }
  }

  // Check incomplete_details for finish reason
  if (response.incomplete_details) {
    const reason = response.incomplete_details.reason;
    if (reason === 'max_output_tokens') {
      return FinishReason.MAX_TOKENS;
    }
    if (reason === 'content_filter') {
      return FinishReason.REFUSAL;
    }
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
