import { llm } from "mirascope";

// Basic streaming example
const recommendBook = llm.defineCall<{ genre: string }>({
  model: "openai/gpt-5-mini:responses",
  maxTokens: 1024,
  thinking: { level: "default", includeThoughts: true },
  template: ({ genre }) => `Recommend a ${genre} book`,
});

const response = await recommendBook.stream({ genre: "fantasy " });

// Stream text chunks as they arrive
process.stdout.write("Streaming: ");
for await (const text of response.textStream()) {
  process.stdout.write(text);
}
console.log("\n");

// Access the complete text after streaming
console.log("Complete text:", response.text());

// Access usage information
console.log("Usage:", response.usage);
