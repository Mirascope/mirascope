/**
 * E2E tests for LLM tool usage.
 *
 * These tests verify we correctly encode tools in requests and decode
 * tool calls from responses. Tests run against multiple providers via parameterization.
 */

import { resolve } from 'node:path';
import { createIt, describe, expect } from '@/tests/e2e/utils';
import { PROVIDERS_FOR_TOOLS_TESTS } from '@/tests/e2e/providers';
import { Model, defineTool, type Response, type StreamResponse } from '@/llm';

const it = createIt(resolve(__dirname, 'cassettes'), 'tools');

/**
 * Password map for the secret retrieval tool.
 */
const PASSWORD_MAP: Record<string, string> = {
  mellon: 'Welcome to Moria!',
  radiance: 'Life before Death',
};

/**
 * A simple tool for testing that retrieves secrets based on passwords.
 *
 * Note: The __schema is provided explicitly here because the TypeScript
 * transformer is not yet integrated into the test build process. In
 * production usage, __schema would be injected by the transformer.
 */
const secretRetrievalTool = defineTool<{ password: string }>({
  name: 'secret_retrieval_tool',
  description: 'A tool that requires a password to retrieve a secret.',
  fieldDefinitions: {
    password: 'The password to retrieve the secret for.',
  },
  tool: ({ password }) => {
    return PASSWORD_MAP[password] ?? 'Invalid password!';
  },
  __schema: {
    type: 'object',
    properties: {
      password: {
        type: 'string',
        description: 'The password to retrieve the secret for.',
      },
    },
    required: ['password'],
    additionalProperties: false,
  },
});

describe('tool usage', () => {
  it.record.each(PROVIDERS_FOR_TOOLS_TESTS)(
    'calls tool and resumes with results',
    async ({ model: modelId }) => {
      const model = new Model(modelId, { maxTokens: 1000 });

      // Call with tool - ask LLM to use the tool
      let response: Response = await model.call(
        'Please retrieve the secrets for these passwords: "mellon" and "radiance". ' +
          'Use the secret_retrieval_tool for each password.',
        [secretRetrievalTool]
      );

      // Verify we got tool calls
      expect(response.toolCalls.length).toBeGreaterThanOrEqual(1);

      // Loop until no more tool calls (some providers like Google call tools sequentially)
      while (response.toolCalls.length > 0) {
        // Execute the tools
        const toolOutputs = await response.executeTools();

        // Verify tool outputs
        expect(toolOutputs.length).toBe(response.toolCalls.length);
        for (const output of toolOutputs) {
          expect(output.type).toBe('tool_output');
          expect(output.error).toBeNull();
        }

        // Resume with tool outputs
        response = await response.resume(toolOutputs);
      }

      // Verify the final response mentions the secrets
      const text = response.text();
      expect(text).toMatch(/moria/i);
      expect(text).toMatch(/life before death/i);
    }
  );
});

// TODO: Enable once streaming tool support is implemented in provider decoders.
// Currently, the provider decoders (anthropic, openai, google) don't emit
// tool_call chunks during streaming - they only handle text content.
// See: decode-stream.ts in each provider directory.
describe.skip('tool usage with streaming', () => {
  it.record.each(PROVIDERS_FOR_TOOLS_TESTS)(
    'streams tool calls and resumes with results',
    async ({ model: modelId }) => {
      const model = new Model(modelId, { maxTokens: 1000 });

      // Stream with tool - ask LLM to use the tool
      let response: StreamResponse = await model.stream(
        'Please retrieve the secrets for these passwords: "mellon" and "radiance". ' +
          'Use the secret_retrieval_tool for each password.',
        [secretRetrievalTool]
      );

      // Consume the stream (equivalent to Python's response.finish())
      await response.consume();

      // Verify we got tool calls
      expect(response.toolCalls.length).toBeGreaterThanOrEqual(1);

      // Loop until no more tool calls (some providers like Google call tools sequentially)
      while (response.toolCalls.length > 0) {
        // Execute the tools
        const toolOutputs = await response.executeTools();

        // Verify tool outputs
        expect(toolOutputs.length).toBe(response.toolCalls.length);
        for (const output of toolOutputs) {
          expect(output.type).toBe('tool_output');
          expect(output.error).toBeNull();
        }

        // Resume with tool outputs using resumeStream to continue streaming
        response = await response.resumeStream(toolOutputs);

        // Consume the resumed stream
        await response.consume();
      }

      // Verify the final response mentions the secrets
      const text = response.text();
      expect(text).toMatch(/moria/i);
      expect(text).toMatch(/life before death/i);
    }
  );
});
