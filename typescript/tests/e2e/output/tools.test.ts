/**
 * E2E tests for LLM tool usage.
 *
 * These tests verify we correctly encode tools in requests and decode
 * tool calls from responses. Tests run against multiple providers via parameterization.
 */

import { resolve } from "node:path";

import {
  defineCall,
  defineTool,
  type Response,
  type StreamResponse,
} from "@/llm";
import { PROVIDERS_FOR_TOOLS_TESTS } from "@/tests/e2e/providers";
import { createIt, describe, expect, snapshotTest } from "@/tests/e2e/utils";

const it = createIt(resolve(__dirname, "cassettes"), "tools");

/**
 * Password map for the secret retrieval tool.
 */
const PASSWORD_MAP: Record<string, string> = {
  mellon: "Welcome to Moria!",
  radiance: "Life before Death",
};

/**
 * A simple tool for testing that retrieves secrets based on passwords.
 */
const secretRetrievalTool = defineTool<{ password: string }>({
  name: "secret_retrieval_tool",
  description:
    "A tool that requires a password to retrieve a secret. Takes a 'password' field.",
  tool: ({ password }) => {
    return PASSWORD_MAP[password] ?? "Invalid password!";
  },
});

describe("tool usage", () => {
  it.record.each(PROVIDERS_FOR_TOOLS_TESTS)(
    "calls tool and resumes with results",
    async ({ model }) => {
      const retrieveSecrets = defineCall<{ passwords: string[] }>({
        model,
        maxTokens: 1000,
        tools: [secretRetrievalTool],
        template: ({ passwords }) =>
          `Please retrieve the secrets for these passwords: ${passwords.map((p) => `"${p}"`).join(" and ")}. ` +
          "Use the secret_retrieval_tool for each password.",
      });

      const snap = await snapshotTest(async (s) => {
        // Call with tool - ask LLM to use the tool
        let response: Response = await retrieveSecrets({
          passwords: ["mellon", "radiance"],
        });

        // Verify we got tool calls
        expect(response.toolCalls.length).toBeGreaterThanOrEqual(1);

        let iterations = 0;
        // Loop until no more tool calls (some providers like Google call tools sequentially)
        while (response.toolCalls.length > 0) {
          iterations++;
          // Execute the tools
          const toolOutputs = await response.executeTools();

          // Verify tool outputs
          expect(toolOutputs.length).toBe(response.toolCalls.length);
          for (const output of toolOutputs) {
            expect(output.type).toBe("tool_output");
            expect(output.error).toBeNull();
          }

          // Resume with tool outputs
          response = await response.resume(toolOutputs);
        }

        s.setResponse(response);
        s.set("toolIterations", iterations);

        // Verify the final response mentions the secrets
        const text = response.text();
        expect(text).toMatch(/moria/i);
        expect(text).toMatch(/life before death/i);
      });

      expect(snap.toObject()).toMatchSnapshot();
    },
  );
});

describe("tool usage with streaming", () => {
  it.record.each(PROVIDERS_FOR_TOOLS_TESTS)(
    "streams tool calls and resumes with results",
    async ({ model }) => {
      const retrieveSecrets = defineCall<{ passwords: string[] }>({
        model,
        maxTokens: 1000,
        tools: [secretRetrievalTool],
        template: ({ passwords }) =>
          `Please retrieve the secrets for these passwords: ${passwords.map((p) => `"${p}"`).join(" and ")}. ` +
          "Use the secret_retrieval_tool for each password.",
      });

      const snap = await snapshotTest(async (s) => {
        // Stream with tool - ask LLM to use the tool
        let response: StreamResponse = await retrieveSecrets.stream({
          passwords: ["mellon", "radiance"],
        });

        // Consume the stream (equivalent to Python's response.finish())
        await response.consume();

        // Verify we got tool calls
        expect(response.toolCalls.length).toBeGreaterThanOrEqual(1);

        let iterations = 0;
        // Loop until no more tool calls (some providers like Google call tools sequentially)
        while (response.toolCalls.length > 0) {
          iterations++;
          // Execute the tools
          const toolOutputs = await response.executeTools();

          // Verify tool outputs
          expect(toolOutputs.length).toBe(response.toolCalls.length);
          for (const output of toolOutputs) {
            expect(output.type).toBe("tool_output");
            expect(output.error).toBeNull();
          }

          // Resume with tool outputs - returns StreamResponse to continue streaming
          response = await response.resume(toolOutputs);

          // Consume the resumed stream
          await response.consume();
        }

        s.setResponse(response);
        s.set("toolIterations", iterations);

        // Verify the final response mentions the secrets
        const text = response.text();
        expect(text).toMatch(/moria/i);
        expect(text).toMatch(/life before death/i);
      });

      expect(snap.toObject()).toMatchSnapshot();
    },
  );
});
