/**
 * Session management example.
 *
 * This example demonstrates how to group related traces together
 * using sessions for multi-turn conversations.
 */
import { llm, ops } from "mirascope";

// Configure tracing
ops.configure({
  apiKey: process.env.MIRASCOPE_API_KEY,
});

// Define a chat function
const chat = llm.defineCall<{ message: string }>({
  model: "anthropic/claude-haiku-4-5",
  maxTokens: 1024,
  template: ({ message }) => message,
});

// Wrap with tracing
const tracedChat = ops.traceCall(chat);

// Run multiple calls within a session
// All traces within the session are grouped together in Mirascope Cloud
await ops.session({ id: "user-123-conversation-1" }, async () => {
  console.log("=== Session Start ===");

  // First message
  const response1 = await tracedChat({ message: "Hello! What is TypeScript?" });
  console.log("Response 1:", response1.text());

  // Second message (same session)
  const response2 = await tracedChat({
    message: "Can you give me a simple example?",
  });
  console.log("Response 2:", response2.text());

  // Check current session
  const currentSession = ops.currentSession();
  console.log("Current session ID:", currentSession?.id);

  console.log("=== Session End ===");
});

// You can also use custom session attributes
await ops.session(
  {
    id: "user-456-conversation-1",
    attributes: {
      userId: "user-456",
      conversationType: "support",
      channel: "web",
    },
  },
  async () => {
    const response = await tracedChat({
      message: "I need help with my account.",
    });
    console.log("Support response:", response.text());
  },
);
await ops.forceFlush();
