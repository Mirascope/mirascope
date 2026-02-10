/**
 * Unit tests for OpenAI Completions provider utilities.
 *
 * Note: Most encoding tests are covered by e2e tests in tests/e2e/.
 * These tests focus on edge cases that can't be triggered via e2e.
 */

import type { ChatCompletion } from "openai/resources/chat/completions";

import { describe, it, expect, vi } from "vitest";

import type { Thought } from "@/llm/content";
import type { AudioMimeType } from "@/llm/content";
import type { AssistantMessage } from "@/llm/messages";

import { Audio, Document } from "@/llm/content";
import { FeatureNotSupportedError } from "@/llm/exceptions";
import { assistant, user } from "@/llm/messages";
import {
  encodeMessages,
  decodeResponse,
  buildRequestParams,
} from "@/llm/providers/openai/completions/_utils";
import { featureInfoForOpenAIModel } from "@/llm/providers/openai/completions/_utils/feature-info";
import { FinishReason } from "@/llm/responses/finish-reason";

describe("encodeMessages edge cases", () => {
  it("encodes user message with name", () => {
    const messages = [user("Hello!", { name: "Alice" })];
    const encoded = encodeMessages(messages);

    expect(encoded).toEqual([
      { role: "user", content: "Hello!", name: "Alice" },
    ]);
  });

  it("encodes assistant message with empty content", () => {
    const messages = [
      assistant([], { providerId: "openai", modelId: "openai/gpt-4o" }),
    ];
    const encoded = encodeMessages(messages);

    expect(encoded).toEqual([{ role: "assistant", content: null }]);
  });

  it("encodes assistant message with name", () => {
    const messages = [
      assistant("Hi!", {
        providerId: "openai",
        modelId: "openai/gpt-4o",
        name: "Bot",
      }),
    ];
    const encoded = encodeMessages(messages);

    expect(encoded).toEqual([
      { role: "assistant", content: "Hi!", name: "Bot" },
    ]);
  });
});

describe("buildRequestParams thinking config", () => {
  it("encodes thoughts as text when encodeThoughtsAsText is true", () => {
    const thought: Thought = { type: "thought", thought: "Reasoning..." };
    const messages = [
      assistant([thought, { type: "text", text: "Result" }], {
        providerId: "openai",
        modelId: "openai/gpt-4o",
      }),
    ];

    const params = buildRequestParams(
      "openai/gpt-4o:completions",
      messages,
      undefined,
      {
        thinking: { level: "medium", encodeThoughtsAsText: true },
      },
    );

    // Multiple text parts are kept as a list (thought encoded as text + result)
    expect(params.messages).toEqual([
      {
        role: "assistant",
        content: [
          { type: "text", text: "**Thinking:** Reasoning..." },
          { type: "text", text: "Result" },
        ],
      },
    ]);
  });

  it("drops thoughts when encodeThoughtsAsText is not set", () => {
    const thought: Thought = { type: "thought", thought: "Reasoning..." };
    const messages = [
      assistant([thought, { type: "text", text: "Result" }], {
        providerId: "openai",
        modelId: "openai/gpt-4o",
      }),
    ];

    const params = buildRequestParams(
      "openai/gpt-4o:completions",
      messages,
      undefined,
      {
        thinking: { level: "medium" },
      },
    );

    // Single text part is simplified to string
    expect(params.messages).toEqual([{ role: "assistant", content: "Result" }]);
  });
});

describe("buildRequestParams", () => {
  it("builds basic request with messages", () => {
    const messages = [user("Hello")];
    const params = buildRequestParams("openai/gpt-4o", messages);

    expect(params).toEqual({
      model: "gpt-4o",
      messages: [{ role: "user", content: "Hello" }],
    });
  });

  it("includes maxTokens when provided", () => {
    const messages = [user("Hello")];
    const params = buildRequestParams("openai/gpt-4o", messages, undefined, {
      maxTokens: 100,
    });

    expect(params.max_completion_tokens).toBe(100);
  });

  it("includes temperature when provided", () => {
    const messages = [user("Hello")];
    const params = buildRequestParams("openai/gpt-4o", messages, undefined, {
      temperature: 0.7,
    });

    expect(params.temperature).toBe(0.7);
  });

  it("includes topP when provided", () => {
    const messages = [user("Hello")];
    const params = buildRequestParams("openai/gpt-4o", messages, undefined, {
      topP: 0.9,
    });

    expect(params.top_p).toBe(0.9);
  });

  it("includes seed when provided", () => {
    const messages = [user("Hello")];
    const params = buildRequestParams("openai/gpt-4o", messages, undefined, {
      seed: 42,
    });

    expect(params.seed).toBe(42);
  });

  it("includes stopSequences when provided", () => {
    const messages = [user("Hello")];
    const params = buildRequestParams("openai/gpt-4o", messages, undefined, {
      stopSequences: ["END", "STOP"],
    });

    expect(params.stop).toEqual(["END", "STOP"]);
  });
});

