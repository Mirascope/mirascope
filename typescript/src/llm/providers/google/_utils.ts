/**
 * Google-specific utilities for encoding requests and decoding responses.
 */

import type {
  Blob as GoogleBlob,
  Content,
  ContentUnion,
  GenerateContentConfig,
  GenerateContentParameters,
  GenerateContentResponse,
  Part,
  ThinkingConfig as GoogleThinkingConfig,
  FinishReason as GoogleFinishReasonType,
} from "@google/genai";

import {
  ApiError,
  FinishReason as GoogleFinishReason,
  ThinkingLevel as GoogleThinkingLevel,
} from "@google/genai";

import type {
  AssistantContentPart,
  Audio,
  Document,
  Image,
  Text,
  Thought,
  ToolCall,
  UserContentPart,
} from "@/llm/content";
import type { Format } from "@/llm/formatting";
import type { AssistantMessage, Message } from "@/llm/messages";
import type { Params } from "@/llm/models";
import type {
  ThinkingConfig,
  ThinkingLevel,
} from "@/llm/models/thinking-config";
import type { GoogleModelId } from "@/llm/providers/google/model-id";
import type { Usage } from "@/llm/responses/usage";
import type { ToolSchema, Tools } from "@/llm/tools";

import {
  APIError,
  AuthenticationError,
  BadRequestError,
  FeatureNotSupportedError,
  NotFoundError,
  PermissionError,
  RateLimitError,
  ServerError,
} from "@/llm/exceptions";
import { ParamHandler, type ProviderErrorMap } from "@/llm/providers/base";
import { modelName } from "@/llm/providers/google/model-id";
import { FinishReason } from "@/llm/responses/finish-reason";
import { createUsage } from "@/llm/responses/usage";
import { ProviderTool, isProviderTool, isWebSearchTool } from "@/llm/tools";

/**
 * Default tool ID for Google function calls when no ID is provided.
 * Google doesn't always provide tool IDs, so we use this as a fallback.
 */
const UNKNOWN_TOOL_ID = "google_unknown_tool_id";

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
 * Encode an Image content part to Google's Part format.
 * Google requires inline data (base64), not URL references.
 *
 * @throws FeatureNotSupportedError if the image uses a URL source
 */
function encodeImage(image: Image): Part {
  if (image.source.type === "url_image_source") {
    throw new FeatureNotSupportedError(
      "url_image_source",
      "google",
      null,
      "Google does not support URL-referenced images. Try `Image.download(...)` instead.",
    );
  }
  const inlineData: GoogleBlob = {
    data: image.source.data,
    mimeType: image.source.mimeType,
  };
  return { inlineData };
}

/**
 * Encode an Audio content part to Google's Part format.
 */
function encodeAudio(audio: Audio): Part {
  const inlineData: GoogleBlob = {
    data: audio.source.data,
    mimeType: audio.source.mimeType,
  };
  return { inlineData };
}

/**
 * Encode a Document content part to Google's Part format.
 * Google requires inline data (base64), not URL references.
 *
 * @throws FeatureNotSupportedError if the document uses a URL source
 */
function encodeDocument(doc: Document): Part {
  const { source } = doc;
  switch (source.type) {
    case "base64_document_source": {
      const inlineData: GoogleBlob = {
        data: source.data,
        mimeType: source.mediaType,
      };
      return { inlineData };
    }
    case "text_document_source": {
      // Google expects base64 inline data, so encode the text
      const inlineData: GoogleBlob = {
        data: btoa(source.data),
        mimeType: source.mediaType,
      };
      return { inlineData };
    }
    case "url_document_source":
      throw new FeatureNotSupportedError(
        "url_document_source",
        "google",
        null,
        "Google does not support URL-referenced documents. Use `Document.fromFile(...)` or `Document.fromBytes(...)` instead.",
      );
  }
}

/**
 * Process content parts from either user or assistant messages.
 * Converts to Google's Part format.
 *
 * @param content - The content parts to process
 * @param encodeThoughtsAsText - Whether to encode thoughts as text
 */
function processContentParts(
  content: readonly (UserContentPart | AssistantContentPart)[],
  encodeThoughtsAsText: boolean = false,
): Part[] {
  const parts: Part[] = [];

  for (const part of content) {
    switch (part.type) {
      case "text":
        parts.push({ text: part.text });
        break;

      case "image":
        parts.push(encodeImage(part));
        break;

      case "audio":
        parts.push(encodeAudio(part));
        break;

      /* v8 ignore start - tool encoding will be tested via e2e */
      case "tool_call":
        parts.push({
          functionCall: {
            name: part.name,
            args: JSON.parse(part.args) as Record<string, unknown>,
          },
        });
        break;

      case "tool_output": {
        // Google expects the result to be an object
        const response =
          typeof part.result === "string"
            ? { result: part.result }
            : (part.result as Record<string, unknown>);
        parts.push({
          functionResponse: {
            name: part.name,
            response,
          },
        });
        break;
      }
      /* v8 ignore stop */

      case "document":
        parts.push(encodeDocument(part));
        break;

      /* v8 ignore start - thought encoding will be tested via e2e */

      case "thought":
        // Encode thoughts as text when requested, otherwise drop
        if (encodeThoughtsAsText) {
          parts.push({ text: "**Thinking:** " + part.thought });
        }
        break;
      /* v8 ignore stop */
    }
  }

  return parts;
}

