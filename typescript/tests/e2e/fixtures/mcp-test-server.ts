/**
 * TypeScript MCP test server for E2E tests.
 *
 * This server provides the same tools as the Python test server,
 * allowing MCP tests to run without Python in CI.
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

// Ensure uncaught errors are logged to stderr for debugging
process.on("uncaughtException", (error) => {
  console.error("Uncaught exception in MCP server:", error);
  process.exit(1);
});

process.on("unhandledRejection", (reason) => {
  console.error("Unhandled rejection in MCP server:", reason);
  process.exit(1);
});

const server = new McpServer({
  name: "mirascope-test-server",
  version: "1.0.0",
});

// Schema definitions matching the Python server's Pydantic models
const ComputerInfoSchema = z.object({
  name: z.string().describe("The name of the computer"),
  years_computed: z.number().describe("How many years it took to compute"),
});

const UltimateAnswerSchema = z.object({
  answer: z.number().describe("The numerical answer"),
  question: z.string().describe("The question that was asked"),
  computed_by: ComputerInfoSchema.describe("Information about the computer"),
});

// Tool 1: greet - Simple string input/output
server.tool(
  "greet",
  "Greet a user with very special welcome.",
  {
    name: z.string().describe("The name of the person to greet"),
  },
  async ({ name }) => {
    return {
      content: [{ type: "text", text: `Welcome to Zombo.com, ${name}` }],
    };
  },
);

// Tool 2: answer_ultimate_question - No params, complex structured output
server.tool(
  "answer_ultimate_question",
  "Answer the ultimate question of life, the universe, and everything.",
  {},
  async () => {
    const answer = {
      answer: 42,
      question: "What is the answer to life, the universe, and everything?",
      computed_by: {
        name: "Deep Thought",
        years_computed: 7_500_000,
      },
    };
    return {
      content: [{ type: "text", text: JSON.stringify(answer) }],
    };
  },
);

// Tool 3: process_answer - Complex nested input with $defs
server.tool(
  "process_answer",
  "Process and format an ultimate answer.",
  {
    answer_data: UltimateAnswerSchema.describe("The answer data to process"),
  },
  async ({ answer_data }) => {
    const text =
      `The answer ${answer_data.answer} to '${answer_data.question}' ` +
      `was computed by ${answer_data.computed_by.name} ` +
      `over ${answer_data.computed_by.years_computed.toLocaleString()} years`;
    return {
      content: [{ type: "text", text }],
    };
  },
);

// Run with stdio transport
const transport = new StdioServerTransport();
await server.connect(transport);
