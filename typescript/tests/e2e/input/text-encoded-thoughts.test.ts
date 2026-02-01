/**
 * E2E tests for LLM call with text-encoded thoughts.
 *
 * Tests verify that thought-as-text encoding works correctly
 * when passing assistant messages with thoughts back to the LLM.
 */

import { resolve } from "node:path";

import type { Thought } from "@/llm/content";
import type { Message } from "@/llm/messages";
import type { ProviderConfig } from "@/tests/e2e/providers";

import { defineCall } from "@/llm/calls";
import { system, user, assistant } from "@/llm/messages";
import { createIt, describe, expect, snapshotTest } from "@/tests/e2e/utils";

const it = createIt(resolve(__dirname, "cassettes"), "text-encoded-thoughts");

/**
 * Create a conversation with pre-filled thoughts in assistant message.
 *
 * This simulates a multi-turn conversation where the assistant's previous
 * response included thinking content that we want to pass back to the model.
 */
function createMessagesWithThoughts(model: string): Message[] {
  const thought: Thought = {
    type: "thought",
    thought: `Let me see... I have instantaneously remembered this table of fibonacci
numbers with their prime factorizations. That's sure convenient! Let
me see if it has the answer:
0 : 0
1 : 1
2 : 1
3 : 2
4 : 3
5 : 5
6 : 8 = 2^3
7 : 13
8 : 21 = 3 x 7
9 : 34 = 2 x 17
10 : 55 = 5 x 11
11 : 89
12 : 144 = 2^4 x 3^2
13 : 233
14 : 377 = 13 x 29
15 : 610 = 2 x 5 x 61
16 : 987 = 3 x 7 x 47
17 : 1597
18 : 2584 = 2^3 x 17 x 19
19 : 4181 = 37 x 113
20 : 6765 = 3 x 5 x 11 x 41
21 : 10946 = 2 x 13 x 421
22 : 17711 = 89 x 199
23 : 28657

There we have it! 28657 is the first fibonacci number ending in 57,
and it is prime. I'm supposed to answer with extreme concision, so I'll
just say 'Yes.'`,
  };

  return [
    system(
      "Always answer with extreme concision, giving the answer and no added context.",
    ),
    user("Is the first fibonacci number to end with the digits 57 prime?"),
    assistant([thought, { type: "text", text: "Yes." }], {
      modelId: model,
      providerId: "openai",
      rawMessage: { is_dummy_for_testing_purposes: true },
    }),
    user("Please tell me what the number is."),
  ];
}

/**
 * Providers for text-encoded thoughts tests.
 * Using thinking-capable models.
 *
 * Note: OpenAI is excluded because o4-mini doesn't support "minimal" thinking level.
 * It only supports: "low", "medium", "high".
 */
const TEXT_ENCODED_THOUGHTS_PROVIDERS: ProviderConfig[] = [
  { providerId: "anthropic", model: "anthropic/claude-sonnet-4-20250514" },
  { providerId: "google", model: "google/gemini-2.5-flash" },
];

describe("text encoded thoughts", () => {
  it.record.each(TEXT_ENCODED_THOUGHTS_PROVIDERS)(
    "encodes thoughts as text for model consumption",
    async ({ model }) => {
      const callWithThoughts = defineCall({
        model,
        maxTokens: 500,
        thinking: {
          level: "minimal",
          encodeThoughtsAsText: true,
        },
        template: () => createMessagesWithThoughts(model),
      });

      const snap = await snapshotTest(async (s) => {
        const response = await callWithThoughts();
        s.setResponse(response);

        // The model should be able to read the thoughts and know the answer is 28657
        const text = response.text();
        expect(text).toContain("28657");
      });

      expect(snap.toObject()).toMatchSnapshot();
    },
    60000,
  );
});
