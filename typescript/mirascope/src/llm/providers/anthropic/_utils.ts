/**
 * Anthropic-specific utilities for encoding requests and decoding responses.
 */

import Anthropic from '@anthropic-ai/sdk';
import type {
  ContentBlock,
  Message as AnthropicMessage,
  MessageCreateParamsNonStreaming,
} from '@anthropic-ai/sdk/resources/messages';

import type { AssistantContentPart, Text } from '@/llm/content';
import {
  APIError,
  AuthenticationError,
  BadRequestError,
  ConnectionError,
  FeatureNotSupportedError,
  NotFoundError,
  PermissionError,
  RateLimitError,
  ServerError,
} from '@/llm/exceptions';
import type { AssistantMessage, Message, SystemMessage } from '@/llm/messages';
import type { Params } from '@/llm/models';
import { ParamHandler, type ProviderErrorMap } from '@/llm/providers/base';
import type { AnthropicModelId } from '@/llm/providers/anthropic/model-id';
import { modelName } from '@/llm/providers/anthropic/model-id';
import { FinishReason } from '@/llm/responses/finish-reason';
import type { Usage } from '@/llm/responses/usage';
import { createUsage } from '@/llm/responses/usage';

/**
 * Error mapping from Anthropic SDK exceptions to Mirascope error types.
 */
export const ANTHROPIC_ERROR_MAP: ProviderErrorMap = [
  [Anthropic.AuthenticationError, AuthenticationError],
  [Anthropic.PermissionDeniedError, PermissionError],
  [Anthropic.BadRequestError, BadRequestError],
  [Anthropic.NotFoundError, NotFoundError],
  [Anthropic.RateLimitError, RateLimitError],
  [Anthropic.InternalServerError, ServerError],
  [Anthropic.APIError, APIError],
  [Anthropic.APIConnectionError, ConnectionError],
];

/**
 * Encode Mirascope messages to Anthropic API format.
 */
export function encodeMessages(messages: readonly Message[]): {
  system: string | undefined;
  messages: MessageCreateParamsNonStreaming['messages'];
} {
  let system: string | undefined;
  const anthropicMessages: MessageCreateParamsNonStreaming['messages'] = [];

  for (const message of messages) {
    if (message.role === 'system') {
      system = encodeSystemMessage(message);
    } else if (message.role === 'user') {
      anthropicMessages.push({
        role: 'user',
        content: encodeUserContent(message.content),
      });
    } else if (message.role === 'assistant') {
      anthropicMessages.push({
        role: 'assistant',
        content: encodeAssistantContent(message.content),
      });
    }
  }

  return { system, messages: anthropicMessages };
}

function encodeSystemMessage(message: SystemMessage): string {
  return message.content.text;
}

function encodeUserContent(
  content: readonly { type: string; text?: string }[]
): string | Anthropic.Messages.ContentBlockParam[] {
  // If single text part, return as string for simplicity
  const first = content[0];
  if (content.length === 1 && first && first.type === 'text' && first.text) {
    return first.text;
  }

  // Handle array content
  const blocks: Anthropic.Messages.ContentBlockParam[] = [];

  for (const part of content) {
    if (part.type === 'text' && part.text) {
      blocks.push({ type: 'text', text: part.text });
    } else if (part.type === 'image') {
      throw new FeatureNotSupportedError(
        'image content encoding',
        'anthropic',
        null,
        'Image content in user messages is not yet implemented'
      );
    } else if (part.type === 'audio') {
      throw new FeatureNotSupportedError(
        'audio content encoding',
        'anthropic',
        null,
        'Audio content in user messages is not yet implemented'
      );
    } else if (part.type === 'document') {
      throw new FeatureNotSupportedError(
        'document content encoding',
        'anthropic',
        null,
        'Document content in user messages is not yet implemented'
      );
    }
  }

  return blocks;
}

function encodeAssistantContent(
  content: readonly AssistantContentPart[]
): Anthropic.Messages.ContentBlockParam[] {
  return content.map((part) => {
    if (part.type === 'text') {
      return { type: 'text' as const, text: part.text };
    }
    if (part.type === 'tool_call') {
      throw new FeatureNotSupportedError(
        'tool call encoding',
        'anthropic',
        null,
        'Tool calls in assistant messages are not yet implemented'
      );
    }
    if (part.type === 'thought') {
      throw new FeatureNotSupportedError(
        'thought encoding',
        'anthropic',
        null,
        'Thought content in assistant messages is not yet implemented'
      );
    }
    // Unknown content type
    throw new FeatureNotSupportedError(
      `unknown content type: ${(part as { type: string }).type}`,
      'anthropic',
      null,
      `Unknown assistant content type: ${(part as { type: string }).type}`
    );
  });
}