describe("buildRequestParams with reasoning models", () => {
  const reasoningModelFeatureInfo = { isReasoningModel: true };

  it("omits temperature for reasoning models and warns", () => {
    const messages = [user("Hello")];
    const consoleSpy = vi.spyOn(console, "warn").mockImplementation(() => {});

    const params = buildRequestParams(
      "openai/o1",
      messages,
      undefined,
      { temperature: 0.7 },
      reasoningModelFeatureInfo,
    );

    expect(params.temperature).toBeUndefined();
    expect(consoleSpy).toHaveBeenCalledWith(
      expect.stringContaining("temperature"),
    );

    consoleSpy.mockRestore();
  });

  it("omits topP for reasoning models and warns", () => {
    const messages = [user("Hello")];
    const consoleSpy = vi.spyOn(console, "warn").mockImplementation(() => {});

    const params = buildRequestParams(
      "openai/o1",
      messages,
      undefined,
      { topP: 0.9 },
      reasoningModelFeatureInfo,
    );

    expect(params.top_p).toBeUndefined();
    expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining("topP"));

    consoleSpy.mockRestore();
  });

  it("omits stopSequences for reasoning models and warns", () => {
    const messages = [user("Hello")];
    const consoleSpy = vi.spyOn(console, "warn").mockImplementation(() => {});

    const params = buildRequestParams(
      "openai/o1",
      messages,
      undefined,
      { stopSequences: ["END"] },
      reasoningModelFeatureInfo,
    );

    expect(params.stop).toBeUndefined();
    expect(consoleSpy).toHaveBeenCalledWith(
      expect.stringContaining("stopSequences"),
    );

    consoleSpy.mockRestore();
  });
});

describe("decodeResponse", () => {
  const createMockResponse = (
    overrides: Partial<ChatCompletion> = {},
  ): ChatCompletion => ({
    id: "chatcmpl-123",
    object: "chat.completion",
    created: 1677652288,
    model: "gpt-4o",
    choices: [
      {
        index: 0,
        message: {
          role: "assistant",
          content: "Hello!",
          refusal: null,
        },
        finish_reason: "stop",
        logprobs: null,
      },
    ],
    usage: {
      prompt_tokens: 5,
      completion_tokens: 2,
      total_tokens: 7,
    },
    ...overrides,
  });

  it("decodes refusal message as text content", () => {
    const response = createMockResponse({
      choices: [
        {
          index: 0,
          message: {
            role: "assistant",
            content: null,
            refusal: "I can't help with that request.",
          },
          finish_reason: "stop",
          logprobs: null,
        },
      ],
    });

    const decoded = decodeResponse(response, "openai/gpt-4o");

    expect(decoded.assistantMessage.content).toEqual([
      { type: "text", text: "I can't help with that request." },
    ]);
  });

  it("maps content_filter finish reason to REFUSAL", () => {
    const response = createMockResponse({
      choices: [
        {
          index: 0,
          message: {
            role: "assistant",
            content: "",
            refusal: null,
          },
          finish_reason: "content_filter",
          logprobs: null,
        },
      ],
    });

    const decoded = decodeResponse(response, "openai/gpt-4o");

    expect(decoded.finishReason).toBe(FinishReason.REFUSAL);
  });

  it("handles response without usage", () => {
    const response = createMockResponse();
    delete response.usage;

    const decoded = decodeResponse(response, "openai/gpt-4o");

    expect(decoded.usage).toBeNull();
  });
});

