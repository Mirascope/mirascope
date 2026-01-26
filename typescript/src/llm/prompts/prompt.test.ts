import { describe, expect, it } from 'vitest';
import { definePrompt } from '@/llm/prompts/prompt';
import { system, user } from '@/llm/messages';

describe('definePrompt', () => {
  describe('with variables', () => {
    it('creates a prompt with messages method', () => {
      const recommendBook = definePrompt<{ genre: string }>({
        template: ({ genre }) => `Recommend a ${genre} book`,
      });

      const messages = recommendBook.messages({ genre: 'fantasy' });

      expect(messages).toHaveLength(1);
      expect(messages[0]).toMatchObject({
        role: 'user',
        content: [{ type: 'text', text: 'Recommend a fantasy book' }],
      });
    });

    it('stores the template function', () => {
      const template = ({ name }: { name: string }) => `Hello, ${name}!`;
      const greet = definePrompt<{ name: string }>({ template });

      expect(greet.template).toBe(template);
    });

    it('has a stream method', () => {
      const prompt = definePrompt<{ genre: string }>({
        template: ({ genre }) => `Recommend a ${genre} book`,
      });

      expect(typeof prompt.stream).toBe('function');
    });

    it('supports message arrays', () => {
      const chatBot = definePrompt<{ question: string }>({
        template: ({ question }) => [
          system('You are helpful.'),
          user(question),
        ],
      });

      const messages = chatBot.messages({ question: 'What is TypeScript?' });

      expect(messages).toHaveLength(2);
      expect(messages[0]).toMatchObject({ role: 'system' });
      expect(messages[1]).toMatchObject({
        role: 'user',
        content: [{ type: 'text', text: 'What is TypeScript?' }],
      });
    });

    it('supports multiple variables', () => {
      const prompt = definePrompt<{ author: string; genre: string }>({
        template: ({ author, genre }) =>
          `Recommend a ${genre} book by ${author}`,
      });

      const messages = prompt.messages({ author: 'Tolkien', genre: 'fantasy' });

      expect(messages[0]).toMatchObject({
        role: 'user',
        content: [
          { type: 'text', text: 'Recommend a fantasy book by Tolkien' },
        ],
      });
    });
  });

  describe('without variables', () => {
    it('creates a prompt that can be called without vars', () => {
      const sayHello = definePrompt({
        template: () => 'Hello!',
      });

      const messages = sayHello.messages();

      expect(messages).toHaveLength(1);
      expect(messages[0]).toMatchObject({
        role: 'user',
        content: [{ type: 'text', text: 'Hello!' }],
      });
    });

    it('supports message arrays without variables', () => {
      const prompt = definePrompt({
        template: () => [
          system('You are a helpful assistant.'),
          user('What can you do?'),
        ],
      });

      const messages = prompt.messages();

      expect(messages).toHaveLength(2);
    });

    it('has a stream method', () => {
      const prompt = definePrompt({
        template: () => 'Hello!',
      });

      expect(typeof prompt.stream).toBe('function');
    });
  });
});
