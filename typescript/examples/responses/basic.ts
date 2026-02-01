/**
 * Basic response usage example.
 *
 * Demonstrates accessing the response object and its text content.
 *
 * Run with: bun run example examples/responses/basic.ts
 */
import { llm } from "mirascope";

const model = llm.model("openai/gpt-4o-mini");
const response = await model.call("What is the capital of France?");

// Prints the textual content of the response
console.log(response.text());
// Paris is the capital of France.