// ============================================================================
// Message Encoding
// ============================================================================

/**
 * Default max tokens for Google requests.
 */
const DEFAULT_MAX_TOKENS = 8192;

/**
 * Thinking level to budget multiplier for Gemini 2.5 models.
 */
const THINKING_LEVEL_TO_BUDGET_MULTIPLIER: Record<
  Exclude<ThinkingLevel, "none" | "default">,
  number
> = {
  minimal: 0.1,
  low: 0.2,
  medium: 0.4,
  high: 0.6,
  max: 0.8,
};

/**
 * Thinking level mapping for Gemini 3 Pro (only LOW or HIGH supported).
 */
const THINKING_LEVEL_FOR_GEMINI_3_PRO: Record<
  ThinkingLevel,
  GoogleThinkingLevel
> = {
  default: GoogleThinkingLevel.THINKING_LEVEL_UNSPECIFIED,
  none: GoogleThinkingLevel.LOW,
  minimal: GoogleThinkingLevel.LOW,
  low: GoogleThinkingLevel.LOW,
  medium: GoogleThinkingLevel.HIGH,
  high: GoogleThinkingLevel.HIGH,
  max: GoogleThinkingLevel.HIGH,
};

/**
 * Thinking level mapping for Gemini 3 Flash (MINIMAL, LOW, MEDIUM, HIGH supported).
 */
const THINKING_LEVEL_FOR_GEMINI_3_FLASH: Record<
  ThinkingLevel,
  GoogleThinkingLevel
> = {
  default: GoogleThinkingLevel.THINKING_LEVEL_UNSPECIFIED,
  none: GoogleThinkingLevel.MINIMAL,
  minimal: GoogleThinkingLevel.MINIMAL,
  low: GoogleThinkingLevel.LOW,
  medium: GoogleThinkingLevel.MEDIUM,
  high: GoogleThinkingLevel.HIGH,
  max: GoogleThinkingLevel.HIGH,
};

/**
 * Compute Google thinking configuration based on model version.
 *
 * @param thinkingConfig - The ThinkingConfig from params
 * @param maxTokens - Max output tokens (used to compute budget for 2.5 models)
 * @param modelId - The Google model ID to determine version
 * @returns GoogleThinkingConfig with appropriate settings for the model
 */
export function computeGoogleThinkingConfig(
  thinkingConfig: ThinkingConfig,
  maxTokens: number,
  modelId: GoogleModelId,
): GoogleThinkingConfig {
  const level = thinkingConfig.level;
  const result: GoogleThinkingConfig = {};

  // Set includeThoughts if specified
  if (thinkingConfig.includeThoughts !== undefined) {
    result.includeThoughts = thinkingConfig.includeThoughts;
  }

  // Determine thinking config based on model
  if (
    modelId.includes("gemini-3-flash") ||
    modelId.includes("gemini-3.0-flash")
  ) {
    result.thinkingLevel = THINKING_LEVEL_FOR_GEMINI_3_FLASH[level];
  } else if (
    modelId.includes("gemini-3-pro") ||
    modelId.includes("gemini-3.0-pro")
  ) {
    result.thinkingLevel = THINKING_LEVEL_FOR_GEMINI_3_PRO[level];
  } else {
    // Gemini 2.5 and earlier use thinking_budget
    if (level === "default") {
      result.thinkingBudget = -1; // Dynamic/automatic budget
    } else if (level === "none") {
      result.thinkingBudget = 0; // Disable thinking
    } else {
      const multiplier = THINKING_LEVEL_TO_BUDGET_MULTIPLIER[level];
      result.thinkingBudget = Math.floor(multiplier * maxTokens);
    }
  }

  return result;
}

// ============================================================================
// Tool Encoding
// ============================================================================

/* v8 ignore start - tool encoding will be tested via e2e */
/**
 * Convert a ToolSchema to Google's FunctionDeclaration format.
 */
export function encodeToolSchema(tool: ToolSchema): {
  name: string;
  description: string;
  parametersJsonSchema: unknown;
} {
  return {
    name: tool.name,
    description: tool.description,
    // Use parametersJsonSchema for raw JSON schema compatibility
    parametersJsonSchema: {
      type: "object",
      properties: tool.parameters.properties,
      required: tool.parameters.required,
    },
  };
}