describe("raw message round-tripping", () => {
  const createMockResponse = (
    overrides: Partial<ChatCompletion> = {},
  ): ChatCompletion => ({
    id: "chatcmpl-123",
    object: "chat.completion",
    created: 1677652288,
    model: "gpt-4o",
    choices: [
      {
        index: 0,
        message: {
          role: "assistant",
          content: "Hello!",
          refusal: null,
        },
        finish_reason: "stop",
        logprobs: null,
      },
    ],
    usage: {
      prompt_tokens: 5,
      completion_tokens: 2,
      total_tokens: 7,
    },
    ...overrides,
  });

  it("decodeResponse stores serialized message in rawMessage", () => {
    const response = createMockResponse();
    const { assistantMessage } = decodeResponse(response, "openai/gpt-4o");

    // rawMessage should be an object with role and content
    expect(typeof assistantMessage.rawMessage).toBe("object");

    const rawMessage = assistantMessage.rawMessage as unknown as {
      role: string;
      content: string;
    };
    expect(rawMessage.role).toBe("assistant");
    expect(rawMessage.content).toBe("Hello!");
  });

  it("decodeResponse sets providerModelName with completions suffix", () => {
    const response = createMockResponse();
    const { assistantMessage } = decodeResponse(response, "openai/gpt-4o");

    // Should be the base model name with :completions suffix
    expect(assistantMessage.providerModelName).toBe("gpt-4o:completions");
  });

  it("encodeMessages reuses rawMessage for matching assistant messages", () => {
    // Create an assistant message that would have come from decodeResponse
    const assistantMsg: AssistantMessage = {
      role: "assistant",
      content: [{ type: "text", text: "Hello!" }],
      name: null,
      providerId: "openai",
      modelId: "openai/gpt-4o",
      providerModelName: "gpt-4o:completions",
      rawMessage: {
        role: "assistant",
        content: "Hello!",
      } as unknown as AssistantMessage["rawMessage"],
    };

    const messages = [user("Hi"), assistantMsg, user("How are you?")];
    const encoded = encodeMessages(messages, false, "openai/gpt-4o");

    // Should have: user message, raw assistant message, user message
    expect(encoded).toHaveLength(3);

    // First is user message
    expect(encoded[0]).toEqual({ role: "user", content: "Hi" });

    // Second should be the raw message reused directly
    expect(encoded[1]).toHaveProperty("role", "assistant");
    expect(encoded[1]).toHaveProperty("content", "Hello!");

    // Third is user message
    expect(encoded[2]).toEqual({ role: "user", content: "How are you?" });
  });

  it("encodeMessages does NOT reuse rawMessage for different provider", () => {
    // Create an assistant message from a different provider
    const assistantMsg: AssistantMessage = {
      role: "assistant",
      content: [{ type: "text", text: "Hello!" }],
      name: null,
      providerId: "anthropic", // Different provider
      modelId: "anthropic/claude-haiku-4-5",
      providerModelName: "claude-haiku-4-5",
      rawMessage: {
        role: "assistant",
        content: [{ type: "text", text: "Hello!" }],
      } as unknown as AssistantMessage["rawMessage"],
    };

    const messages = [user("Hi"), assistantMsg];
    const encoded = encodeMessages(messages, false, "openai/gpt-4o");

    // Should encode from content, not raw message
    expect(encoded).toHaveLength(2);
    expect(encoded[1]).toEqual({ role: "assistant", content: "Hello!" });
  });

  it("encodeMessages does NOT reuse rawMessage for different model", () => {
    // Create an assistant message from a different model
    const assistantMsg: AssistantMessage = {
      role: "assistant",
      content: [{ type: "text", text: "Hello!" }],
      name: null,
      providerId: "openai",
      modelId: "openai/gpt-4o-mini", // Different model
      providerModelName: "gpt-4o-mini:completions",
      rawMessage: {
        role: "assistant",
        content: "Hello!",
      } as unknown as AssistantMessage["rawMessage"],
    };

    const messages = [user("Hi"), assistantMsg];
    // Request is for gpt-4o, but message is from gpt-4o-mini
    const encoded = encodeMessages(messages, false, "openai/gpt-4o");

    // Should encode from content, not raw message
    expect(encoded).toHaveLength(2);
    expect(encoded[1]).toEqual({ role: "assistant", content: "Hello!" });
  });

  it("encodeMessages does NOT reuse rawMessage without proper structure", () => {
    // Create an assistant message with non-standard rawMessage
    const assistantMsg: AssistantMessage = {
      role: "assistant",
      content: [{ type: "text", text: "Hello!" }],
      name: null,
      providerId: "openai",
      modelId: "openai/gpt-4o",
      providerModelName: "gpt-4o:completions",
      rawMessage: {
        // Missing 'role' key - should not be reused
        content: "Hello!",
      } as unknown as AssistantMessage["rawMessage"],
    };

    const messages = [user("Hi"), assistantMsg];
    const encoded = encodeMessages(messages, false, "openai/gpt-4o");

    // Should encode from content, not raw message
    expect(encoded).toHaveLength(2);
    expect(encoded[1]).toEqual({ role: "assistant", content: "Hello!" });
  });

  it("encodeMessages does NOT reuse rawMessage when encodeThoughtsAsText is true", () => {
    // Create an assistant message with proper structure
    const assistantMsg: AssistantMessage = {
      role: "assistant",
      content: [{ type: "text", text: "Hello!" }],
      name: null,
      providerId: "openai",
      modelId: "openai/gpt-4o",
      providerModelName: "gpt-4o:completions",
      rawMessage: {
        role: "assistant",
        content: "Hello!",
      } as unknown as AssistantMessage["rawMessage"],
    };

    const messages = [user("Hi"), assistantMsg];
    // encodeThoughtsAsText is true - should not reuse raw message
    const encoded = encodeMessages(messages, true, "openai/gpt-4o");

    // Should encode from content, not raw message
    expect(encoded).toHaveLength(2);
    expect(encoded[1]).toEqual({ role: "assistant", content: "Hello!" });
  });
});

