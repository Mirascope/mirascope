declare const Bun: unknown;

/**
 * Runtime integration test for the compile-time transformer.
 *
 * Used by both Node.js (via --import mirascope/loader) and Bun (via preload plugin).
 * Verifies that the transformer injects __schema into defineTool<T>() calls
 * and that the full tool-call flow works end-to-end.
 *
 * Run with Node.js:  node --import mirascope/loader tests/runtimes/transformer-test.ts
 * Run with Bun:      bun tests/runtimes/transformer-test.ts
 */
import { installMockFetch } from "./mock-fetch.ts";

// Install mock fetch BEFORE any SDK code creates provider clients
const mockState = installMockFetch();

// Ensure a dummy API key is set so the provider registry doesn't throw
// MissingAPIKeyError before any HTTP request reaches our mock fetch.
process.env.ANTHROPIC_API_KEY ??= "test-key";

// Import SDK after mock is installed
const { llm } = await import("mirascope");

// ============================================================================
// Helpers
// ============================================================================

const runtime = typeof Bun !== "undefined" ? "bun" : "node";

function assert(condition: boolean, message: string): asserts condition {
  if (!condition) {
    throw new Error(`FAIL: ${message}`);
  }
}

// ============================================================================
// Test: Transformer-based tool definition
// ============================================================================

type SqrtArgs = {
  /** The number to compute the square root of */
  number: number;
};

// defineTool<T>() without a Zod validator THROWS if __schema was not injected
// by the transformer. This is the primary assertion that the loader works.
const sqrtTool = llm.defineTool<SqrtArgs>({
  name: "sqrt_tool",
  description: "Computes the square root of a number",
  tool: ({ number }) => Math.sqrt(number),
});

console.log(`[${runtime}] 1. Transformer injected schema`);
assert(!!sqrtTool.parameters, "tool.parameters should exist");
assert(sqrtTool.parameters.type === "object", "schema type should be 'object'");
assert(
  !!sqrtTool.parameters.properties.number,
  "schema should have 'number' property",
);

// ============================================================================
// Test: Full tool-call flow with mocked API
// ============================================================================

const mathAssistant = llm.defineCall<{ query: string }>({
  model: "anthropic/claude-haiku-4-5",
  tools: [sqrtTool],
  template: ({ query }) => query,
});

console.log(`[${runtime}] 2. Making API call...`);
const response = await mathAssistant({ query: "What is sqrt(4242)?" });

assert(response.toolCalls.length === 1, "should have 1 tool call");
assert(
  response.toolCalls[0]!.name === "sqrt_tool",
  `tool call name should be 'sqrt_tool', got '${response.toolCalls[0]!.name}'`,
);

const toolOutputs = await response.executeTools();
assert(toolOutputs.length === 1, "should have 1 tool output");
assert(toolOutputs[0]!.error === null, "tool should not error");
console.log(`[${runtime}]    tool output: ${toolOutputs[0]!.result}`);

console.log(`[${runtime}] 3. Resuming with tool outputs...`);
const answer = await response.resume(toolOutputs);
assert(
  answer.text().includes("65.13"),
  `answer should contain '65.13', got '${answer.text()}'`,
);

// ============================================================================
// Test: Request body verification (schema was sent to API)
// ============================================================================

console.log(`[${runtime}] 4. Verifying request bodies...`);
assert(
  mockState.requests.length === 2,
  `should have made 2 API requests, got ${mockState.requests.length}`,
);

const firstReq = mockState.requests[0]!.body!;
const tools = firstReq.tools!;
assert(!!tools && tools.length === 1, "first request should have 1 tool");

const inputSchema = tools[0]!.input_schema;
assert(!!inputSchema, "tool should have input_schema in request");

const properties = inputSchema.properties ?? {};
assert(!!properties.number, "input_schema.properties should have 'number'");

console.log(`[${runtime}] All checks passed!`);
