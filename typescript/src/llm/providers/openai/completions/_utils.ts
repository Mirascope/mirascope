/**
 * OpenAI Completions API utilities for encoding requests and decoding responses.
 */

import type {
  ChatCompletion,
  ChatCompletionAssistantMessageParam,
  ChatCompletionContentPart,
  ChatCompletionContentPartText,
  ChatCompletionCreateParamsNonStreaming,
  ChatCompletionMessageParam,
} from 'openai/resources/chat/completions';

import type {
  AssistantContentPart,
  Text,
  UserContentPart,
} from '@/llm/content';
import { FeatureNotSupportedError } from '@/llm/exceptions';
import type { AssistantMessage, Message, SystemMessage } from '@/llm/messages';
import type { Params } from '@/llm/models';
import { ParamHandler } from '@/llm/providers/base';
import type { OpenAIModelId } from '@/llm/providers/openai/model-id';
import { modelName } from '@/llm/providers/openai/model-id';
import { FinishReason } from '@/llm/responses/finish-reason';
import type { Usage } from '@/llm/responses/usage';
import { createUsage } from '@/llm/responses/usage';

// ============================================================================
// Content Part Processing
// ============================================================================

interface ProcessContentOptions {
  encodeThoughtsAsText?: boolean;
}

/**
 * Result of processing content parts, categorized by type.
 */
interface ProcessedContentParts {
  text: ChatCompletionContentPartText[];
}

/**
 * Process content parts from either user or assistant messages.
 * Categorizes parts by type and converts to OpenAI format where applicable.
 */
function processContentParts(
  content: readonly (UserContentPart | AssistantContentPart)[],
  options: ProcessContentOptions = {}
): ProcessedContentParts {
  const result: ProcessedContentParts = {
    text: [],
  };

  for (const part of content) {
    switch (part.type) {
      case 'text':
        result.text.push({ type: 'text', text: part.text });
        break;

      case 'thought':
        // When encodeThoughtsAsText is true, encode as text; otherwise drop
        if (options.encodeThoughtsAsText) {
          result.text.push({
            type: 'text',
            text: '**Thinking:** ' + part.thought,
          });
        }
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
      /* v8 ignore stop */
    }
  }

  return result;
}

// ============================================================================
// Content Simplification
// ============================================================================

/**
 * Simplify content parts to string if only a single text part.
 * For multiple parts, returns the array as-is.
 */
function simplifyContent<T extends ChatCompletionContentPart>(
  parts: T[]
): string | T[] {
  if (parts.length === 1 && parts[0] && parts[0].type === 'text') {
    return parts[0].text;
  }
  return parts;
}

/**
 * Encode Mirascope messages to OpenAI Chat Completions API format.
 *
 * @param messages - The messages to encode
 * @param encodeThoughtsAsText - Whether to encode thoughts as text in assistant messages
 */
export function encodeMessages(
  messages: readonly Message[],
  encodeThoughtsAsText: boolean = false
): ChatCompletionMessageParam[] {
  const openaiMessages: ChatCompletionMessageParam[] = [];

  for (const message of messages) {
    if (message.role === 'system') {
      openaiMessages.push(encodeSystemMessage(message));
    } else if (message.role === 'user') {
      openaiMessages.push(encodeUserMessage(message));
    } else if (message.role === 'assistant') {
      openaiMessages.push(
        encodeAssistantMessage(message, encodeThoughtsAsText)
      );
    }
  }

  return openaiMessages;
}

function encodeSystemMessage(
  message: SystemMessage
): ChatCompletionMessageParam {
  return {
    role: 'system',
    content: message.content.text,
  };
}

/**
 * Encode a Mirascope user message to OpenAI format.
 */
function encodeUserMessage(
  message: Extract<Message, { role: 'user' }>
): ChatCompletionMessageParam {
  const { text } = processContentParts(message.content);

  return {
    role: 'user',
    content: simplifyContent(text),
    ...(message.name && { name: message.name }),
  };
}

/**
 * Encode a Mirascope assistant message to OpenAI format.
 */
function encodeAssistantMessage(
  message: AssistantMessage,
  encodeThoughtsAsText: boolean
): ChatCompletionAssistantMessageParam {
  const { text } = processContentParts(message.content, {
    encodeThoughtsAsText,
  });

  // Join text parts into a single string for assistant messages
  const content = text.map((p) => p.text).join('') || null;

  return {
    role: 'assistant',
    content,
    ...(message.name && { name: message.name }),
  };
}