describe("audio encoding", () => {
  it("throws FeatureNotSupportedError for unsupported audio format", () => {
    // Create audio with unsupported format (ogg)
    const oggAudio = {
      type: "audio" as const,
      source: {
        type: "base64_audio_source" as const,
        data: "dGVzdA==", // base64 for 'test'
        mimeType: "audio/ogg" as AudioMimeType,
      },
    };
    const messages = [user(["Listen to this", oggAudio])];

    expect(() =>
      buildRequestParams("openai/gpt-4o-audio-preview:completions", messages),
    ).toThrow(FeatureNotSupportedError);
  });

  it("throws FeatureNotSupportedError for models without audio support", () => {
    // Create valid WAV audio with proper magic bytes (RIFF....WAVE)
    const wavAudio = Audio.fromBytes(
      new Uint8Array([
        0x52,
        0x49,
        0x46,
        0x46, // 'RIFF'
        0x00,
        0x00,
        0x00,
        0x00, // file size (placeholder)
        0x57,
        0x41,
        0x56,
        0x45, // 'WAVE'
      ]),
    );
    const messages = [user(["Listen to this", wavAudio])];

    // gpt-4o-mini doesn't support audio - need to pass feature info to enable check
    const featureInfo = featureInfoForOpenAIModel("gpt-4o-mini");
    expect(() =>
      buildRequestParams(
        "openai/gpt-4o-mini:completions",
        messages,
        undefined,
        {},
        featureInfo,
      ),
    ).toThrow(FeatureNotSupportedError);
  });

  it("throws FeatureNotSupportedError with null modelId when modelId is undefined", () => {
    // Create valid WAV audio with proper magic bytes (RIFF....WAVE)
    const wavAudio = Audio.fromBytes(
      new Uint8Array([
        0x52,
        0x49,
        0x46,
        0x46, // 'RIFF'
        0x00,
        0x00,
        0x00,
        0x00, // file size (placeholder)
        0x57,
        0x41,
        0x56,
        0x45, // 'WAVE'
      ]),
    );
    const messages = [user(["Listen to this", wavAudio])];

    // Call encodeMessages directly without modelId but with feature info that disables audio
    const featureInfo = { audioSupport: false };
    expect(() =>
      encodeMessages(messages, false, undefined, featureInfo),
    ).toThrow(FeatureNotSupportedError);
  });
});

describe("document encoding", () => {
  it("encodes base64 document source as file", () => {
    const doc: Document = {
      type: "document",
      source: {
        type: "base64_document_source",
        data: "JVBERi0xLjQ=",
        mediaType: "application/pdf",
      },
    };
    const messages = [user(["Read this", doc])];

    const params = buildRequestParams("openai/gpt-4o:completions", messages);

    const content = (params.messages[0] as { content: unknown[] }).content;
    expect(content).toHaveLength(2);
    expect(content[1]).toEqual({
      type: "file",
      file: {
        file_data: "data:application/pdf;base64,JVBERi0xLjQ=",
        filename: "document.pdf",
      },
    });
  });

  it("encodes text document source as file", () => {
    const doc: Document = {
      type: "document",
      source: {
        type: "text_document_source",
        data: "Hello, world!",
        mediaType: "text/plain",
      },
    };
    const messages = [user(["Read this", doc])];

    const params = buildRequestParams("openai/gpt-4o:completions", messages);

    const content = (params.messages[0] as { content: unknown[] }).content;
    expect(content).toHaveLength(2);
    expect(content[1]).toEqual({
      type: "file",
      file: {
        file_data: `data:text/plain;base64,${btoa("Hello, world!")}`,
        filename: "document.txt",
      },
    });
  });

  it("throws FeatureNotSupportedError for URL document source", () => {
    const doc = Document.fromUrl("https://example.com/doc.pdf");
    const messages = [user(["Read this", doc])];

    expect(() =>
      buildRequestParams("openai/gpt-4o:completions", messages),
    ).toThrow(FeatureNotSupportedError);
  });
});
