/**
 * Unit tests for OpenAI Responses provider utilities.
 *
 * Note: Most encoding/decoding tests are covered by e2e tests in tests/e2e/.
 * These tests focus on error mapping and thinking config encoding.
 */

import type { Response as OpenAIResponse } from "openai/resources/responses/responses";

import { describe, it, expect } from "vitest";

import type { AssistantMessage } from "@/llm/messages";

import { Audio, Document, Image } from "@/llm/content";
import { FeatureNotSupportedError } from "@/llm/exceptions";
import { user } from "@/llm/messages";
import {
  computeReasoning,
  buildRequestParams,
  decodeResponse,
  encodeMessages,
} from "@/llm/providers/openai/responses/_utils";

describe("computeReasoning", () => {
  it("maps default level to medium effort", () => {
    expect(computeReasoning("default", false)).toEqual({ effort: "medium" });
  });

  it("maps none level to none effort", () => {
    expect(computeReasoning("none", false)).toEqual({ effort: "none" });
  });

  it("maps minimal level to minimal effort", () => {
    expect(computeReasoning("minimal", false)).toEqual({ effort: "minimal" });
  });

  it("maps low level to low effort", () => {
    expect(computeReasoning("low", false)).toEqual({ effort: "low" });
  });

  it("maps medium level to medium effort", () => {
    expect(computeReasoning("medium", false)).toEqual({ effort: "medium" });
  });

  it("maps high level to high effort", () => {
    expect(computeReasoning("high", false)).toEqual({ effort: "high" });
  });

  it("maps max level to xhigh effort", () => {
    expect(computeReasoning("max", false)).toEqual({ effort: "xhigh" });
  });

  it("adds summary when includeThoughts is true", () => {
    expect(computeReasoning("medium", true)).toEqual({
      effort: "medium",
      summary: "auto",
    });
  });
});

describe("buildRequestParams thinking config", () => {
  it("sets reasoning when thinking is specified", () => {
    const messages = [user("Hello")];

    const params = buildRequestParams(
      "openai/o4-mini:responses",
      messages,
      undefined,
      {
        thinking: { level: "medium" },
      },
    );

    expect(params.reasoning).toEqual({ effort: "medium" });
  });

  it("sets reasoning with summary when includeThoughts is true", () => {
    const messages = [user("Hello")];

    const params = buildRequestParams(
      "openai/o4-mini:responses",
      messages,
      undefined,
      {
        thinking: { level: "high", includeThoughts: true },
      },
    );

    expect(params.reasoning).toEqual({ effort: "high", summary: "auto" });
  });
});

describe("image encoding", () => {
  it("encodes URL image source", () => {
    const urlImage = Image.fromUrl("https://example.com/image.png");
    const messages = [user(["Describe this", urlImage])];

    const params = buildRequestParams(
      "openai/gpt-4o:responses",
      messages,
      undefined,
      {},
    );

    // Check that the URL is passed through correctly
    expect(params.input).toContainEqual({
      role: "user",
      content: [
        { type: "input_text", text: "Describe this" },
        {
          type: "input_image",
          image_url: "https://example.com/image.png",
          detail: "auto",
        },
      ],
    });
  });
});

describe("audio encoding", () => {
  it("throws FeatureNotSupportedError for audio input", () => {
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

    expect(() =>
      buildRequestParams("openai/gpt-4o:responses", messages, undefined, {}),
    ).toThrow(FeatureNotSupportedError);
  });
});

describe("document encoding", () => {
  it("encodes base64 document source as input_file", () => {
    const doc: Document = {
      type: "document",
      source: {
        type: "base64_document_source",
        data: "JVBERi0xLjQ=",
        mediaType: "application/pdf",
      },
    };
    const messages = [user(["Read this", doc])];

    const params = buildRequestParams(
      "openai/gpt-4o:responses",
      messages,
      undefined,
      {},
    );

    expect(params.input).toContainEqual({
      role: "user",
      content: [
        { type: "input_text", text: "Read this" },
        {
          type: "input_file",
          file_data: "data:application/pdf;base64,JVBERi0xLjQ=",
          filename: "document.pdf",
        },
      ],
    });
  });

  it("encodes text document source as input_file", () => {
    const doc: Document = {
      type: "document",
      source: {
        type: "text_document_source",
        data: "Hello, world!",
        mediaType: "text/plain",
      },
    };
    const messages = [user(["Read this", doc])];

    const params = buildRequestParams(
      "openai/gpt-4o:responses",
      messages,
      undefined,
      {},
    );

    expect(params.input).toContainEqual({
      role: "user",
      content: [
        { type: "input_text", text: "Read this" },
        {
          type: "input_file",
          file_data: `data:text/plain;base64,${btoa("Hello, world!")}`,
          filename: "document.txt",
        },
      ],
    });
  });

  it("encodes URL document source as input_file with file_url", () => {
    const doc = Document.fromUrl("https://example.com/doc.pdf");
    const messages = [user(["Read this", doc])];

    const params = buildRequestParams(
      "openai/gpt-4o:responses",
      messages,
      undefined,
      {},
    );

    expect(params.input).toContainEqual({
      role: "user",
      content: [
        { type: "input_text", text: "Read this" },
        {
          type: "input_file",
          file_url: "https://example.com/doc.pdf",
        },
      ],
    });
  });
});

