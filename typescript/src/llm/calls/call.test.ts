import { describe, expect, it } from 'vitest';
import { defineCall } from '@/llm/calls/call';
import { Model } from '@/llm/models';
import { system, user } from '@/llm/messages';

describe('defineCall', () => {
  describe('with variables', () => {
    it('creates a call with messages method', () => {
      const recommendBook = defineCall<{ genre: string }>({
        model: 'anthropic/claude-sonnet-4-20250514',
        template: ({ genre }) => `Recommend a ${genre} book`,
      });

      const messages = recommendBook.prompt.messages({ genre: 'fantasy' });

      expect(messages).toHaveLength(1);
      expect(messages[0]).toMatchObject({
        role: 'user',
        content: [{ type: 'text', text: 'Recommend a fantasy book' }],
      });
    });

    it('stores the model', () => {
      const call = defineCall<{ name: string }>({
        model: 'anthropic/claude-sonnet-4-20250514',
        template: ({ name }) => `Hello, ${name}!`,
      });

      expect(call.model).toBeInstanceOf(Model);
      expect(call.model.modelId).toBe('anthropic/claude-sonnet-4-20250514');
    });

    it('stores the template function', () => {
      const template = ({ name }: { name: string }) => `Hello, ${name}!`;
      const call = defineCall<{ name: string }>({
        model: 'anthropic/claude-sonnet-4-20250514',
        template,
      });

      expect(call.template).toBe(template);
    });

    it('exposes the underlying prompt', () => {
      const call = defineCall<{ name: string }>({
        model: 'anthropic/claude-sonnet-4-20250514',
        template: ({ name }) => `Hello, ${name}!`,
      });

      expect(call.prompt).toBeDefined();
      expect(call.prompt.messages({ name: 'World' })).toHaveLength(1);
    });

    it('supports message arrays', () => {
      const chatBot = defineCall<{ question: string }>({
        model: 'anthropic/claude-sonnet-4-20250514',
        template: ({ question }) => [
          system('You are helpful.'),
          user(question),
        ],
      });

      const messages = chatBot.prompt.messages({
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
      const call = defineCall<{ topic: string }>({
        model,
        template: ({ topic }) => `Write about ${topic}`,
      });

      expect(call.model).toBe(model);
      expect(call.model.params).toEqual({ temperature: 0.7 });
    });

    it('accepts params as top-level properties', () => {
      const call = defineCall<{ query: string }>({
        model: 'anthropic/claude-sonnet-4-20250514',
        temperature: 0,
        maxTokens: 100,
        template: ({ query }) => query,
      });

      expect(call.model.params).toEqual({ temperature: 0, maxTokens: 100 });
    });

    it('throws when passing params with Model instance', () => {
      const model = new Model('anthropic/claude-sonnet-4-20250514');

      expect(() =>
        defineCall<{ query: string }>({
          model,
          temperature: 0.5,
          template: ({ query }) => query,
        })
      ).toThrow(
        'Cannot pass params when model is a Model instance. Use new Model(id, params) instead.'
      );
    });

    it('has a stream method', () => {
      const call = defineCall<{ genre: string }>({
        model: 'anthropic/claude-sonnet-4-20250514',
        template: ({ genre }) => `Recommend a ${genre} book`,
      });

      expect(typeof call.stream).toBe('function');
    });
  });

  describe('without variables', () => {
    it('creates a call that can be called without vars', () => {
      const sayHello = defineCall({
        model: 'anthropic/claude-sonnet-4-20250514',
        template: () => 'Hello!',
      });

      const messages = sayHello.prompt.messages();

      expect(messages).toHaveLength(1);
      expect(messages[0]).toMatchObject({
        role: 'user',
        content: [{ type: 'text', text: 'Hello!' }],
      });
    });

    it('supports message arrays without variables', () => {
      const call = defineCall({
        model: 'anthropic/claude-sonnet-4-20250514',
        template: () => [
          system('You are a helpful assistant.'),
          user('What can you do?'),
        ],
      });

      const messages = call.prompt.messages();

      expect(messages).toHaveLength(2);
    });

    it('accepts params without variables', () => {
      const call = defineCall({
        model: 'anthropic/claude-sonnet-4-20250514',
        temperature: 0.5,
        template: () => 'Hello!',
      });

      expect(call.model.params).toEqual({ temperature: 0.5 });
    });

    it('has a stream method', () => {
      const call = defineCall({
        model: 'anthropic/claude-sonnet-4-20250514',
        template: () => 'Hello!',
      });

      expect(typeof call.stream).toBe('function');
    });
  });
});
