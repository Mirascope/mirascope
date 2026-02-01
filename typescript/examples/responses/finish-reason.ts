/**
 * Finish reason example.
 *
 * Demonstrates checking why a response ended (normal completion,
 * token limit, etc.).
 *
 * Run with: bun run example examples/responses/finish-reason.ts
 */
import { llm } from "mirascope";

const model = llm.model("anthropic/claude-haiku-4-5", { maxTokens: 40 });
const response = await model.call("Write a long story about a bear.");

// finishReason is null when the response completes normally
// It's set when the response was cut off or stopped abnormally
if (response.finishReason === llm.FinishReason.MAX_TOKENS) {
  console.log("Response was truncated due to token limit");
} else if (response.finishReason === null) {
  console.log("Response completed normally");
}
