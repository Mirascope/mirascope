/**
 * Anthropic-specific utilities for encoding requests and decoding responses.
 */

import Anthropic from '@anthropic-ai/sdk';
import type {
  ContentBlock,
  Message as AnthropicMessage,
  MessageCreateParamsNonStreaming,
} from '@anthropic-ai/sdk/resources/messages';

import type {
  AssistantContentPart,
  Text,
  Thought,
  UserContentPart,
} from '@/llm/content';
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
import type { AssistantMessage, Message } from '@/llm/messages';
import type { Params } from '@/llm/models';
import type { ThinkingLevel } from '@/llm/models/thinking-config';
import { ParamHandler, type ProviderErrorMap } from '@/llm/providers/base';
import type { AnthropicModelId } from '@/llm/providers/anthropic/model-id';
import { modelName } from '@/llm/providers/anthropic/model-id';
import { FinishReason } from '@/llm/responses/finish-reason';
import type { Usage } from '@/llm/responses/usage';
import { createUsage } from '@/llm/responses/usage';

/**
 * Default max tokens for Anthropic requests.
 */
const DEFAULT_MAX_TOKENS = 4096;

/**
 * Thinking level to budget multiplier mapping.
 * The multiplier is applied to max_tokens to compute the thinking budget.
 */
const THINKING_LEVEL_TO_BUDGET_MULTIPLIER: Record<
  Exclude<ThinkingLevel, 'none' | 'default'>,
  number
> = {
  minimal: 0, // Will become 1024 (minimum allowed)
  low: 0.2,
  medium: 0.4,
  high: 0.6,
  max: 0.8,
};

/**
 * Compute Anthropic token budget from ThinkingConfig level.
 *
 * @param level - The thinking level from ThinkingConfig
 * @param maxTokens - The max_tokens value for the request
 * @returns Token budget (0 to disable, -1 for provider default, positive for budget)
 */
export function computeThinkingBudget(
  level: ThinkingLevel,
  maxTokens: number
): number {
  if (level === 'none') {
    return 0; // Disabled
  }
  if (level === 'default') {
    return -1; // Use provider default (don't set thinking param)
  }

  const multiplier = THINKING_LEVEL_TO_BUDGET_MULTIPLIER[level];
  const budget = Math.floor(multiplier * maxTokens);
  return Math.max(1024, budget); // Minimum 1024 tokens
}

/**
 * Error mapping from Anthropic SDK exceptions to Mirascope error types.
 * Note: More specific error classes must come before their parent classes
 * since the error map is checked with instanceof in order.
 */
export const ANTHROPIC_ERROR_MAP: ProviderErrorMap = [
  [Anthropic.AuthenticationError, AuthenticationError],
  [Anthropic.PermissionDeniedError, PermissionError],
  [Anthropic.BadRequestError, BadRequestError],
  [Anthropic.NotFoundError, NotFoundError],
  [Anthropic.RateLimitError, RateLimitError],
  [Anthropic.InternalServerError, ServerError],
  [Anthropic.APIConnectionError, ConnectionError],
  [Anthropic.APIError, APIError],
];

// ============================================================================
// Content Part Processing
// ============================================================================

/**
 * Process content parts from either user or assistant messages.
 * Converts to Anthropic's ContentBlockParam format.
 */
function processContentParts(
  content: readonly (UserContentPart | AssistantContentPart)[]
): Anthropic.Messages.ContentBlockParam[] {
  const blocks: Anthropic.Messages.ContentBlockParam[] = [];

  for (const part of content) {
    switch (part.type) {
      case 'text':
        blocks.push({ type: 'text', text: part.text });
        break;

      /* v8 ignore start - content types not yet implemented */
      case 'image':
        throw new FeatureNotSupportedError(
          'image content encoding',
          'anthropic',
          null,
          'Image content is not yet implemented'
        );

      case 'audio':
        throw new FeatureNotSupportedError(
          'audio content encoding',
          'anthropic',
          null,
          'Audio content is not yet implemented'
        );

      case 'document':
        throw new FeatureNotSupportedError(
          'document content encoding',
          'anthropic',
          null,
          'Document content is not yet implemented'
        );

      case 'tool_output':
        throw new FeatureNotSupportedError(
          'tool output encoding',
          'anthropic',
          null,
          'Tool outputs are not yet implemented'
        );

      case 'tool_call':
        throw new FeatureNotSupportedError(
          'tool call encoding',
          'anthropic',
          null,
          'Tool calls are not yet implemented'
        );

      case 'thought':
        throw new FeatureNotSupportedError(
          'thought encoding',
          'anthropic',
          null,
          'Thought content is not yet implemented'
        );
      /* v8 ignore stop */
    }
  }

  return blocks;
}

