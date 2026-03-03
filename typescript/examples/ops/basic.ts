import {
  SimpleSpanProcessor,
  ConsoleSpanExporter,
} from "@opentelemetry/sdk-trace-base";
// Configure tracing with a TracerProvider (see Configuration docs for backend options)
// Example: use ConsoleSpanExporter for development
import { NodeTracerProvider } from "@opentelemetry/sdk-trace-node";
/**
 * Basic ops tracing example.
 *
 * This example demonstrates how to configure tracing and wrap functions
 * with the trace() wrapper for observability.
 */
import { llm, ops } from "mirascope";

const provider = new NodeTracerProvider();
provider.addSpanProcessor(new SimpleSpanProcessor(new ConsoleSpanExporter()));
ops.configure({ tracerProvider: provider });

// Define a simple call
const recommendBook = llm.defineCall<{ genre: string }>({
  model: "anthropic/claude-haiku-4-5",
  maxTokens: 1024,
  template: ({ genre }) => `Please recommend a book in ${genre}.`,
});

// Wrap the call with tracing - the unified trace() API handles both functions and calls
const tracedRecommendBook = ops.trace(recommendBook, {
  tags: ["recommendation", "books"],
  metadata: { source: "example" },
});

// Execute the traced call
const response = await tracedRecommendBook({ genre: "fantasy" });
console.log("Response:", response.text());
await ops.forceFlush();
