/**
 * E2E tests for tool execution error handling.
 *
 * Tests verify that tool execution errors are properly captured
 * and can be used to retry the tool call.
 */

import { resolve } from "node:path";

import { defineCall, defineTool, type Response } from "@/llm";
import { PROVIDERS_FOR_TOOLS_TESTS } from "@/tests/e2e/providers";
import { createIt, describe, expect } from "@/tests/e2e/utils";

const it = createIt(resolve(__dirname, "cassettes"), "tool-error");

/**
 * A tool that validates a passphrase and throws if incorrect.
 */
const passphraseTestTool = defineTool<{ passphrase: string }>({
  name: "passphrase_test_tool",
  description: "A tool that must be called with the correct passphrase.",
  tool: ({ passphrase }) => {
    if (passphrase !== "cake") {
      throw new Error(
        "Incorrect passphrase: The correct passphrase is 'cake'. Try again.",
      );
    }
    return "The cake is a lie.";
  },
});

describe("tool error handling", () => {
  it.record.each(PROVIDERS_FOR_TOOLS_TESTS)(
    "handles tool execution errors and retries",
    async ({ model }) => {
      const useTestTool = defineCall({
        model,
        maxTokens: 1000,
        tools: [passphraseTestTool],
        template: () =>
          "Use the test tool to retrieve the secret phrase. The passphrase is 'portal'",
      });

      const allOutputs: Array<{
        name: string;
        result: string;
        error?: string;
      }> = [];

      let response: Response = await useTestTool();

      // Loop until no more tool calls (model should eventually figure out the passphrase)
      let iterations = 0;
      const maxIterations = 5;

      while (response.toolCalls.length > 0 && iterations < maxIterations) {
        const toolOutputs = await response.executeTools();
        for (const o of toolOutputs) {
          allOutputs.push({
            name: o.name,
            result: String(o.result),
            error: o.error?.message,
          });
        }

        // Resume with tool outputs (which include errors)
        response = await response.resume(toolOutputs);
        iterations++;
      }

      // The model should eventually get the correct passphrase
      expect(response.text().length).toBeGreaterThan(0);

      // Verify tool execution flow:
      // 1. First attempt with "portal" should fail
      // 2. Model should eventually get the secret phrase
      expect(allOutputs.length).toBeGreaterThanOrEqual(1);
      expect(allOutputs.some((o) => o.error)).toBe(true); // At least one error

      // The secret should be obtained either from tool output or mentioned in response
      const hasToolSuccess = allOutputs.some(
        (o) => o.result === "The cake is a lie.",
      );
      const hasResponseMention =
        response.text().toLowerCase().includes("cake") ||
        response.text().includes("The cake is a lie");
      expect(hasToolSuccess || hasResponseMention).toBe(true); // Eventually succeeds
    },
    60000, // Longer timeout for tool retry loops
  );
});
