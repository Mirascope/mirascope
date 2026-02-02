/**
 * Function versioning example.
 *
 * This example demonstrates how to use version() to track
 * function changes across deployments. The compile-time transform
 * captures the original TypeScript source for accurate versioning.
 */
import { ops } from "mirascope";

// Configure with Mirascope Cloud for function registration
ops.configure({
  apiKey: process.env.MIRASCOPE_API_KEY,
});

// Version a function - the compile-time transform captures the source
// and computes a hash for tracking changes
const computeEmbedding = ops.version(
  async (text: string): Promise<number[]> => {
    // Simulate embedding computation
    const words = text.toLowerCase().split(/\s+/);
    return words.map((_, i) => Math.sin(i * 0.1));
  },
  {
    name: "embedding-v1",
    tags: ["embedding", "production"],
    metadata: { model: "custom" },
  },
);

// Use the versioned function
const embedding = await computeEmbedding("Hello world, this is a test.");
console.log("Embedding:", embedding.slice(0, 5), "...");

// Access version info
console.log("Version info:", computeEmbedding.versionInfo);

// Use .wrapped() to get both result and trace info
const result = await computeEmbedding.wrapped(
  "Another text to compute embedding for.",
);
console.log("Result embedding:", result.result.slice(0, 5), "...");
console.log("Trace ID:", result.traceId);
console.log("Function UUID:", result.functionUuid);

// Version a call with defineCall integration
import { llm } from "mirascope";

const recommendBook = llm.defineCall<{ genre: string }>({
  model: "anthropic/claude-haiku-4-5",
  maxTokens: 1024,
  template: ({ genre }) => `Please recommend a book in ${genre}.`,
});

// Version the call - the unified version() API handles both functions and calls
// Changes to the prompt template will be tracked
const versionedRecommend = ops.version(recommendBook, {
  name: "book-recommendation",
  tags: ["recommendation", "v1"],
});

const response = await versionedRecommend({ genre: "science fiction" });
console.log("Recommendation:", response.text());
console.log("Versioned call info:", versionedRecommend.versionInfo);
