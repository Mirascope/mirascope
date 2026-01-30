/**
 * Basic structured output example using TypeScript types with JSDoc.
 *
 * Demonstrates using plain TypeScript types (no Zod) to get typed responses from LLMs.
 * The compile-time transformer injects the JSON schema from the type definition,
 * including JSDoc comments as field descriptions.
 *
 * Run with: bun run example examples/format/basic.ts
 */
import { llm } from "mirascope";

/**
 * Define a TypeScript type for the structured output.
 * JSDoc comments on properties become field descriptions in the schema,
 * helping the LLM understand what each field should contain.
 */
type Book = {
  /** The title of the book */
  title: string;
  /** The author's full name */
  author: string;
  /** The year the book was published */
  year: string;
  /** The literary genre (e.g., science fiction, fantasy, mystery) */
  genre: string;
  /** A brief 2-3 sentence summary of the book's plot */
  summary: string;
};

// Create a call with the format
// Use defineCall<VarsType>()({...}) to specify variables type while inferring format type.
const recommendBook = llm.defineCall<{ genre: string }>()({
  model: "anthropic/claude-haiku-4-5",
  maxTokens: 1024,
  format: llm.defineFormat<Book>({ mode: "tool" }),
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
