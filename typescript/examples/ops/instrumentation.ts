/**
 * LLM instrumentation example.
 *
 * This example demonstrates how to instrument LLM calls for automatic
 * tracing with GenAI semantic conventions.
 */
import { llm, ops } from "mirascope";

// Configure tracing
ops.configure({
  apiKey: process.env.MIRASCOPE_API_KEY,
});

// Instrument the Mirascope LLM module
// This wraps all Model methods to create spans with GenAI attributes
ops.instrumentLLM();

// Now all LLM calls are automatically traced
const recommendBook = llm.defineCall<{ genre: string }>({
  model: "anthropic/claude-haiku-4-5",
  maxTokens: 1024,
  template: ({ genre }) => `Please recommend a book in ${genre}.`,
});

// This call is automatically instrumented with:
// - gen_ai.system: "anthropic"
// - gen_ai.request.model: "claude-haiku-4-5"
// - gen_ai.usage.input_tokens: <count>
// - gen_ai.usage.output_tokens: <count>
// - And more GenAI semantic convention attributes
const response = await recommendBook({ genre: "mystery" });
console.log("Response:", response.text());
console.log("Usage:", response.usage);

// You can also instrument provider SDKs directly
// These use community OpenTelemetry instrumentation packages

// Instrument OpenAI SDK (requires @opentelemetry/instrumentation-openai)
// await ops.instrumentOpenai();

// Instrument Anthropic SDK (requires @traceloop/instrumentation-anthropic)
// await ops.instrumentAnthropic();

// Instrument Google GenAI SDK (requires @traceloop/instrumentation-google-generativeai)
// await ops.instrumentGoogleGenai();

// Check instrumentation status
console.log("LLM instrumented:", ops.isLLMInstrumented());

// Uninstrument when done (optional - usually left instrumented)
// ops.uninstrumentLLM();
await ops.forceFlush();
