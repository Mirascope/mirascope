/**
 * Basic ops tracing example.
 *
 * This example demonstrates how to configure tracing and wrap functions
 * with the trace() wrapper for observability.
 */
import { llm, ops } from "mirascope";

// Configure tracing with Mirascope Cloud (or use a custom tracer provider)
ops.configure({
  apiKey: process.env.MIRASCOPE_API_KEY,
});

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