// ============================================================================
// Content Simplification
// ============================================================================

/**
 * Simplify user content to string if only a single text part.
 * Anthropic accepts string for simple user messages.
 */
function simplifyUserContent(
  blocks: Anthropic.Messages.ContentBlockParam[]
): string | Anthropic.Messages.ContentBlockParam[] {
  if (blocks.length === 1 && blocks[0] && blocks[0].type === 'text') {
    return blocks[0].text;
  }
  return blocks;
}

// ============================================================================
// Message Encoding
// ============================================================================

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
      system = message.content.text;
    } else if (message.role === 'user') {
      const blocks = processContentParts(message.content);
      anthropicMessages.push({
        role: 'user',
        content: simplifyUserContent(blocks),
      });
    } else if (message.role === 'assistant') {
      anthropicMessages.push({
        role: 'assistant',
        content: processContentParts(message.content),
      });
    }
  }

  return { system, messages: anthropicMessages };
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
    const maxTokens = p.getOrDefault('maxTokens', DEFAULT_MAX_TOKENS);
    const requestParams: MessageCreateParamsNonStreaming = {
      model: modelName(modelId),
      messages: anthropicMessages,
      max_tokens: maxTokens,
    };

    if (system) {
      requestParams.system = system;
    }

    const temperature = p.get('temperature');
    const topP = p.get('topP');

    // Anthropic doesn't allow both temperature and topP together
    if (temperature !== undefined && topP !== undefined) {
      throw new FeatureNotSupportedError(
        'temperature + topP',
        'anthropic',
        modelId,
        'Anthropic does not allow both temperature and top_p to be specified together'
      );
    }

    if (temperature !== undefined) {
      requestParams.temperature = temperature;
    }

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
    p.warnUnsupported('seed', 'Anthropic does not support the seed parameter');

    const thinkingConfig = p.get('thinking');
    if (thinkingConfig) {
      const budget = computeThinkingBudget(thinkingConfig.level, maxTokens);
      if (budget === 0) {
        requestParams.thinking = { type: 'disabled' };
      } else if (budget > 0) {
        requestParams.thinking = { type: 'enabled', budget_tokens: budget };
      }
      // If budget === -1, don't set thinking (use provider default)
    }

    return requestParams;
  });
}

/**
 * Decode Anthropic response to Mirascope types.
 *
 * @param response - The raw Anthropic API response
 * @param modelId - The model ID used for the request
 * @param includeThoughts - Whether to include thinking blocks in the response (default: false)
 */
export function decodeResponse(
  response: AnthropicMessage,
  modelId: AnthropicModelId,
  includeThoughts: boolean = false
): {
  assistantMessage: AssistantMessage;
  finishReason: FinishReason | null;
  usage: Usage | null;
} {
  const content = decodeContent(response.content, includeThoughts);

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

function decodeContent(
  content: ContentBlock[],
  includeThoughts: boolean
): AssistantContentPart[] {
  const parts: AssistantContentPart[] = [];

  for (const block of content) {
    if (block.type === 'text') {
      const text: Text = { type: 'text', text: block.text };
      parts.push(text);
    } else if (block.type === 'thinking') {
      if (includeThoughts) {
        const thought: Thought = { type: 'thought', thought: block.thinking };
        parts.push(thought);
      }
      /* v8 ignore start - redacted_thinking can't be reliably triggered in tests */
    } else if (block.type === 'redacted_thinking') {
      // Skip redacted thinking blocks - they contain encrypted thinking
      // that cannot be decoded
      continue;
      /* v8 ignore stop */
      /* v8 ignore start - content types not yet implemented */
    } else if (block.type === 'tool_use') {
      throw new FeatureNotSupportedError(
        'tool use decoding',
        'anthropic',
        null,
        'Tool use blocks in responses are not yet implemented'
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
    /* v8 ignore stop */
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
    /* v8 ignore next 2 - defensive default case */
    default:
      return null;
  }
}

export function decodeUsage(usage: AnthropicMessage['usage']): Usage {
  return createUsage({
    inputTokens: usage.input_tokens,
    outputTokens: usage.output_tokens,
    /* v8 ignore next 2 - cache tokens only present with caching enabled, will add tests later */
    cacheReadTokens: usage.cache_read_input_tokens ?? 0,
    cacheWriteTokens: usage.cache_creation_input_tokens ?? 0,
    raw: usage,
  });
}