/**
 * Build the request parameters for the OpenAI Chat Completions API.
 *
 * This function performs strict param checking - any unhandled params will
 * cause an error to ensure we don't silently ignore user configuration.
 */
export function buildRequestParams(
  modelId: OpenAIModelId,
  messages: readonly Message[],
  params: Params = {}
): ChatCompletionCreateParamsNonStreaming {
  return ParamHandler.with(params, 'openai', modelId, (p) => {
    const thinkingConfig = p.get('thinking');
    const encodeThoughtsAsText = thinkingConfig?.encodeThoughtsAsText ?? false;

    const openaiMessages = encodeMessages(messages, encodeThoughtsAsText);

    const requestParams: ChatCompletionCreateParamsNonStreaming = {
      model: modelName(modelId, null),
      messages: openaiMessages,
    };

    const maxTokens = p.get('maxTokens');
    if (maxTokens !== undefined) {
      // max_completion_tokens is the preferred parameter (max_tokens is deprecated)
      requestParams.max_completion_tokens = maxTokens;
    }

    const temperature = p.get('temperature');
    if (temperature !== undefined) {
      requestParams.temperature = temperature;
    }

    const topP = p.get('topP');
    if (topP !== undefined) {
      requestParams.top_p = topP;
    }

    const seed = p.get('seed');
    if (seed !== undefined) {
      requestParams.seed = seed;
    }

    const stopSequences = p.get('stopSequences');
    if (stopSequences !== undefined) {
      requestParams.stop = stopSequences;
    }

    // OpenAI doesn't support topK
    p.warnUnsupported('topK', 'OpenAI does not support the top_k parameter');

    return requestParams;
  });
}

/**
 * Decode OpenAI Chat Completions response to Mirascope types.
 */
export function decodeResponse(
  response: ChatCompletion,
  modelId: OpenAIModelId
): {
  assistantMessage: AssistantMessage;
  finishReason: FinishReason | null;
  usage: Usage | null;
} {
  const choice = response.choices[0];
  /* v8 ignore start - defensive check for empty choices */
  if (!choice) {
    throw new Error('No choices in response');
  }
  /* v8 ignore stop */

  const content = decodeContent(choice.message);

  const assistantMessage: AssistantMessage = {
    role: 'assistant',
    content,
    name: null,
    providerId: 'openai',
    modelId,
    providerModelName: response.model,
    rawMessage: response as unknown as AssistantMessage['rawMessage'],
  };

  const finishReason = decodeFinishReason(choice.finish_reason);

  /* v8 ignore next - usage is always present in API responses */
  const usage = response.usage ? decodeUsage(response.usage) : null;

  return { assistantMessage, finishReason, usage };
}

function decodeContent(
  message: ChatCompletion.Choice['message']
): AssistantContentPart[] {
  const parts: AssistantContentPart[] = [];

  // Handle text content
  if (message.content) {
    const text: Text = { type: 'text', text: message.content };
    parts.push(text);
  }

  // Handle refusal as text (OpenAI returns refusal as separate field)
  /* v8 ignore start - refusals are difficult to trigger reliably */
  if (message.refusal) {
    const text: Text = { type: 'text', text: message.refusal };
    parts.push(text);
  }
  /* v8 ignore end */

  /* v8 ignore start - tool calls not yet implemented */
  // Handle tool calls
  if (message.tool_calls && message.tool_calls.length > 0) {
    throw new FeatureNotSupportedError(
      'tool call decoding',
      'openai',
      null,
      'Tool calls in responses are not yet implemented'
    );
  }
  /* v8 ignore stop */

  return parts;
}

function decodeFinishReason(
  finishReason: ChatCompletion.Choice['finish_reason']
): FinishReason | null {
  switch (finishReason) {
    case 'length':
      return FinishReason.MAX_TOKENS;
    /* v8 ignore start - refusals are difficult to trigger reliably */
    case 'content_filter':
      return FinishReason.REFUSAL;
    /* v8 ignore end */
    case 'stop':
    case 'tool_calls':
    case 'function_call':
      return null; // Normal completion
    /* v8 ignore next 2 - defensive default case */
    default:
      return null;
  }
}

function decodeUsage(usage: NonNullable<ChatCompletion['usage']>): Usage {
  return createUsage({
    inputTokens: usage.prompt_tokens,
    outputTokens: usage.completion_tokens,
    cacheReadTokens: usage.prompt_tokens_details?.cached_tokens ?? 0,
    reasoningTokens: usage.completion_tokens_details?.reasoning_tokens ?? 0,
    raw: usage,
  });
}
