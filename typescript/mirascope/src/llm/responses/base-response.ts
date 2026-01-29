/**
 * Shared base of Response implementations.
 */

import type {
  AssistantContentPart,
  Text,
  Thought,
  ToolCall,
} from '@/llm/content';
import type { AssistantMessage, Message } from '@/llm/messages';
import type { Params } from '@/llm/models';
import type { ModelId, ProviderId } from '@/llm/providers';
import type { FinishReason } from '@/llm/responses/finish-reason';
import { RootResponse } from '@/llm/responses/root-response';
import type { Usage } from '@/llm/responses/usage';

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
 */
export class BaseResponse extends RootResponse {
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

  constructor(init: BaseResponseInit) {
    super();

    this.raw = init.raw;
    this.providerId = init.providerId;
    this.modelId = init.modelId;
    this.providerModelName = init.providerModelName;
    this.params = init.params;
    this.finishReason = init.finishReason;
    this.usage = init.usage;

    // Process content from assistant message, organizing by type
    const texts: Text[] = [];
    const toolCalls: ToolCall[] = [];
    const thoughts: Thought[] = [];
    const content: AssistantContentPart[] = [];

    for (const part of init.assistantMessage.content) {
      content.push(part);

      if (part.type === 'text') {
        texts.push(part);
        /* v8 ignore start - tool_call and thought content not yet implemented */
      } else if (part.type === 'tool_call') {
        // Note: FORMAT_TOOL transformation is not implemented yet as it requires
        // Format infrastructure. When implemented, tool calls starting with the
        // format tool name should be converted to Text parts.
        toolCalls.push(part);
      } else if (part.type === 'thought') {
        thoughts.push(part);
      }
      /* v8 ignore stop */
    }

    this.texts = texts;
    this.toolCalls = toolCalls;
    this.thoughts = thoughts;
    this.content = content;

    // Build full message history
    this.messages = [...init.inputMessages, init.assistantMessage];
  }
}
