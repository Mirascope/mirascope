import { llm } from "mirascope";

const sqrtTool = llm.defineTool<{ number: number }>({
  name: "sqrt_tool",
  description: "Computes the square root of a number",
  fieldDefinitions: {
    number: "The number to compute the square root of",
  },
  tool: ({ number }) => Math.sqrt(number),
});

const mathAssistant = llm.defineCall<{ query: string }>({
  model: "openai/gpt-4o-mini",
  tools: [sqrtTool],
  template: ({ query }) => query,
});

const response = await mathAssistant({
  query: "What's the square root of 4242?",
});

const toolCall = response.toolCalls[0]!;
console.log(toolCall);
// ToolCall { type: 'tool_call', id: '...', name: 'sqrt_tool', args: { number: 4242 } }

// Execute all tool calls and get outputs
const toolOutputs = await response.executeTools();
console.log(toolOutputs[0]);
// ToolOutput { type: 'tool_output', id: '...', name: 'sqrt_tool', output: 65.13063795173512, error: null }

const answer = await response.resume(toolOutputs);
console.log(answer.text());
// The square root of 4242 is approximately 65.13063795173512.