/**
 * Encode an array of tool schemas to Google's format.
 * Google wraps all function declarations in a single Tool object.
 */
export function encodeTools(
  tools: readonly ToolSchema[],
): NonNullable<GenerateContentConfig["tools"]> {
  return [
    {
      functionDeclarations: tools.map(encodeToolSchema),
    },
  ];
}
/* v8 ignore stop */

/**
 * Encode Mirascope messages to Google API format.
 *
 * Converts the unified Mirascope message format to Google's Content array format.
 * System messages are extracted separately as Google uses `systemInstruction`.
 * Assistant messages are mapped to the 'model' role.
 *
 * @param messages - The messages to encode
 * @param modelId - The model ID for the request (used to check if raw message can be reused)
 * @param encodeThoughtsAsText - Whether to encode thoughts as text in assistant messages
 */
export function encodeMessages(
  messages: readonly Message[],
  modelId: GoogleModelId,
  encodeThoughtsAsText: boolean = false,
): {
  systemInstruction: ContentUnion | undefined;
  contents: Content[];
} {
  let systemInstruction: ContentUnion | undefined;
  const contents: Content[] = [];

  for (const message of messages) {
    if (message.role === "system") {
      systemInstruction = message.content.text;
    } else if (message.role === "user") {
      contents.push({
        role: "user",
        parts: processContentParts(message.content),
      });
    } else if (message.role === "assistant") {
      // Check if we can reuse the raw message (from same provider/model)
      if (
        message.providerId === "google" &&
        message.modelId === modelId &&
        message.rawMessage &&
        !encodeThoughtsAsText
      ) {
        // Reuse the serialized content directly
        contents.push(message.rawMessage as Content);
      } else {
        // Otherwise, encode from content parts
        contents.push({
          role: "model",
          parts: processContentParts(message.content, encodeThoughtsAsText),
        });
      }
    }
  }

  return { systemInstruction, contents };
}

/**
 * Build the request parameters for the Google API.
 *
 * This function performs strict param checking - any unhandled params will
 * cause an error to ensure we don't silently ignore user configuration.
 *
 * @param modelId - The model ID to use
 * @param messages - The messages to send
 * @param params - Optional parameters (temperature, maxTokens, etc.)
 * @param tools - Optional tools to make available to the model
 */
export function buildRequestParams(
  modelId: GoogleModelId,
  messages: readonly Message[],
  tools?: Tools,
  format?: Format | null,
  params: Params = {},
): GenerateContentParameters {
  return ParamHandler.with(params, "google", modelId, (p) => {
    const thinkingConfig = p.get("thinking");
    const encodeThoughtsAsText = thinkingConfig?.encodeThoughtsAsText ?? false;

    const { systemInstruction, contents } = encodeMessages(
      messages,
      modelId,
      encodeThoughtsAsText,
    );

    const maxTokens = p.getOrDefault("maxTokens", DEFAULT_MAX_TOKENS);
    const config: GenerateContentConfig = {
      maxOutputTokens: maxTokens,
    };

    // Start with system instruction from messages
    let systemPrompt = systemInstruction;

    /* v8 ignore start - tool encoding will be tested via e2e */
    // Collect all tools (explicit + format tool)
    const regularTools: ToolSchema[] = [];
    let hasWebSearch = false;

    if (tools !== undefined && tools.length > 0) {
      // Separate regular tools from provider tools
      for (const tool of tools) {
        // Check for provider tools first (WebSearchTool extends ProviderTool)
        if (isProviderTool(tool)) {
          if (isWebSearchTool(tool)) {
            hasWebSearch = true;
          } else {
            // Cast needed because TS narrows to never after WebSearchTool check
            const unsupportedTool = tool as ProviderTool;
            throw new FeatureNotSupportedError(
              `Provider tool ${unsupportedTool.name}`,
              "google",
              modelId,
              `Provider tool '${unsupportedTool.name}' is not supported by Google`,
            );
          }
        } else {
          // Regular tool (BaseTool extends ToolSchema)
          regularTools.push(tool as ToolSchema);
        }
      }
    }

    // Add format tool if mode is 'tool'
    if (format) {
      if (format.mode === "tool") {
        const formatToolSchema = format.createToolSchema();
        regularTools.push(formatToolSchema);
      }
      if (format.formattingInstructions) {
        systemPrompt = systemPrompt
          ? `${format.formattingInstructions}\n\n${systemPrompt}`
          : format.formattingInstructions;
      }
    }

    const googleTools: NonNullable<GenerateContentConfig["tools"]> = [];

    if (regularTools.length > 0) {
      googleTools.push(...encodeTools(regularTools));
    }

    if (hasWebSearch) {
      googleTools.push({ googleSearch: {} });
    }

    if (googleTools.length > 0) {
      config.tools = googleTools;
    }
    /* v8 ignore stop */

    if (systemPrompt) {
      config.systemInstruction = systemPrompt;
    }

    const temperature = p.get("temperature");
    if (temperature !== undefined) {
      config.temperature = temperature;
    }

    const topP = p.get("topP");
    if (topP !== undefined) {
      config.topP = topP;
    }

    const topK = p.get("topK");
    if (topK !== undefined) {
      config.topK = topK;
    }

    const stopSequences = p.get("stopSequences");
    if (stopSequences !== undefined) {
      config.stopSequences = stopSequences;
    }

    const seed = p.get("seed");
    if (seed !== undefined) {
      config.seed = seed;
    }

    if (thinkingConfig) {
      config.thinkingConfig = computeGoogleThinkingConfig(
        thinkingConfig,
        maxTokens,
        modelId,
      );
    }

    return {
      model: modelName(modelId),
      contents,
      config,
    };
  });
}