describe("raw message round-tripping", () => {
  // Mock response for testing - using minimal structure that matches actual API responses
  const mockOpenAIResponse = {
    id: "resp_123",
    object: "response",
    created_at: 1234567890,
    status: "completed",
    model: "gpt-4o",
    output: [
      {
        type: "message",
        id: "msg_123",
        status: "completed",
        role: "assistant",
        content: [{ type: "output_text", text: "Hello!", annotations: [] }],
      },
    ],
    usage: {
      input_tokens: 10,
      output_tokens: 5,
      total_tokens: 15,
    },
  } as unknown as OpenAIResponse;

  it("decodeResponse stores serialized output items in rawMessage", () => {
    const { assistantMessage } = decodeResponse(
      mockOpenAIResponse,
      "openai/gpt-4o:responses",
    );

    // rawMessage should be an array of serialized output items
    expect(Array.isArray(assistantMessage.rawMessage)).toBe(true);

    const rawMessage = assistantMessage.rawMessage as unknown as Array<
      Record<string, unknown>
    >;
    expect(rawMessage).toHaveLength(1);
    expect(rawMessage[0]).toHaveProperty("type", "message");
    expect(rawMessage[0]).toHaveProperty("id", "msg_123");
    expect(rawMessage[0]).toHaveProperty("content");
  });

  it("decodeResponse sets providerModelName with :responses suffix", () => {
    const { assistantMessage } = decodeResponse(
      mockOpenAIResponse,
      "openai/gpt-4o:responses",
    );

    expect(assistantMessage.providerModelName).toBe("gpt-4o:responses");
  });

  it("encodeMessages reuses rawMessage for matching assistant messages", () => {
    // Create an assistant message that would have come from decodeResponse
    const assistantMsg: AssistantMessage = {
      role: "assistant",
      content: [{ type: "text", text: "Hello!" }],
      name: null,
      providerId: "openai",
      modelId: "openai/gpt-4o:responses",
      providerModelName: "gpt-4o:responses",
      rawMessage: [
        {
          type: "message",
          id: "msg_123",
          status: "completed",
          role: "assistant",
          content: [{ type: "output_text", text: "Hello!" }],
        },
      ] as unknown as AssistantMessage["rawMessage"],
    };

    const messages = [user("Hi"), assistantMsg, user("How are you?")];
    const encoded = encodeMessages(messages, "openai/gpt-4o:responses");

    // Should have: user message, raw assistant output, user message
    expect(encoded).toHaveLength(3);

    // First is user message
    expect(encoded[0]).toEqual({ role: "user", content: "Hi" });

    // Second should be the raw message reused directly
    const assistantItem = encoded[1] as unknown as Record<string, unknown>;
    expect(assistantItem).toHaveProperty("type", "message");
    expect(assistantItem).toHaveProperty("id", "msg_123");

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
        // Some Anthropic raw message
        id: "msg_123",
        content: [{ type: "text", text: "Hello!" }],
      } as unknown as AssistantMessage["rawMessage"],
    };

    const messages = [user("Hi"), assistantMsg];
    const encoded = encodeMessages(messages, "openai/gpt-4o:responses");

    // Should encode from content, not raw message
    expect(encoded).toHaveLength(2);
    expect(encoded[1]).toEqual({ role: "assistant", content: "Hello!" });
  });

  it("encodeMessages does NOT reuse rawMessage for different model", () => {
    // Create an assistant message from a different OpenAI model
    const assistantMsg: AssistantMessage = {
      role: "assistant",
      content: [{ type: "text", text: "Hello!" }],
      name: null,
      providerId: "openai",
      modelId: "openai/gpt-4o-mini:responses",
      providerModelName: "gpt-4o-mini:responses", // Different model
      rawMessage: [
        {
          type: "message",
          id: "msg_123",
          status: "completed",
          role: "assistant",
          content: [{ type: "output_text", text: "Hello!" }],
        },
      ] as unknown as AssistantMessage["rawMessage"],
    };

    const messages = [user("Hi"), assistantMsg];
    // Request is for gpt-4o, but message is from gpt-4o-mini
    const encoded = encodeMessages(messages, "openai/gpt-4o:responses");

    // Should encode from content, not raw message
    expect(encoded).toHaveLength(2);
    expect(encoded[1]).toEqual({ role: "assistant", content: "Hello!" });
  });

  it("encodeMessages does NOT reuse non-array rawMessage", () => {
    // Create an assistant message with non-array rawMessage (legacy format)
    const assistantMsg: AssistantMessage = {
      role: "assistant",
      content: [{ type: "text", text: "Hello!" }],
      name: null,
      providerId: "openai",
      modelId: "openai/gpt-4o:responses",
      providerModelName: "gpt-4o:responses",
      rawMessage: {
        // Non-array format (old style)
        id: "resp_123",
        output: [],
      } as unknown as AssistantMessage["rawMessage"],
    };

    const messages = [user("Hi"), assistantMsg];
    const encoded = encodeMessages(messages, "openai/gpt-4o:responses");

    // Should encode from content, not raw message
    expect(encoded).toHaveLength(2);
    expect(encoded[1]).toEqual({ role: "assistant", content: "Hello!" });
  });
});
