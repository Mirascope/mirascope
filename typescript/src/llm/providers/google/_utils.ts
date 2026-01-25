/**
 * Google-specific utilities for encoding requests and decoding responses.
 */

import type {
  Content,
  ContentUnion,
  GenerateContentConfig,
  GenerateContentParameters,
  GenerateContentResponse,
  Part,
  FinishReason as GoogleFinishReasonType,
} from '@google/genai';
import { ApiError, FinishReason as GoogleFinishReason } from '@google/genai';

import type {
  AssistantContentPart,
  Text,
  UserContentPart,
} from '@/llm/content';
import {
  APIError,
  AuthenticationError,
  BadRequestError,
  FeatureNotSupportedError,
  NotFoundError,
  PermissionError,
  RateLimitError,
  ServerError,
} from '@/llm/exceptions';
import type { AssistantMessage, Message } from '@/llm/messages';
import type { Params } from '@/llm/models';
import { ParamHandler, type ProviderErrorMap } from '@/llm/providers/base';
import type { GoogleModelId } from '@/llm/providers/google/model-id';
import { modelName } from '@/llm/providers/google/model-id';
import { FinishReason } from '@/llm/responses/finish-reason';
import type { Usage } from '@/llm/responses/usage';
import { createUsage } from '@/llm/responses/usage';

/**
 * Error mapping from Google SDK exceptions to Mirascope error types.
 * Google SDK uses a single ApiError class with status codes.
 */
export const GOOGLE_ERROR_MAP: ProviderErrorMap = [[ApiError, APIError]];

/**
 * Map Google error status codes to specific Mirascope error types.
 *
 * @param status - HTTP status code from the Google API error
 * @returns The appropriate Mirascope error class for this status code
 */
export function mapGoogleErrorByStatus(status: number): typeof APIError {
  switch (status) {
    case 401:
      return AuthenticationError;
    case 403:
      return PermissionError;
    case 404:
      return NotFoundError;
    case 429:
      return RateLimitError;
    case 400:
    case 422:
      return BadRequestError;
    default:
      if (status >= 500) {
        return ServerError;
      }
      return APIError;
  }
}

// ============================================================================
// Content Part Processing
// ============================================================================

/**
 * Process content parts from either user or assistant messages.
 * Converts to Google's Part format.
 */
function processContentParts(
  content: readonly (UserContentPart | AssistantContentPart)[]
): Part[] {
  const parts: Part[] = [];

  for (const part of content) {
    switch (part.type) {
      case 'text':
        parts.push({ text: part.text });
        break;

      /* v8 ignore start - content types not yet implemented */
      case 'image':
        throw new FeatureNotSupportedError(
          'image content encoding',
          'google',
          null,
          'Image content is not yet implemented'
        );

      case 'audio':
        throw new FeatureNotSupportedError(
          'audio content encoding',
          'google',
          null,
          'Audio content is not yet implemented'
        );

      case 'document':
        throw new FeatureNotSupportedError(
          'document content encoding',
          'google',
          null,
          'Document content is not yet implemented'
        );

      case 'tool_output':
        throw new FeatureNotSupportedError(
          'tool output encoding',
          'google',
          null,
          'Tool outputs are not yet implemented'
        );

      case 'tool_call':
        throw new FeatureNotSupportedError(
          'tool call encoding',
          'google',
          null,
          'Tool calls are not yet implemented'
        );

      case 'thought':
        throw new FeatureNotSupportedError(
          'thought encoding',
          'google',
          null,
          'Thought content is not yet implemented'
        );
      /* v8 ignore stop */
    }
  }

  return parts;
}

// ============================================================================
// Message Encoding
// ============================================================================

/**
 * Encode Mirascope messages to Google API format.
 *
 * Converts the unified Mirascope message format to Google's Content array format.
 * System messages are extracted separately as Google uses `systemInstruction`.
 * Assistant messages are mapped to the 'model' role.
 */
export function encodeMessages(messages: readonly Message[]): {
  systemInstruction: ContentUnion | undefined;
  contents: Content[];
} {
  let systemInstruction: ContentUnion | undefined;
  const contents: Content[] = [];

  for (const message of messages) {
    if (message.role === 'system') {
      systemInstruction = message.content.text;
    } else if (message.role === 'user') {
      contents.push({
        role: 'user',
        parts: processContentParts(message.content),
      });
    } else if (message.role === 'assistant') {
      contents.push({
        role: 'model',
        parts: processContentParts(message.content),
      });
    }
  }

  return { systemInstruction, contents };
}

/**
 * Build the request parameters for the Google API.
 *
 * This function performs strict param checking - any unhandled params will
 * cause an error to ensure we don't silently ignore user configuration.
 */
export function buildRequestParams(
  modelId: GoogleModelId,
  messages: readonly Message[],
  params: Params = {}
): GenerateContentParameters {
  const { systemInstruction, contents } = encodeMessages(messages);

  return ParamHandler.with(params, 'google', modelId, (p) => {
    const config: GenerateContentConfig = {
      maxOutputTokens: p.getOrDefault('maxTokens', 8192),
    };

    if (systemInstruction) {
      config.systemInstruction = systemInstruction;
    }

    const temperature = p.get('temperature');
    if (temperature !== undefined) {
      config.temperature = temperature;
    }

    const topP = p.get('topP');
    if (topP !== undefined) {
      config.topP = topP;
    }

    const topK = p.get('topK');
    if (topK !== undefined) {
      config.topK = topK;
    }

    const stopSequences = p.get('stopSequences');
    if (stopSequences !== undefined) {
      config.stopSequences = stopSequences;
    }

    const seed = p.get('seed');
    if (seed !== undefined) {
      config.seed = seed;
    }

    // Thinking not yet implemented
    p.warnNotImplemented('thinking', 'thinking config');

    return {
      model: modelName(modelId),
      contents,
      config,
    };
  });
}

