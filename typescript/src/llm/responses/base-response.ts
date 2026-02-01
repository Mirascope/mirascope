/**
 * Shared base of Response implementations.
 */

import type {
  AssistantContentPart,
  Text,
  Thought,
  ToolCall,
} from "@/llm/content";
import type { Format } from "@/llm/formatting";
import type { AssistantMessage, Message } from "@/llm/messages";
import type { Params } from "@/llm/models";
import type { ModelId, ProviderId } from "@/llm/providers";
import type { FinishReason } from "@/llm/responses/finish-reason";
import type { Usage } from "@/llm/responses/usage";
import type { BaseToolkit } from "@/llm/tools";

import { FORMAT_TOOL_NAME } from "@/llm/formatting";
import { RootResponse } from "@/llm/responses/root-response";

/**
 * Initialization options for creating a BaseResponse.
 */
export interface BaseResponseInit {
  /**
   * The raw response from the LLM provider.
   */
  raw: unknown;

  /**
   * The provider that generated this response.
   */
  providerId: ProviderId;

  /**
   * The model ID that generated this response.
   */
  modelId: ModelId;

  /**
   * Provider-specific model name (may include additional info like API mode).
   */
  providerModelName: string;

  /**
   * The parameters used to generate this response.
   */
  params: Params;

  /**
   * The toolkit containing all tools available for this response.
   * Can be a Toolkit or ContextToolkit.
   */
  toolkit: BaseToolkit;

  /**
   * The Format describing the structured response format, if any.
   */
  format?: Format | null;

  /**
   * The input messages (before the assistant response).
   */
  inputMessages: readonly Message[];

  /**
   * The assistant message containing the response content.
   */
  assistantMessage: AssistantMessage;

  /**
   * The reason generation stopped, if not normal completion.
   */
  finishReason: FinishReason | null;

  /**
   * Token usage statistics, if available.
   */
  usage: Usage | null;
}

/**
 * Base response class with constructor logic.
 *
 * This class processes the assistant message content, organizing it by type
 * (text, tool calls, thoughts) for easy access.
 *
 * @template F - The type of the formatted output when using structured outputs.
 */
export class BaseResponse<F = unknown> extends RootResponse<F> {
  readonly raw: unknown;
  readonly providerId: ProviderId;
  readonly modelId: ModelId;
  readonly providerModelName: string;
  readonly params: Params;
  readonly messages: readonly Message[];
  readonly content: readonly AssistantContentPart[];
  readonly texts: readonly Text[];
  readonly toolCalls: readonly ToolCall[];
  readonly thoughts: readonly Thought[];
  readonly finishReason: FinishReason | null;
  readonly usage: Usage | null;
  readonly format: Format | null;
  readonly toolkit: BaseToolkit;

  constructor(init: BaseResponseInit) {
    super();

    this.raw = init.raw;
    this.providerId = init.providerId;
    this.modelId = init.modelId;
    this.providerModelName = init.providerModelName;
    this.params = init.params;
    this.finishReason = init.finishReason;
    this.usage = init.usage;
    this.format = init.format ?? null;

    // Process content from assistant message, organizing by type
    // FORMAT_TOOL calls are transformed to text content for parse() access
    const texts: Text[] = [];
    const toolCalls: ToolCall[] = [];
    const thoughts: Thought[] = [];
    const content: AssistantContentPart[] = [];

    for (const part of init.assistantMessage.content) {
      if (part.type === "text") {
        texts.push(part);
        content.push(part);
        /* v8 ignore start - tool_call and thought content not yet implemented */
      } else if (part.type === "tool_call") {
        // Transform FORMAT_TOOL calls to text content
        // The tool call args contain the JSON structured output
        if (part.name.startsWith(FORMAT_TOOL_NAME)) {
          const textPart: Text = { type: "text", text: part.args };
          texts.push(textPart);
          content.push(textPart);
        } else {
          toolCalls.push(part);
          content.push(part);
        }
      } else if (part.type === "thought") {
        thoughts.push(part);
        content.push(part);
      }
      /* v8 ignore stop */
    }

    this.texts = texts;
    this.toolCalls = toolCalls;
    this.thoughts = thoughts;
    this.content = content;

    // Build full message history
    this.messages = [...init.inputMessages, init.assistantMessage];

    // Store the toolkit directly (conversion from tools happens in child classes)
    this.toolkit = init.toolkit;
  }
}
