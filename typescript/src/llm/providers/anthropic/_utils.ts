/**
 * Anthropic-specific utilities for encoding requests and decoding responses.
 */

import type {
  Base64ImageSource as AnthropicBase64ImageSource,
  Base64PDFSource,
  ContentBlock,
  DocumentBlockParam,
  ImageBlockParam,
  Message as AnthropicMessage,
  MessageCreateParamsNonStreaming,
  PlainTextSource,
  URLImageSource as AnthropicURLImageSource,
  URLPDFSource,
} from "@anthropic-ai/sdk/resources/messages";

import Anthropic from "@anthropic-ai/sdk";

import type {
  AssistantContentPart,
  Document,
  Image,
  ImageMimeType,
  Text,
  Thought,
  ToolCall,
  UserContentPart,
} from "@/llm/content";
import type { Format } from "@/llm/formatting";
import type { AssistantMessage, Message } from "@/llm/messages";
import type { Params } from "@/llm/models";
import type { ThinkingLevel } from "@/llm/models/thinking-config";
import type { AnthropicModelId } from "@/llm/providers/anthropic/model-id";
import type { Usage } from "@/llm/responses/usage";
import type { ToolSchema, Tools } from "@/llm/tools";

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
} from "@/llm/exceptions";
import { modelName } from "@/llm/providers/anthropic/model-id";
import { ParamHandler, type ProviderErrorMap } from "@/llm/providers/base";
import { FinishReason } from "@/llm/responses/finish-reason";
import { createUsage } from "@/llm/responses/usage";
import { ProviderTool, isProviderTool, isWebSearchTool } from "@/llm/tools";

/**
 * Default max tokens for Anthropic requests.
 */
const DEFAULT_MAX_TOKENS = 4096;

/**
 * Supported Anthropic image MIME types.
 */
type AnthropicImageMimeType =
  | "image/jpeg"
  | "image/png"
  | "image/gif"
  | "image/webp";

/**
 * Convert an ImageMimeType to Anthropic-supported media type.
 *
 * @throws FeatureNotSupportedError for unsupported formats (HEIC, HEIF)
 */
function toAnthropicImageMimeType(
  mimeType: ImageMimeType,
): AnthropicImageMimeType {
  if (
    mimeType === "image/jpeg" ||
    mimeType === "image/png" ||
    mimeType === "image/gif" ||
    mimeType === "image/webp"
  ) {
    return mimeType;
  }
  throw new FeatureNotSupportedError(
    `image format: ${mimeType}`,
    "anthropic",
    null,
    `Anthropic does not support ${mimeType}. Supported formats: JPEG, PNG, GIF, WebP.`,
  );
}

/**
 * Encode an Image content part to Anthropic's ImageBlockParam format.
 */
function encodeImage(image: Image): ImageBlockParam {
  if (image.source.type === "base64_image_source") {
    const source: AnthropicBase64ImageSource = {
      type: "base64",
      media_type: toAnthropicImageMimeType(image.source.mimeType),
      data: image.source.data,
    };
    return { type: "image", source };
  } else {
    const source: AnthropicURLImageSource = {
      type: "url",
      url: image.source.url,
    };
    return { type: "image", source };
  }
}

/**
 * Encode a Document content part to Anthropic's DocumentBlockParam format.
 */
function encodeDocument(doc: Document): DocumentBlockParam {
  const { source } = doc;
  switch (source.type) {
    case "base64_document_source": {
      const pdfSource: Base64PDFSource = {
        type: "base64",
        data: source.data,
        media_type: "application/pdf",
      };
      return { type: "document", source: pdfSource };
    }
    case "text_document_source": {
      const textSource: PlainTextSource = {
        type: "text",
        data: source.data,
        media_type: "text/plain",
      };
      return { type: "document", source: textSource };
    }
    case "url_document_source": {
      const urlSource: URLPDFSource = {
        type: "url",
        url: source.url,
      };
      return { type: "document", source: urlSource };
    }
  }
}

/**
 * Thinking level to budget multiplier mapping.
 * The multiplier is applied to max_tokens to compute the thinking budget.
 */