/**
 * Decode Google API response to Mirascope types.
 *
 * Extracts the assistant message content, finish reason, and usage information
 * from the Google GenerateContentResponse.
 *
 * @param response - Raw response from Google's generateContent API
 * @param modelId - The model ID used for the request
 * @returns Decoded assistant message, finish reason, and usage information
 */
export function decodeResponse(
  response: GenerateContentResponse,
  modelId: GoogleModelId
): {
  assistantMessage: AssistantMessage;
  finishReason: FinishReason | null;
  usage: Usage | null;
} {
  const candidate = response.candidates?.[0];
  /* v8 ignore next - defensive fallback for missing parts */
  const content = candidate?.content?.parts ?? [];
  const decodedContent = decodeContent(content);

  const assistantMessage: AssistantMessage = {
    role: 'assistant',
    content: decodedContent,
    name: null,
    providerId: 'google',
    modelId,
    /* v8 ignore next - modelVersion always present in practice */
    providerModelName: response.modelVersion ?? modelName(modelId),
    rawMessage: response as unknown as AssistantMessage['rawMessage'],
  };

  const finishReason = decodeFinishReason(candidate?.finishReason);
  const usage = decodeUsage(response);

  return { assistantMessage, finishReason, usage };
}

/**
 * Decode Google response parts to Mirascope content format.
 *
 * @param parts - Array of Google Part objects from the response
 * @returns Array of Mirascope AssistantContentPart objects
 * @throws FeatureNotSupportedError for unsupported part types (function_call, thought)
 */
function decodeContent(parts: Part[]): AssistantContentPart[] {
  const content: AssistantContentPart[] = [];

  for (const part of parts) {
    if (part.text !== undefined) {
      const text: Text = { type: 'text', text: part.text };
      content.push(text);
      /* v8 ignore start - content types not yet implemented */
    } else if (part.functionCall) {
      throw new FeatureNotSupportedError(
        'function call decoding',
        'google',
        null,
        'Function call blocks in responses are not yet implemented'
      );
    } else if (part.thought) {
      throw new FeatureNotSupportedError(
        'thought decoding',
        'google',
        null,
        'Thought blocks in responses are not yet implemented'
      );
    } else {
      // Unknown part type - be strict so we know what we're missing
      const partKeys = Object.keys(part).filter(
        (k) => part[k as keyof Part] !== undefined
      );
      throw new FeatureNotSupportedError(
        `unknown part type: ${partKeys.join(', ')}`,
        'google',
        null,
        `Unknown content part in response is not yet implemented`
      );
    }
    /* v8 ignore stop */
  }

  return content;
}

/**
 * Convert Google finish reason to Mirascope FinishReason.
 *
 * Maps Google's finish reasons to the unified Mirascope format:
 * - MAX_TOKENS → FinishReason.MAX_TOKENS
 * - SAFETY, RECITATION, BLOCKLIST, etc. → FinishReason.REFUSAL
 * - STOP or undefined → null (normal completion)
 *
 * @param finishReason - Google finish reason from the response candidate
 * @returns Mirascope FinishReason or null for normal completion
 */
function decodeFinishReason(
  finishReason: GoogleFinishReasonType | undefined
): FinishReason | null {
  switch (finishReason) {
    case GoogleFinishReason.MAX_TOKENS:
      return FinishReason.MAX_TOKENS;
    /* v8 ignore next 6 - refusal reasons can't be reliably triggered in e2e tests */
    case GoogleFinishReason.SAFETY:
    case GoogleFinishReason.RECITATION:
    case GoogleFinishReason.BLOCKLIST:
    case GoogleFinishReason.PROHIBITED_CONTENT:
    case GoogleFinishReason.SPII:
      return FinishReason.REFUSAL;
    case GoogleFinishReason.STOP:
    case undefined:
      return null; // Normal completion
    /* v8 ignore next 2 - defensive default case */
    default:
      return null;
  }
}

/**
 * Extract usage information from the Google response.
 *
 * Maps Google's usage metadata to the unified Mirascope Usage format:
 * - promptTokenCount → inputTokens
 * - candidatesTokenCount + thoughtsTokenCount → outputTokens
 * - cachedContentTokenCount → cacheReadTokens
 * - thoughtsTokenCount → reasoningTokens
 *
 * @param response - Raw Google API response
 * @returns Mirascope Usage object or null if no metadata available
 */
function decodeUsage(response: GenerateContentResponse): Usage | null {
  const metadata = response.usageMetadata;
  /* v8 ignore next 3 - defensive null check */
  if (!metadata) {
    return null;
  }

  /* v8 ignore start - token counts always present in practice, fallbacks are defensive */
  return createUsage({
    inputTokens: metadata.promptTokenCount ?? 0,
    outputTokens:
      (metadata.candidatesTokenCount ?? 0) + (metadata.thoughtsTokenCount ?? 0),
    cacheReadTokens: metadata.cachedContentTokenCount ?? 0,
    reasoningTokens: metadata.thoughtsTokenCount ?? 0,
    raw: metadata,
  });
  /* v8 ignore stop */
}
