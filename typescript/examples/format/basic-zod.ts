/**
 * Zod-native structured output example.
 *
 * Demonstrates using Zod schemas to get typed, validated responses from LLMs.
 * This pattern works WITHOUT the compile-time transformer.
 *
 * Run with: bun run example examples/format/basic-zod.ts
 */
import { llm } from "mirascope";
import { z } from "zod";

// Define a Zod schema for the structured output
const BookSchema = z.object({
  title: z.string().describe("The title of the book"),
  author: z.string().describe("The author of the book"),
  year: z.number().describe("The year the book was published"),
  genre: z.string().describe("The genre of the book"),
  summary: z.string().describe("A brief summary of the book"),
});

// Infer TypeScript type from Zod schema
type Book = z.infer<typeof BookSchema>;

// Create a call with format option
// Use defineCall<VarsType>()({...}) to specify variables type while inferring format type.
const recommendBook = llm.defineCall<{ genre: string }>()({
  model: "anthropic/claude-haiku-4-5",
  maxTokens: 1024,
  format: BookSchema, // Use Zod schema directly as format
  template: ({ genre }) =>
    `Recommend a classic ${genre} book. Provide structured information about the book.`,
});

// Call the LLM and parse the response
const response = await recommendBook({ genre: "science fiction" });

// Parse the structured response (fully typed)
const book = response.parse();

console.log("Recommended Book:");
console.log("================");
console.log(`Title: ${book.title}`);
console.log(`Author: ${book.author}`);
console.log(`Year: ${book.year}`);
console.log(`Genre: ${book.genre}`);
console.log(`Summary: ${book.summary}`);
