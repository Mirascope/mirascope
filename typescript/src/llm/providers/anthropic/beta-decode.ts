/**
 * Beta Anthropic response decoding utilities.
 *
 * Handles BetaMessage type which has additional stop reasons and content types
 * compared to the standard Message type.
 */

import type {
  BetaContentBlock,
  BetaMessage,
  BetaStopReason,
  BetaUsage,
} from "@anthropic-ai/sdk/resources/beta/messages/messages";

import type { AssistantContentPart, Text, Thought } from "@/llm/content";
import type { AssistantMessage } from "@/llm/messages";
import type { AnthropicModelId } from "@/llm/providers/anthropic/model-id";
import type { Usage } from "@/llm/responses/usage";

import { FeatureNotSupportedError } from "@/llm/exceptions";
import { FinishReason } from "@/llm/responses/finish-reason";
import { createUsage } from "@/llm/responses/usage";

/**
 * Decode Beta Anthropic response to Mirascope types.
 *
 * Similar to standard decodeResponse but handles BetaMessage type
 * which has additional stop reasons (refusal, etc.) and content types.
 *
 * @param response - The raw BetaMessage from Anthropic API
 * @param modelId - The model ID used for the request
 * @param includeThoughts - Whether to include thinking blocks in the response (default: false)
 */
export function betaDecodeResponse(
  response: BetaMessage,
  modelId: AnthropicModelId,
  includeThoughts: boolean = false,
): {
  assistantMessage: AssistantMessage;
  finishReason: FinishReason | null;
  usage: Usage | null;
} {
  const content = betaDecodeContent(response.content, includeThoughts);

  const assistantMessage: AssistantMessage = {
    role: "assistant",
    content,
    name: null,
    // Note: providerId is 'anthropic' (not 'anthropic-beta') to match Python SDK
    providerId: "anthropic",
    modelId,
    providerModelName: response.model,
    rawMessage: response as unknown as AssistantMessage["rawMessage"],
  };

  const finishReason = betaDecodeStopReason(response.stop_reason);
  const usage = betaDecodeUsage(response.usage);

  return { assistantMessage, finishReason, usage };
}

/**
 * Decode beta content blocks to Mirascope content parts.
 *
 * @param content - The content blocks from the beta response
 * @param includeThoughts - Whether to include thinking blocks
 */
function betaDecodeContent(
  content: BetaContentBlock[],
  includeThoughts: boolean,
): AssistantContentPart[] {
  const parts: AssistantContentPart[] = [];

  for (const block of content) {
    if (block.type === "text") {
      const text: Text = { type: "text", text: block.text };
      parts.push(text);
    } else if (block.type === "thinking") {
      if (includeThoughts) {
        const thought: Thought = { type: "thought", thought: block.thinking };
        parts.push(thought);
      }
    } else if (block.type === "redacted_thinking") {
      // Skip redacted thinking blocks - they contain encrypted thinking
      // that cannot be decoded
      continue;
      /* v8 ignore start - content types not yet implemented */
    } else if (block.type === "tool_use") {
      throw new FeatureNotSupportedError(
        "tool use decoding",
        "anthropic",
        null,
        "Tool use blocks in responses are not yet implemented",
      );
    } else {
      // Unknown block type - be strict so we know what we're missing
      throw new FeatureNotSupportedError(
        `unknown block type: ${block.type}`,
        "anthropic",
        null,
        `Unknown content block type '${block.type}' in beta response is not yet implemented`,
      );
    }
    /* v8 ignore stop */
  }

  return parts;
}

/**
 * Decode beta stop reason to Mirascope FinishReason.
 *
 * Beta API has additional stop reasons compared to standard:
 * - 'refusal': Model refused to generate content
 * - 'pause_turn': Conversation paused (not yet supported)
 * - 'model_context_window_exceeded': Context too long (not yet supported)
 */
function betaDecodeStopReason(
  stopReason: BetaStopReason | null,
): FinishReason | null {
  switch (stopReason) {
    case "max_tokens":
      return FinishReason.MAX_TOKENS;
    case "refusal":
      return FinishReason.REFUSAL;
    case "end_turn":
    case "stop_sequence":
    case "tool_use":
    case "pause_turn":
      return null; // Normal completion
    /* v8 ignore next 2 - defensive default case */
    default:
      return null;
  }
}

/**
 * Decode beta usage to Mirascope Usage.
 *
 * Beta usage has additional fields (cache_creation, server_tool_use)
 * but we only use the common fields for now.
 */
function betaDecodeUsage(usage: BetaUsage): Usage {
  return createUsage({
    inputTokens: usage.input_tokens,
    outputTokens: usage.output_tokens,
    cacheReadTokens: usage.cache_read_input_tokens ?? 0,
    cacheWriteTokens: usage.cache_creation_input_tokens ?? 0,
    raw: usage,
  });
}
