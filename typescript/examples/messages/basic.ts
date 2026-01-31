/**
 * Basic message creation example.
 *
 * Demonstrates creating messages with shorthand functions.
 *
 * Run with: bun run example examples/messages/basic.ts
 */
import { llm, type Message } from "mirascope";

// Creating messages with shorthand functions
const systemMessage = llm.messages.system("You are a helpful assistant.");
const userMessage = llm.messages.user("Hello, how are you?");

// Messages are used when calling LLMs
const messages: readonly Message[] = [systemMessage, userMessage];

console.log(messages);
