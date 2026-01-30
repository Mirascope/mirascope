import { describe, expect, it } from "vitest";

import type { Image } from "@/llm/content/image";
import type { Thought } from "@/llm/content/thought";
import type { ToolCall } from "@/llm/content/tool-call";

import { assistant, system, user } from "@/llm/messages/message";

describe("system", () => {
  it("creates a system message from a string", () => {
    const msg = system("You are a helpful assistant.");

    expect(msg).toEqual({
      role: "system",
      content: { type: "text", text: "You are a helpful assistant." },
    });
  });

  it("creates a system message from a Text object", () => {
    const msg = system({ type: "text", text: "System instructions." });

    expect(msg).toEqual({
      role: "system",
      content: { type: "text", text: "System instructions." },
    });
  });
});

describe("user", () => {
  it("creates a user message from a string", () => {
    const msg = user("Hello!");

    expect(msg).toEqual({
      role: "user",
      content: [{ type: "text", text: "Hello!" }],
      name: null,
    });
  });

  it("creates a user message from a Text object", () => {
    const msg = user({ type: "text", text: "Hello!" });

    expect(msg).toEqual({
      role: "user",
      content: [{ type: "text", text: "Hello!" }],
      name: null,
    });
  });

  it("creates a user message from an array of strings", () => {
    const msg = user(["Hello!", "How are you?"]);

    expect(msg).toEqual({
      role: "user",
      content: [
        { type: "text", text: "Hello!" },
        { type: "text", text: "How are you?" },
      ],
      name: null,
    });
  });

  it("creates a user message with mixed content types", () => {
    const image: Image = {
      type: "image",
      source: { type: "url_image_source", url: "https://example.com/img.png" },
    };

    const msg = user(["Look at this:", image]);

    expect(msg).toEqual({
      role: "user",
      content: [{ type: "text", text: "Look at this:" }, image],
      name: null,
    });
  });

  it("creates a user message with a name", () => {
    const msg = user("Hello!", { name: "Alice" });

    expect(msg).toEqual({
      role: "user",
      content: [{ type: "text", text: "Hello!" }],
      name: "Alice",
    });
  });
});

describe("assistant", () => {
  it("creates an assistant message from a string", () => {
    const msg = assistant("Hello! How can I help?", {
      modelId: "claude-3-opus",
      providerId: "anthropic",
    });

    expect(msg).toEqual({
      role: "assistant",
      content: [{ type: "text", text: "Hello! How can I help?" }],
      name: null,
      providerId: "anthropic",
      modelId: "claude-3-opus",
      providerModelName: null,
      rawMessage: null,
    });
  });

  it("creates an assistant message from a Text object", () => {
    const msg = assistant(
      { type: "text", text: "Response text." },
      { modelId: null, providerId: null },
    );

    expect(msg).toEqual({
      role: "assistant",
      content: [{ type: "text", text: "Response text." }],
      name: null,
      providerId: null,
      modelId: null,
      providerModelName: null,
      rawMessage: null,
    });
  });

  it("creates an assistant message with tool calls", () => {
    const toolCall: ToolCall = {
      type: "tool_call",
      id: "call_123",
      name: "get_weather",
      args: '{"location": "San Francisco"}',
    };

    const msg = assistant(["Let me check the weather.", toolCall], {
      modelId: "gpt-4",
      providerId: "openai",
    });

    expect(msg).toEqual({
      role: "assistant",
      content: [{ type: "text", text: "Let me check the weather." }, toolCall],
      name: null,
      providerId: "openai",
      modelId: "gpt-4",
      providerModelName: null,
      rawMessage: null,
    });
  });

  it("creates an assistant message with thoughts", () => {
    const thought: Thought = {
      type: "thought",
      thought: "I should consider the context...",
    };

    const msg = assistant([thought, "Here is my response."], {
      modelId: "claude-3-opus",
      providerId: "anthropic",
    });

    expect(msg).toEqual({
      role: "assistant",
      content: [thought, { type: "text", text: "Here is my response." }],
      name: null,
      providerId: "anthropic",
      modelId: "claude-3-opus",
      providerModelName: null,
      rawMessage: null,
    });
  });

  it("creates an assistant message with all optional fields", () => {
    const rawData = { id: "msg_123", model: "claude-3-opus" };

    const msg = assistant("Response", {
      modelId: "claude-3-opus",
      providerId: "anthropic",
      providerModelName: "claude-3-opus:messages",
      rawMessage: rawData,
      name: "Assistant",
    });

    expect(msg).toEqual({
      role: "assistant",
      content: [{ type: "text", text: "Response" }],
      name: "Assistant",
      providerId: "anthropic",
      modelId: "claude-3-opus",
      providerModelName: "claude-3-opus:messages",
      rawMessage: rawData,
    });
  });
});