/**
 * Build the request parameters for the Anthropic API.
 *
 * This function performs strict param checking - any unhandled params will
 * cause an error to ensure we don't silently ignore user configuration.
 */
export function buildRequestParams(
  modelId: AnthropicModelId,
  messages: readonly Message[],
  params: Params = {}
): MessageCreateParamsNonStreaming {
  const { system, messages: anthropicMessages } = encodeMessages(messages);

  return ParamHandler.with(params, 'anthropic', modelId, (p) => {
    const requestParams: MessageCreateParamsNonStreaming = {
      model: modelName(modelId),
      messages: anthropicMessages,
      max_tokens: p.getOrDefault('maxTokens', 4096),
    };

    if (system) {
      requestParams.system = system;
    }

    const temperature = p.get('temperature');
    if (temperature !== undefined) {
      requestParams.temperature = temperature;
    }

    const topP = p.get('topP');
    if (topP !== undefined) {
      requestParams.top_p = topP;
    }

    const topK = p.get('topK');
    if (topK !== undefined) {
      requestParams.top_k = topK;
    }

    const stopSequences = p.get('stopSequences');
    if (stopSequences !== undefined) {
      requestParams.stop_sequences = stopSequences;
    }

    // Anthropic doesn't support seed
    p.throwUnsupported('seed', 'Anthropic does not support the seed parameter');

    // Thinking not yet implemented
    p.warnNotImplemented('thinking', 'thinking config');

    return requestParams;
  });
}

/**
 * Decode Anthropic response to Mirascope types.
 */
export function decodeResponse(
  response: AnthropicMessage,
  modelId: AnthropicModelId
): {
  assistantMessage: AssistantMessage;
  finishReason: FinishReason | null;
  usage: Usage | null;
} {
  const content = decodeContent(response.content);

  const assistantMessage: AssistantMessage = {
    role: 'assistant',
    content,
    name: null,
    providerId: 'anthropic',
    modelId,
    providerModelName: response.model,
    rawMessage: response as unknown as AssistantMessage['rawMessage'],
  };

  const finishReason = decodeStopReason(response.stop_reason);
  const usage = decodeUsage(response.usage);

  return { assistantMessage, finishReason, usage };
}

function decodeContent(content: ContentBlock[]): AssistantContentPart[] {
  const parts: AssistantContentPart[] = [];

  for (const block of content) {
    if (block.type === 'text') {
      const text: Text = { type: 'text', text: block.text };
      parts.push(text);
    } else if (block.type === 'tool_use') {
      throw new FeatureNotSupportedError(
        'tool use decoding',
        'anthropic',
        null,
        'Tool use blocks in responses are not yet implemented'
      );
    } else if (block.type === 'thinking') {
      throw new FeatureNotSupportedError(
        'thinking decoding',
        'anthropic',
        null,
        'Thinking blocks in responses are not yet implemented'
      );
    } else {
      // Unknown block type - be strict so we know what we're missing
      throw new FeatureNotSupportedError(
        `unknown block type: ${block.type}`,
        'anthropic',
        null,
        `Unknown content block type '${block.type}' in response is not yet implemented`
      );
    }
  }

  return parts;
}

function decodeStopReason(
  stopReason: AnthropicMessage['stop_reason']
): FinishReason | null {
  switch (stopReason) {
    case 'max_tokens':
      return FinishReason.MAX_TOKENS;
    case 'end_turn':
    case 'stop_sequence':
    case 'tool_use':
      return null; // Normal completion
    default:
      return null;
  }
}

function decodeUsage(usage: AnthropicMessage['usage']): Usage {
  return createUsage({
    inputTokens: usage.input_tokens,
    outputTokens: usage.output_tokens,
    cacheReadTokens: usage.cache_read_input_tokens ?? 0,
    cacheWriteTokens: usage.cache_creation_input_tokens ?? 0,
    raw: usage,
  });
}
