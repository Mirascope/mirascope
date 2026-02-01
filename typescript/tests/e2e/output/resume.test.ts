/**
 * E2E tests for LLM resume functionality.
 *
 * These tests verify that conversations can be continued using response.resume().
 * Tests run against multiple providers via parameterization.
 */

import { resolve } from 'node:path';
import { createIt, describe, expect } from '@/tests/e2e/utils';
import { PROVIDERS } from '@/tests/e2e/providers';
import { defineCall, defineContextCall } from '@/llm/calls';
import { createContext } from '@/llm/context';

const it = createIt(resolve(__dirname, 'cassettes'), 'resume');

describe('resume from call', () => {
  it.record.each(PROVIDERS)(
    'resumes conversation with new content',
    async ({ model }) => {
      const call = defineCall({
        model,
        maxTokens: 500,
        template: () => 'Say exactly: "Hello"',
      });

      const response = await call();
      expect(response.text()).toMatch(/hello/i);

      // Resume the conversation
      const followUp = await response.resume('Now say exactly: "Goodbye"');

      expect(followUp.text()).toMatch(/goodbye/i);
      // Messages should include the original exchange plus the follow-up
      expect(followUp.messages.length).toBe(4); // user, assistant, user, assistant
    }
  );

  it.record.each(PROVIDERS)(
    'resumeStream returns streaming response',
    async ({ model }) => {
      const call = defineCall({
        model,
        maxTokens: 500,
        template: () => 'Say exactly: "Hello"',
      });

      const response = await call();
      expect(response.text()).toMatch(/hello/i);

      // Resume with streaming
      const followUp = await response.resumeStream(
        'Now say exactly: "Goodbye"'
      );

      const chunks: string[] = [];
      for await (const text of followUp.textStream()) {
        chunks.push(text);
      }

      expect(chunks.length).toBeGreaterThan(0);
      expect(followUp.text()).toMatch(/goodbye/i);
      expect(followUp.messages.length).toBe(4);
    }
  );
});

describe('resume from stream', () => {
  it.record.each(PROVIDERS)(
    'resumes conversation after streaming',
    async ({ model }) => {
      const call = defineCall({
        model,
        maxTokens: 500,
        template: () => 'Say exactly: "Hello"',
      });

      const streamResponse = await call.stream();

      // Consume the stream first
      for await (const _ of streamResponse.textStream()) {
        // Just consume
      }

      expect(streamResponse.text()).toMatch(/hello/i);

      // Resume the conversation
      const followUp = await streamResponse.resume(
        'Now say exactly: "Goodbye"'
      );

      expect(followUp.text()).toMatch(/goodbye/i);
      expect(followUp.messages.length).toBe(4);
    }
  );

  it.record.each(PROVIDERS)(
    'resumeStream from stream returns streaming response',
    async ({ model }) => {
      const call = defineCall({
        model,
        maxTokens: 500,
        template: () => 'Say exactly: "Hello"',
      });

      const streamResponse = await call.stream();

      // Consume the stream first
      for await (const _ of streamResponse.textStream()) {
        // Just consume
      }

      expect(streamResponse.text()).toMatch(/hello/i);

      // Resume with streaming
      const followUp = await streamResponse.resumeStream(
        'Now say exactly: "Goodbye"'
      );

      const chunks: string[] = [];
      for await (const text of followUp.textStream()) {
        chunks.push(text);
      }

      expect(chunks.length).toBeGreaterThan(0);
      expect(followUp.text()).toMatch(/goodbye/i);
      expect(followUp.messages.length).toBe(4);
    }
  );
});

interface TestDeps {
  greeting: string;
}

describe('context resume from call', () => {
  it.record.each(PROVIDERS)(
    'resumes context conversation with new content',
    async ({ model }) => {
      const call = defineContextCall<TestDeps>({
        model,
        maxTokens: 500,
        template: ({ ctx }) => `Say exactly: "${ctx.deps.greeting}"`,
      });

      const ctx = createContext<TestDeps>({ greeting: 'Hello' });
      const response = await call(ctx);
      expect(response.text()).toMatch(/hello/i);

      // Resume the conversation with context
      const followUp = await response.resume(ctx, 'Now say exactly: "Goodbye"');

      expect(followUp.text()).toMatch(/goodbye/i);
      expect(followUp.messages.length).toBe(4);
    }
  );

  it.record.each(PROVIDERS)(
    'context resumeStream returns streaming response',
    async ({ model }) => {
      const call = defineContextCall<TestDeps>({
        model,
        maxTokens: 500,
        template: ({ ctx }) => `Say exactly: "${ctx.deps.greeting}"`,
      });

      const ctx = createContext<TestDeps>({ greeting: 'Hello' });
      const response = await call(ctx);
      expect(response.text()).toMatch(/hello/i);

      // Resume with streaming
      const followUp = await response.resumeStream(
        ctx,
        'Now say exactly: "Goodbye"'
      );

      const chunks: string[] = [];
      for await (const text of followUp.textStream()) {
        chunks.push(text);
      }

      expect(chunks.length).toBeGreaterThan(0);
      expect(followUp.text()).toMatch(/goodbye/i);
      expect(followUp.messages.length).toBe(4);
    }
  );
});

describe('context resume from stream', () => {
  it.record.each(PROVIDERS)(
    'resumes context conversation after streaming',
    async ({ model }) => {
      const call = defineContextCall<TestDeps>({
        model,
        maxTokens: 500,
        template: ({ ctx }) => `Say exactly: "${ctx.deps.greeting}"`,
      });

      const ctx = createContext<TestDeps>({ greeting: 'Hello' });
      const streamResponse = await call.stream(ctx);

      // Consume the stream first
      for await (const _ of streamResponse.textStream()) {
        // Just consume
      }

      expect(streamResponse.text()).toMatch(/hello/i);

      // Resume the conversation with context
      const followUp = await streamResponse.resume(
        ctx,
        'Now say exactly: "Goodbye"'
      );

      expect(followUp.text()).toMatch(/goodbye/i);
      expect(followUp.messages.length).toBe(4);
    }
  );

  it.record.each(PROVIDERS)(
    'context resumeStream from stream returns streaming response',
    async ({ model }) => {
      const call = defineContextCall<TestDeps>({
        model,
        maxTokens: 500,
        template: ({ ctx }) => `Say exactly: "${ctx.deps.greeting}"`,
      });

      const ctx = createContext<TestDeps>({ greeting: 'Hello' });
      const streamResponse = await call.stream(ctx);

      // Consume the stream first
      for await (const _ of streamResponse.textStream()) {
        // Just consume
      }

      expect(streamResponse.text()).toMatch(/hello/i);

      // Resume with streaming
      const followUp = await streamResponse.resumeStream(
        ctx,
        'Now say exactly: "Goodbye"'
      );

      const chunks: string[] = [];
      for await (const text of followUp.textStream()) {
        chunks.push(text);
      }

      expect(chunks.length).toBeGreaterThan(0);
      expect(followUp.text()).toMatch(/goodbye/i);
      expect(followUp.messages.length).toBe(4);
    }
  );
});
