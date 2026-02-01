/**
 * Response resume example.
 *
 * Demonstrates continuing a conversation by resuming from a response
 * with a new user message.
 *
 * Run with: bun run example examples/responses/resume.ts
 */
import { llm } from "mirascope";

const model = llm.model("openai/gpt-4o");
const response = await model.call("What's the capital of France?");
console.log(response.text());
// Paris is the capital of France.

// Continue the conversation with the same model and message history
const followup = await response.resume("What's the population of that city?");
console.log(followup.text());
// Paris has a population of approximately 2.1 million people...

// Chain multiple turns
const another = await followup.resume("What famous landmarks are there?");
console.log(another.text());
// Paris is home to many famous landmarks including the Eiffel Tower...
