import { describe, expect, it } from 'vitest';
import { createContext, type Context } from '@/llm/context';
import { defineContextCall } from '@/llm/calls/context-call';
import { Model } from '@/llm/models';
import { system, user } from '@/llm/messages';

interface TestDeps {
  userId: string;
  userName: string;
}

describe('defineContextCall', () => {
  describe('with variables', () => {
    it('creates a call with messages method', () => {
      const greetUser = defineContextCall<{ greeting: string }, TestDeps>({
        model: 'anthropic/claude-sonnet-4-20250514',
        template: ({ ctx, greeting }) =>
          `${greeting}, ${ctx.deps.userName}! (ID: ${ctx.deps.userId})`,
      });

      const ctx = createContext<TestDeps>({ userId: '123', userName: 'Alice' });
      const messages = greetUser.prompt.messages(ctx, { greeting: 'Hello' });

      expect(messages).toHaveLength(1);
      expect(messages[0]).toMatchObject({
        role: 'user',
        content: [{ type: 'text', text: 'Hello, Alice! (ID: 123)' }],
      });
    });

    it('stores the model', () => {
      const call = defineContextCall<{ name: string }, TestDeps>({
        model: 'anthropic/claude-sonnet-4-20250514',
        template: ({ ctx, name }) => `Hello, ${name} from ${ctx.deps.userId}!`,
      });

      expect(call.model).toBeInstanceOf(Model);
      expect(call.model.modelId).toBe('anthropic/claude-sonnet-4-20250514');
    });

    it('stores the template function', () => {
      const template = ({
        ctx,
        name,
      }: {
        ctx: Context<TestDeps>;
        name: string;
      }) => `Hello, ${name} from ${ctx.deps.userId}!`;
      const call = defineContextCall<{ name: string }, TestDeps>({
        model: 'anthropic/claude-sonnet-4-20250514',
        template,
      });

      expect(call.template).toBe(template);
    });

    it('exposes the underlying prompt', () => {
      const call = defineContextCall<{ name: string }, TestDeps>({
        model: 'anthropic/claude-sonnet-4-20250514',
        template: ({ ctx, name }) => `Hello, ${name} from ${ctx.deps.userId}!`,
      });

      const ctx = createContext<TestDeps>({ userId: '123', userName: 'Alice' });

      expect(call.prompt).toBeDefined();
      expect(call.prompt.messages(ctx, { name: 'World' })).toHaveLength(1);
    });

    it('supports message arrays', () => {
      interface SystemDeps {
        systemPrompt: string;
      }

      const chatBot = defineContextCall<{ question: string }, SystemDeps>({
        model: 'anthropic/claude-sonnet-4-20250514',
        template: ({ ctx, question }) => [
          system(ctx.deps.systemPrompt),
          user(question),
        ],
      });

      const ctx = createContext<SystemDeps>({
        systemPrompt: 'You are helpful.',
      });
      const messages = chatBot.prompt.messages(ctx, {
        question: 'What is TypeScript?',
      });

      expect(messages).toHaveLength(2);
      expect(messages[0]).toMatchObject({ role: 'system' });
      expect(messages[1]).toMatchObject({
        role: 'user',
        content: [{ type: 'text', text: 'What is TypeScript?' }],
      });
    });

    it('accepts a Model instance', () => {
      const model = new Model('anthropic/claude-sonnet-4-20250514', {
        temperature: 0.7,
      });
      const call = defineContextCall<{ topic: string }, TestDeps>({
        model,
        template: ({ ctx, topic }) =>
          `Write about ${topic} for ${ctx.deps.userName}`,
      });

      expect(call.model).toBe(model);
      expect(call.model.params).toEqual({ temperature: 0.7 });
    });

    it('accepts params as top-level properties', () => {
      const call = defineContextCall<{ query: string }, TestDeps>({
        model: 'anthropic/claude-sonnet-4-20250514',
        temperature: 0,
        maxTokens: 100,
        template: ({ ctx, query }) => `${ctx.deps.userName}: ${query}`,
      });

      expect(call.model.params).toEqual({ temperature: 0, maxTokens: 100 });
    });

    it('throws when passing params with Model instance', () => {
      const model = new Model('anthropic/claude-sonnet-4-20250514');

      expect(() =>
        defineContextCall<{ query: string }, TestDeps>({
          model,
          temperature: 0.5,
          template: ({ ctx, query }) => `${ctx.deps.userName}: ${query}`,
        })
      ).toThrow(
        'Cannot pass params when model is a Model instance. Use new Model(id, params) instead.'
      );
    });

    it('has a stream method', () => {
      const call = defineContextCall<{ greeting: string }, TestDeps>({
        model: 'anthropic/claude-sonnet-4-20250514',
        template: ({ ctx, greeting }) => `${greeting}, ${ctx.deps.userName}!`,
      });

      expect(typeof call.stream).toBe('function');
    });

    it('has a call method', () => {
      const call = defineContextCall<{ greeting: string }, TestDeps>({
        model: 'anthropic/claude-sonnet-4-20250514',
        template: ({ ctx, greeting }) => `${greeting}, ${ctx.deps.userName}!`,
      });

      expect(typeof call.call).toBe('function');
    });
  });

  describe('without variables', () => {
    it('creates a call that can be called without vars', () => {
      const sayHello = defineContextCall<TestDeps>({
        model: 'anthropic/claude-sonnet-4-20250514',
        template: ({ ctx }) => `Hello, ${ctx.deps.userName}!`,
      });

      const ctx = createContext<TestDeps>({ userId: '123', userName: 'Alice' });
      const messages = sayHello.prompt.messages(ctx);

      expect(messages).toHaveLength(1);
      expect(messages[0]).toMatchObject({
        role: 'user',
        content: [{ type: 'text', text: 'Hello, Alice!' }],
      });
    });

    it('supports message arrays without variables', () => {
      interface SystemDeps {
        systemPrompt: string;
        defaultQuestion: string;
      }

      const call = defineContextCall<SystemDeps>({
        model: 'anthropic/claude-sonnet-4-20250514',
        template: ({ ctx }) => [
          system(ctx.deps.systemPrompt),
          user(ctx.deps.defaultQuestion),
        ],
      });

      const ctx = createContext<SystemDeps>({
        systemPrompt: 'You are helpful.',
        defaultQuestion: 'What can you do?',
      });
      const messages = call.prompt.messages(ctx);

      expect(messages).toHaveLength(2);
    });

    it('accepts params without variables', () => {
      const call = defineContextCall<TestDeps>({
        model: 'anthropic/claude-sonnet-4-20250514',
        temperature: 0.5,
        template: ({ ctx }) => `Hello, ${ctx.deps.userName}!`,
      });

      expect(call.model.params).toEqual({ temperature: 0.5 });
    });

    it('has a stream method', () => {
      const call = defineContextCall<TestDeps>({
        model: 'anthropic/claude-sonnet-4-20250514',
        template: ({ ctx }) => `Hello, ${ctx.deps.userName}!`,
      });

      expect(typeof call.stream).toBe('function');
    });

    it('has a call method', () => {
      const call = defineContextCall<TestDeps>({
        model: 'anthropic/claude-sonnet-4-20250514',
        template: ({ ctx }) => `Hello, ${ctx.deps.userName}!`,
      });

      expect(typeof call.call).toBe('function');
    });
  });
});