const THINKING_LEVEL_TO_BUDGET_MULTIPLIER: Record<
  Exclude<ThinkingLevel, "none" | "default">,
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
  maxTokens: number,
): number {
  if (level === "none") {
    return 0; // Disabled
  }
  if (level === "default") {
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
 * Cacheable content types that can have cache_control applied.
 */
const CACHEABLE_CONTENT_TYPES = new Set([
  "text",
  "image",
  "document",
  "tool_output",
  "tool_call",
]);

/**
 * Process content parts from either user or assistant messages.
 * Converts to Anthropic's ContentBlockParam format.
 *
 * @param content - The content parts to process
 * @param encodeThoughtsAsText - Whether to encode thoughts as text
 * @param addCacheControl - Whether to add cache_control to the last cacheable content block
 */
function processContentParts(
  content: readonly (UserContentPart | AssistantContentPart)[],
  encodeThoughtsAsText: boolean = false,
  addCacheControl: boolean = false,
): Anthropic.Messages.ContentBlockParam[] {
  const blocks: Anthropic.Messages.ContentBlockParam[] = [];

  // Find the last cacheable content index if we need to add cache control
  let lastCacheableIndex = -1;
  if (addCacheControl) {
    for (let i = content.length - 1; i >= 0; i--) {
      const part = content[i]!;
      if (CACHEABLE_CONTENT_TYPES.has(part.type)) {
        // Skip empty text
        if (part.type === "text" && !part.text) {
          continue;
        }
        lastCacheableIndex = i;
        break;
      }
    }
  }

  for (let i = 0; i < content.length; i++) {
    const part = content[i]!;
    const shouldAddCache = addCacheControl && i === lastCacheableIndex;

    switch (part.type) {
      case "text":
        blocks.push({
          type: "text",
          text: part.text,
          ...(shouldAddCache && { cache_control: { type: "ephemeral" } }),
        });
        break;

      case "image":
        blocks.push({
          ...encodeImage(part),
          ...(shouldAddCache && { cache_control: { type: "ephemeral" } }),
        });
        break;

      case "audio":
        throw new FeatureNotSupportedError(
          "audio input",
          "anthropic",
          null,
          "Anthropic does not support audio inputs.",
        );

      /* v8 ignore start - tool encoding will be tested via e2e */
      case "tool_call":
        blocks.push({
          type: "tool_use",
          id: part.id,
          name: part.name,
          input: JSON.parse(part.args) as Record<string, unknown>,
          ...(shouldAddCache && { cache_control: { type: "ephemeral" } }),
        });
        break;

      case "tool_output":
        blocks.push({
          type: "tool_result",
          tool_use_id: part.id,
          content:
            typeof part.result === "string"
              ? part.result
              : JSON.stringify(part.result),
          is_error: part.error !== null,
          ...(shouldAddCache && { cache_control: { type: "ephemeral" } }),
        });
        break;
      /* v8 ignore stop */

      case "document":
        blocks.push({
          ...encodeDocument(part),
          ...(shouldAddCache && { cache_control: { type: "ephemeral" } }),
        });
        break;

      /* v8 ignore start - encodeThoughtsAsText will be tested via e2e */
      case "thought":
        // Encode thoughts as text when requested, otherwise drop
        if (encodeThoughtsAsText) {
          blocks.push({ type: "text", text: "**Thinking:** " + part.thought });
        }
        break;
      /* v8 ignore stop */
    }
  }

  return blocks;
}

// ============================================================================
// Content Simplification
// ============================================================================

/**
 * Simplify content to string if only a single text part without cache_control.
 * Anthropic accepts string for simple messages, but not when cache_control is present.
 */
function simplifyContent(
  blocks: Anthropic.Messages.ContentBlockParam[],
): string | Anthropic.Messages.ContentBlockParam[] {
  if (
    blocks.length === 1 &&
    blocks[0] &&
    blocks[0].type === "text" &&
    !("cache_control" in blocks[0] && blocks[0].cache_control)
  ) {
    return blocks[0].text;
  }
  return blocks;
}

// ============================================================================
// Message Encoding
// ============================================================================

/**
 * Encode a single user or assistant message.
 *
 * @param message - The message to encode
 * @param modelId - The model ID for the request
 * @param encodeThoughtsAsText - Whether to encode thoughts as text
 * @param addCacheControl - Whether to add cache_control to the last content block
 */
function encodeMessage(
  message: Message,
  modelId: AnthropicModelId,
  encodeThoughtsAsText: boolean,
  addCacheControl: boolean,
): Anthropic.Messages.MessageParam | null {
  /* v8 ignore next 3 - defensive check: system messages filtered in encodeMessages */
  if (message.role === "system") {
    return null; // System messages are handled separately
  }

  if (message.role === "user") {
    const blocks = processContentParts(
      message.content,
      false, // encodeThoughtsAsText not applicable to user messages
      addCacheControl,
    );
    return {
      role: "user",
      content: simplifyContent(blocks),
    };
  }

  // assistant message
  // Check if we can reuse the raw message (from same provider/model)
  // Can only reuse if not adding cache control and not encoding thoughts as text
  if (
    !addCacheControl &&
    !encodeThoughtsAsText &&
    message.providerId === "anthropic" &&
    message.modelId === modelId &&
    message.rawMessage
  ) {
    // Reuse the serialized message directly
    return message.rawMessage as unknown as Anthropic.Messages.MessageParam;
  }

  // Otherwise, encode from content parts
  const blocks = processContentParts(
    message.content,
    encodeThoughtsAsText,
    addCacheControl,
  );
  return {
    role: "assistant",
    content: simplifyContent(blocks),
  };
}

/**
 * Encode Mirascope messages to Anthropic API format.
 *
 * If the conversation contains assistant messages (indicating multi-turn),
 * adds cache_control to the last content block of the last message.
 *
 * @param messages - The messages to encode
 * @param modelId - The model ID for the request (used to check if raw message can be reused)
 * @param encodeThoughtsAsText - Whether to encode thoughts as text in assistant messages
 */
export function encodeMessages(
  messages: readonly Message[],
  modelId: AnthropicModelId,
  encodeThoughtsAsText: boolean = false,
): {
  system: string | undefined;
  messages: MessageCreateParamsNonStreaming["messages"];
} {
  let system: string | undefined;
  const anthropicMessages: MessageCreateParamsNonStreaming["messages"] = [];

  // Extract system message
  const nonSystemMessages: Message[] = [];
  for (const message of messages) {
    if (message.role === "system") {
      system = message.content.text;
    } else {
      nonSystemMessages.push(message);
    }
  }

  // Detect multi-turn conversations by checking for assistant messages
  const hasAssistantMessage = nonSystemMessages.some(
    (msg) => msg.role === "assistant",
  );

  // Encode messages, adding cache_control to the last message if multi-turn
  for (let i = 0; i < nonSystemMessages.length; i++) {
    const message = nonSystemMessages[i]!;
    const isLast = i === nonSystemMessages.length - 1;
    const addCacheControl = hasAssistantMessage && isLast;

    const encoded = encodeMessage(
      message,
      modelId,
      encodeThoughtsAsText,
      addCacheControl,
    );
    if (encoded) {
      anthropicMessages.push(encoded);
    }
  }

  return { system, messages: anthropicMessages };
}

// ============================================================================
// Tool Encoding
// ============================================================================

/* v8 ignore start - tool encoding will be tested via e2e */
/**
 * Convert a ToolSchema to Anthropic's Tool format.
 */
export function encodeToolSchema(tool: ToolSchema): Anthropic.Messages.Tool {
  return {
    name: tool.name,
    description: tool.description,
    input_schema: {
      type: "object",
      properties: tool.parameters.properties as Record<
        string,
        Anthropic.Messages.Tool.InputSchema
      >,
      required: tool.parameters.required as string[],
    },
  };
}

/**
 * Encode an array of tool schemas to Anthropic's format.
 */
export function encodeTools(
  tools: readonly ToolSchema[],
): Anthropic.Messages.Tool[] {
  return tools.map(encodeToolSchema);
}
/* v8 ignore stop */

/**
 * Build the request parameters for the Anthropic API.
 *
 * This function performs strict param checking - any unhandled params will
 * cause an error to ensure we don't silently ignore user configuration.
 *
 * @param modelId - The model ID to use
 * @param messages - The messages to send
 * @param tools - Optional tools to make available to the model
 * @param format - Optional format for structured output
 * @param params - Optional parameters (temperature, maxTokens, etc.)
 */
export function buildRequestParams(
  modelId: AnthropicModelId,
  messages: readonly Message[],
  tools?: Tools,
  format?: Format | null,
  params: Params = {},
): MessageCreateParamsNonStreaming {
  return ParamHandler.with(params, "anthropic", modelId, (p) => {
    const thinkingConfig = p.get("thinking");
    const encodeThoughtsAsText = thinkingConfig?.encodeThoughtsAsText ?? false;

    const { system, messages: anthropicMessages } = encodeMessages(
      messages,
      modelId,
      encodeThoughtsAsText,
    );

    const maxTokens = p.getOrDefault("maxTokens", DEFAULT_MAX_TOKENS);
    const requestParams: MessageCreateParamsNonStreaming = {
      model: modelName(modelId),
      messages: anthropicMessages,
      max_tokens: maxTokens,
    };

    // Start with the system prompt from messages
    let systemPrompt = system;

    // Collect tools from both explicit tools and format tool
    const allTools: Anthropic.Messages.ToolUnion[] = [];

    /* v8 ignore start - tool encoding will be tested via e2e */
    if (tools !== undefined && tools.length > 0) {
      // Separate regular tools from provider tools
      const regularTools: ToolSchema[] = [];
      for (const tool of tools) {
        // Check for provider tools first (WebSearchTool extends ProviderTool)
        if (isProviderTool(tool)) {
          if (isWebSearchTool(tool)) {
            // Anthropic's web search tool
            allTools.push({
              type: "web_search_20250305",
              name: "web_search",
            });
          } else {
            // Cast needed because TS narrows to never after WebSearchTool check
            const unsupportedTool = tool as ProviderTool;
            throw new FeatureNotSupportedError(
              `Provider tool ${unsupportedTool.name}`,
              "anthropic",
              modelId,
              `Provider tool '${unsupportedTool.name}' is not supported by Anthropic`,
            );
          }
        } else {
          // Regular tool (BaseTool extends ToolSchema)
          regularTools.push(tool as ToolSchema);
        }
      }
      if (regularTools.length > 0) {
        allTools.push(...encodeTools(regularTools));
      }
    }
    /* v8 ignore stop */

    // Handle format-based tool and instructions
    /* v8 ignore start - format encoding will be tested via e2e */
    if (format) {
      // Check mode support
      if (format.mode === "strict") {
        throw new FeatureNotSupportedError(
          "formatting_mode:strict",
          "anthropic",
          modelId,
          "Anthropic standard API does not support strict mode formatting. Use beta API or tool mode.",
        );
      }

      // Add format tool if mode is 'tool'
      if (format.mode === "tool") {
        const formatToolSchema = format.createToolSchema();
        allTools.push(encodeToolSchema(formatToolSchema));

        // Set tool_choice based on whether we have other tools
        if (tools && tools.length > 0) {
          // When we have other tools, use 'any' to require a tool call
          requestParams.tool_choice = { type: "any" };
        } else {
          // When only format tool, force that specific tool
          requestParams.tool_choice = {
            type: "tool",
            name: formatToolSchema.name,
            disable_parallel_tool_use: true,
          };
        }
      }

      // Add formatting instructions to system prompt
      if (format.formattingInstructions) {
        if (systemPrompt) {
          systemPrompt = `${systemPrompt}\n\n${format.formattingInstructions}`;
        } else {
          systemPrompt = format.formattingInstructions;
        }
      }
    }
    /* v8 ignore stop */

    // Set system prompt if we have one (with cache control for prompt caching)
    if (systemPrompt) {
      requestParams.system = [
        {
          type: "text",
          text: systemPrompt,
          cache_control: { type: "ephemeral" },
        },
      ];
    }

    // Set tools if we have any (with cache control on the last tool)
    /* v8 ignore start - tool encoding will be tested via e2e */
    if (allTools.length > 0) {
      // Add cache control to the last tool for prompt caching
      const lastTool = allTools[allTools.length - 1]!;
      (
        lastTool as Anthropic.Messages.Tool & { cache_control?: object }
      ).cache_control = { type: "ephemeral" };
      requestParams.tools = allTools;
    }
    /* v8 ignore stop */

    const temperature = p.get("temperature");
    const topP = p.get("topP");

    // Anthropic doesn't allow both temperature and topP together
    if (temperature !== undefined && topP !== undefined) {
      throw new FeatureNotSupportedError(
        "temperature + topP",
        "anthropic",
        modelId,
        "Anthropic does not allow both temperature and top_p to be specified together",
      );
    }

    if (temperature !== undefined) {
      requestParams.temperature = temperature;
    }

    if (topP !== undefined) {
      requestParams.top_p = topP;
    }

    const topK = p.get("topK");
    if (topK !== undefined) {
      requestParams.top_k = topK;
    }

    const stopSequences = p.get("stopSequences");
    if (stopSequences !== undefined) {
      requestParams.stop_sequences = stopSequences;
    }

    // Anthropic doesn't support seed
    p.warnUnsupported("seed", "Anthropic does not support the seed parameter");

    if (thinkingConfig) {
      const budget = computeThinkingBudget(thinkingConfig.level, maxTokens);
      if (budget === 0) {
        requestParams.thinking = { type: "disabled" };
      } else if (budget > 0) {
        requestParams.thinking = { type: "enabled", budget_tokens: budget };
      }
      // If budget === -1, don't set thinking (use provider default)
    }

    return requestParams;
  });
}

/**
 * Serialize content blocks for storage in rawMessage.
 *
 * This mirrors Python's `part.model_dump()` pattern for round-tripping.
 */
function serializeContentBlocks(
  content: ContentBlock[],
): Record<string, unknown>[] {
  return content.map((block) => {
    // Copy all non-undefined properties from the block
    const serialized: Record<string, unknown> = {};
    for (const [key, value] of Object.entries(block)) {
      if (value !== undefined) {
        serialized[key] = value;
      }
    }
    return serialized;
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
  includeThoughts: boolean = false,
): {
  assistantMessage: AssistantMessage;
  finishReason: FinishReason | null;
  usage: Usage | null;
} {
  const content = decodeContent(response.content, includeThoughts);

  // Store serialized message for round-tripping in resume operations.
  // This format matches what Anthropic expects as MessageParam.
  const serializedRawMessage = {
    role: response.role,
    content: serializeContentBlocks(response.content),
  };

  const assistantMessage: AssistantMessage = {
    role: "assistant",
    content,
    name: null,
    providerId: "anthropic",
    modelId,
    providerModelName: modelName(modelId),
    rawMessage:
      serializedRawMessage as unknown as AssistantMessage["rawMessage"],
  };

  const finishReason = decodeStopReason(response.stop_reason);
  const usage = decodeUsage(response.usage);

  return { assistantMessage, finishReason, usage };
}

function decodeContent(
  content: ContentBlock[],
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
      /* v8 ignore start - redacted_thinking can't be reliably triggered in tests */
    } else if (block.type === "redacted_thinking") {
      // Skip redacted thinking blocks - they contain encrypted thinking
      // that cannot be decoded
      continue;
      /* v8 ignore stop */
      /* v8 ignore start - tool decoding will be tested via e2e */
    } else if (block.type === "tool_use") {
      const toolCall: ToolCall = {
        type: "tool_call",
        id: block.id,
        name: block.name,
        args: JSON.stringify(block.input),
      };
      parts.push(toolCall);
    } else if (
      block.type === "server_tool_use" ||
      block.type === "web_search_tool_result"
    ) {
      // Skip server-side tool content - preserved in rawMessage
      continue;
      /* v8 ignore stop */
      /* v8 ignore start - defensive unknown block handling */
    } else {
      // Unknown block type - be strict so we know what we're missing
      const unknownBlock = block as { type: string };
      throw new FeatureNotSupportedError(
        `unknown block type: ${unknownBlock.type}`,
        "anthropic",
        null,
        `Unknown content block type '${unknownBlock.type}' in response is not yet implemented`,
      );
    }
    /* v8 ignore stop */
  }

  return parts;
}

function decodeStopReason(
  stopReason: AnthropicMessage["stop_reason"],
): FinishReason | null {
  switch (stopReason) {
    case "max_tokens":
      return FinishReason.MAX_TOKENS;
    case "end_turn":
    case "stop_sequence":
    case "tool_use":
      return null; // Normal completion
    /* v8 ignore next 2 - defensive default case */
    default:
      return null;
  }
}

export function decodeUsage(usage: AnthropicMessage["usage"]): Usage {
  return createUsage({
    inputTokens: usage.input_tokens,
    outputTokens: usage.output_tokens,
    /* v8 ignore next 2 - cache tokens only present with caching enabled, will add tests later */
    cacheReadTokens: usage.cache_read_input_tokens ?? 0,
    cacheWriteTokens: usage.cache_creation_input_tokens ?? 0,
    raw: usage,
  });
}
