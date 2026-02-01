import { describe, expect, it } from 'vitest';
import { createContext, type Context } from '@/llm/context';
import { defineContextPrompt } from '@/llm/prompts/context-prompt';
import { system, user } from '@/llm/messages';

interface TestDeps {
  userId: string;
  userName: string;
}

describe('defineContextPrompt', () => {
  describe('with variables', () => {
    it('creates a prompt with messages method', () => {
      const greetUser = defineContextPrompt<{ greeting: string }, TestDeps>({
        template: ({ ctx, greeting }) =>
          `${greeting}, ${ctx.deps.userName}! (ID: ${ctx.deps.userId})`,
      });

      const ctx = createContext<TestDeps>({ userId: '123', userName: 'Alice' });
      const messages = greetUser.messages(ctx, { greeting: 'Hello' });

      expect(messages).toHaveLength(1);
      expect(messages[0]).toMatchObject({
        role: 'user',
        content: [{ type: 'text', text: 'Hello, Alice! (ID: 123)' }],
      });
    });

    it('stores the template function', () => {
      const template = ({
        ctx,
        name,
      }: {
        ctx: Context<TestDeps>;
        name: string;
      }) => `Hello, ${name} from ${ctx.deps.userId}!`;
      const greet = defineContextPrompt<{ name: string }, TestDeps>({
        template,
      });

      expect(greet.template).toBe(template);
    });

    it('has a stream method', () => {
      const prompt = defineContextPrompt<{ greeting: string }, TestDeps>({
        template: ({ ctx, greeting }) => `${greeting}, ${ctx.deps.userName}!`,
      });

      expect(typeof prompt.stream).toBe('function');
    });

    it('has a call method', () => {
      const prompt = defineContextPrompt<{ greeting: string }, TestDeps>({
        template: ({ ctx, greeting }) => `${greeting}, ${ctx.deps.userName}!`,
      });

      expect(typeof prompt.call).toBe('function');
    });

    it('supports message arrays', () => {
      interface SystemDeps {
        systemPrompt: string;
      }

      const chatBot = defineContextPrompt<{ question: string }, SystemDeps>({
        template: ({ ctx, question }) => [
          system(ctx.deps.systemPrompt),
          user(question),
        ],
      });

      const ctx = createContext<SystemDeps>({
        systemPrompt: 'You are a helpful assistant.',
      });
      const messages = chatBot.messages(ctx, {
        question: 'What is TypeScript?',
      });

      expect(messages).toHaveLength(2);
      expect(messages[0]).toMatchObject({
        role: 'system',
        content: { type: 'text', text: 'You are a helpful assistant.' },
      });
      expect(messages[1]).toMatchObject({
        role: 'user',
        content: [{ type: 'text', text: 'What is TypeScript?' }],
      });
    });

    it('supports multiple variables', () => {
      const prompt = defineContextPrompt<
        { author: string; genre: string },
        TestDeps
      >({
        template: ({ ctx, author, genre }) =>
          `${ctx.deps.userName} wants a ${genre} book by ${author}`,
      });

      const ctx = createContext<TestDeps>({ userId: '123', userName: 'Bob' });
      const messages = prompt.messages(ctx, {
        author: 'Tolkien',
        genre: 'fantasy',
      });

      expect(messages[0]).toMatchObject({
        role: 'user',
        content: [
          { type: 'text', text: 'Bob wants a fantasy book by Tolkien' },
        ],
      });
    });

    it('can access nested deps', () => {
      interface NestedDeps {
        user: {
          id: string;
          profile: {
            name: string;
          };
        };
      }

      const prompt = defineContextPrompt<{ greeting: string }, NestedDeps>({
        template: ({ ctx, greeting }) =>
          `${greeting}, ${ctx.deps.user.profile.name}!`,
      });

      const ctx = createContext<NestedDeps>({
        user: { id: '123', profile: { name: 'Alice' } },
      });
      const messages = prompt.messages(ctx, { greeting: 'Hi' });

      expect(messages[0]).toMatchObject({
        role: 'user',
        content: [{ type: 'text', text: 'Hi, Alice!' }],
      });
    });
  });

  describe('without variables', () => {
    it('creates a prompt that can be called without vars', () => {
      const sayHello = defineContextPrompt<TestDeps>({
        template: ({ ctx }) => `Hello, ${ctx.deps.userName}!`,
      });

      const ctx = createContext<TestDeps>({ userId: '123', userName: 'Alice' });
      const messages = sayHello.messages(ctx);

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

      const prompt = defineContextPrompt<SystemDeps>({
        template: ({ ctx }) => [
          system(ctx.deps.systemPrompt),
          user(ctx.deps.defaultQuestion),
        ],
      });

      const ctx = createContext<SystemDeps>({
        systemPrompt: 'You are helpful.',
        defaultQuestion: 'What can you do?',
      });
      const messages = prompt.messages(ctx);

      expect(messages).toHaveLength(2);
    });

    it('has a stream method', () => {
      const prompt = defineContextPrompt<TestDeps>({
        template: ({ ctx }) => `Hello, ${ctx.deps.userName}!`,
      });

      expect(typeof prompt.stream).toBe('function');
    });

    it('has a call method', () => {
      const prompt = defineContextPrompt<TestDeps>({
        template: ({ ctx }) => `Hello, ${ctx.deps.userName}!`,
      });

      expect(typeof prompt.call).toBe('function');
    });
  });
});
