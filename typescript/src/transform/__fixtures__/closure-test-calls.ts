/**
 * Test fixtures for closure extraction with Call objects.
 *
 * These are real Call definitions that we test the transformer against.
 */
import { z } from "zod";

// Mock imports for testing
const llm = {
  defineCall: <_T = void>(config: unknown) => config,
  defineTool: <_T = void>(config: unknown) => config,
  messages: {
    system: (content: string) => ({ role: "system" as const, content }),
    user: (content: string) => ({ role: "user" as const, content }),
  },
};

const ops = {
  version: <T>(call: T, options?: unknown): T & { __version: unknown } => ({
    ...call,
    __version: options,
  }),
};

// Simple call with inline template
export const simpleCall = llm.defineCall({
  model: "openai/gpt-4o-mini",
  template: () => "Hello, world!",
});

// Call with variables
export const callWithVars = llm.defineCall<{ query: string }>({
  model: "openai/gpt-4o-mini",
  maxTokens: 1024,
  template: ({ query }: { query: string }) => `Please answer: ${query}`,
});

// Call with tools
const weatherTool = llm.defineTool({
  name: "get_weather",
  description: "Get the weather",
  validator: z.object({
    city: z.string(),
  }),
  tool: ({ city }: { city: string }) => `Weather in ${city}: sunny`,
});

export const callWithTools = llm.defineCall<{ location: string }>({
  model: "openai/gpt-4o-mini",
  tools: [weatherTool],
  template: ({ location }: { location: string }) =>
    `What's the weather in ${location}?`,
});

// Call with message helpers
export const callWithMessages = llm.defineCall<{ topic: string }>({
  model: "anthropic/claude-sonnet-4-20250514",
  maxTokens: 2048,
  template: ({ topic }: { topic: string }) => [
    llm.messages.system("You are a helpful assistant."),
    llm.messages.user(`Explain ${topic} to me.`),
  ],
});

// Multi-variable declaration (tests that we don't duplicate the statement)
const configA = "openai/gpt-4o-mini",
  configB = 512;

export const callWithMultiVarDeps = llm.defineCall({
  model: configA,
  maxTokens: configB,
  template: () => "Using multi-var deps",
});

// Versioned call - this is what we're testing
export const versionedSimpleCall = ops.version(simpleCall, {
  name: "simple-call",
  tags: ["test"],
});

export const versionedCallWithVars = ops.version(callWithVars, {
  name: "query-call",
  metadata: { version: "1.0" },
});

export const versionedCallWithTools = ops.version(callWithTools);

export const versionedCallWithMessages = ops.version(callWithMessages, {
  tags: ["production", "claude"],
});

export const versionedCallWithMultiVarDeps = ops.version(callWithMultiVarDeps, {
  name: "multi-var-deps",
});
