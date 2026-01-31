/**
 * E2E tests for LLM call with parse error recovery.
 *
 * Tests verify that ParseError recovery works with retry_message.
 */

import { resolve } from "node:path";

import type { ProviderConfig } from "@/tests/e2e/providers";

import { defineCall } from "@/llm/calls";
import { ParseError } from "@/llm/exceptions";
import { defineOutputParser } from "@/llm/formatting/output-parser";
import { createIt, describe, expect, snapshotTest } from "@/tests/e2e/utils";

const it = createIt(resolve(__dirname, "cassettes"), "parse-error");

/**
 * Output parser that extracts a passphrase and throws if incorrect.
 */
const extractPassphrase = defineOutputParser<string>({
  formattingInstructions: "Respond with a single word: the passphrase.",
  parser: (response) => {
    const text = response.text().trim().toLowerCase();
    if (text !== "cake") {
      throw new Error("Incorrect passphrase. The correct passphrase is 'cake'");
    }
    return "the cake is a lie";
  },
});

/**
 * Providers for parse error tests.
 * We test on a subset since behavior is largely model-agnostic.
 */
const PARSE_ERROR_PROVIDERS: ProviderConfig[] = [
  { providerId: "anthropic", model: "anthropic/claude-haiku-4-5" },
];

describe("parse error handling", () => {
  it.record.each(PARSE_ERROR_PROVIDERS)(
    "recovers from parse errors with retry",
    async ({ model }) => {
      const getPassphrase = defineCall({
        model,
        maxTokens: 100,
        format: extractPassphrase,
        template: () => "Find out the secret and report back.",
      });

      const maxRetries = 3;

      const snap = await snapshotTest(
        async (s) => {
          let response = await getPassphrase();
          const attempts: Array<{ text: string; error?: string }> = [];

          for (let attempt = 0; attempt < maxRetries; attempt++) {
            try {
              const result = response.parse();
              attempts.push({ text: response.text(), error: undefined });
              s.set("result", result);
              break;
            } catch (e) {
              if (!(e instanceof ParseError)) {
                throw e;
              }
              attempts.push({
                text: response.text(),
                error: e.message,
              });

              if (attempt === maxRetries - 1) {
                throw e;
              }

              // Retry with the error message
              response = await response.resume(e.retryMessage());
            }
          }

          s.set("attempts", attempts);
          s.setResponse(response);
        },
        { extraExceptions: [ParseError] },
      );

      expect(snap.toObject()).toMatchSnapshot();
    },
    60000,
  );
});