/**
 * Serialize a Content object for storage in rawMessage.
 *
 * This mirrors Python's `content.model_dump()` pattern for round-tripping.
 */
function serializeContent(
  content: Content | undefined,
): Record<string, unknown> {
  /* v8 ignore start - defensive fallback for missing content */
  if (!content) {
    return { role: "model", parts: [] };
  }
  /* v8 ignore stop */
  // Copy all non-undefined properties
  const serialized: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(content)) {
    if (value !== undefined) {
      serialized[key] = value;
    }
  }
  return serialized;
}

/**
 * Decode Google API response to Mirascope types.
 *
 * Extracts the assistant message content, finish reason, and usage information
 * from the Google GenerateContentResponse.
 *
 * @param response - Raw response from Google's generateContent API
 * @param modelId - The model ID used for the request
 * @param includeThoughts - Whether to include thinking blocks in the response (default: false)
 * @returns Decoded assistant message, finish reason, and usage information
 */
export function decodeResponse(
  response: GenerateContentResponse,
  modelId: GoogleModelId,
  includeThoughts: boolean = false,
): {
  assistantMessage: AssistantMessage;
  finishReason: FinishReason | null;
  usage: Usage | null;
} {
  const candidate = response.candidates?.[0];
  /* v8 ignore next - defensive fallback for missing parts */
  const content = candidate?.content?.parts ?? [];
  const decodedContent = decodeContent(content, includeThoughts);

  // Store serialized candidate content for round-tripping in resume operations.
  // This format matches what Google expects as Content.
  const serializedRawMessage = serializeContent(candidate?.content);

  const assistantMessage: AssistantMessage = {
    role: "assistant",
    content: decodedContent,
    name: null,
    providerId: "google",
    modelId,
    providerModelName: modelName(modelId),
    rawMessage:
      serializedRawMessage as unknown as AssistantMessage["rawMessage"],
  };

  const finishReason = decodeFinishReason(candidate?.finishReason);
  const usage = decodeUsage(response);

  return { assistantMessage, finishReason, usage };
}

/**
 * Decode Google response parts to Mirascope content format.
 *
 * @param parts - Array of Google Part objects from the response
 * @param includeThoughts - Whether to include thought parts
 * @returns Array of Mirascope AssistantContentPart objects
 * @throws FeatureNotSupportedError for unsupported part types (function_call)
 */
function decodeContent(
  parts: Part[],
  includeThoughts: boolean,
): AssistantContentPart[] {
  const content: AssistantContentPart[] = [];

  for (const part of parts) {
    if (part.thought && part.text !== undefined) {
      if (includeThoughts) {
        const thought: Thought = { type: "thought", thought: part.text };
        content.push(thought);
      }
    } else if (part.text !== undefined) {
      const text: Text = { type: "text", text: part.text };
      content.push(text);
      /* v8 ignore start - tool decoding will be tested via e2e */
    } else if (part.functionCall) {
      // Google doesn't always provide IDs for function calls
      const name = part.functionCall.name ?? "";
      const toolCall: ToolCall = {
        type: "tool_call",
        id: part.functionCall.id ?? UNKNOWN_TOOL_ID,
        name,
        args: JSON.stringify(part.functionCall.args ?? {}),
      };
      content.push(toolCall);
      /* v8 ignore stop */
      /* v8 ignore start - defensive unknown part handling */
    } else {
      // Unknown part type - be strict so we know what we're missing
      const partKeys = Object.keys(part).filter(
        (k) => part[k as keyof Part] !== undefined,
      );
      throw new FeatureNotSupportedError(
        `unknown part type: ${partKeys.join(", ")}`,
        "google",
        null,
        `Unknown content part in response is not yet implemented`,
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
  finishReason: GoogleFinishReasonType | undefined,
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
