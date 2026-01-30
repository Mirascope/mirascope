import { describe, expect, it } from 'vitest';
import { createContext, type Context } from '@/llm/context';
import { definePrompt } from '@/llm/prompts/prompt';
import { system, user } from '@/llm/messages';

interface TestDeps {
  userId: string;
  userName: string;
}

describe('definePrompt (context-aware)', () => {
  describe('with variables', () => {
    it('creates a prompt with messages method', () => {
      const greetUser = definePrompt<{
        ctx: Context<TestDeps>;
        greeting: string;
      }>({
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
      const greet = definePrompt<{ ctx: Context<TestDeps>; name: string }>({
        template,
      });

      expect(greet.template).toBe(template);
    });

    it('has a stream method', () => {
      const prompt = definePrompt<{
        ctx: Context<TestDeps>;
        greeting: string;
      }>({
        template: ({ ctx, greeting }) => `${greeting}, ${ctx.deps.userName}!`,
      });

      expect(typeof prompt.stream).toBe('function');
    });

    it('has a call method', () => {
      const prompt = definePrompt<{
        ctx: Context<TestDeps>;
        greeting: string;
      }>({
        template: ({ ctx, greeting }) => `${greeting}, ${ctx.deps.userName}!`,
      });

      expect(typeof prompt.call).toBe('function');
    });

    it('supports message arrays', () => {
      interface SystemDeps {
        systemPrompt: string;
      }

      const chatBot = definePrompt<{
        ctx: Context<SystemDeps>;
        question: string;
      }>({
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
      const prompt = definePrompt<{
        ctx: Context<TestDeps>;
        author: string;
        genre: string;
      }>({
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

      const prompt = definePrompt<{
        ctx: Context<NestedDeps>;
        greeting: string;
      }>({
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
      const sayHello = definePrompt<{ ctx: Context<TestDeps> }>({
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

      const prompt = definePrompt<{ ctx: Context<SystemDeps> }>({
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
      const prompt = definePrompt<{ ctx: Context<TestDeps> }>({
        template: ({ ctx }) => `Hello, ${ctx.deps.userName}!`,
      });

      expect(typeof prompt.stream).toBe('function');
    });

    it('has a call method', () => {
      const prompt = definePrompt<{ ctx: Context<TestDeps> }>({
        template: ({ ctx }) => `Hello, ${ctx.deps.userName}!`,
      });

      expect(typeof prompt.call).toBe('function');
    });

    it('supports zero-arity template with context type', () => {
      // Edge case: template takes no args but context type is specified
      // This tests the template.length === 0 branch in context handling
      const prompt = definePrompt<{ ctx: Context<TestDeps> }>({
        template: () => 'Static message',
      });

      const ctx = createContext<TestDeps>({ userId: '123', userName: 'Alice' });
      const messages = prompt.messages(ctx);

      expect(messages).toHaveLength(1);
      expect(messages[0]).toMatchObject({
        role: 'user',
        content: [{ type: 'text', text: 'Static message' }],
      });
    });
  });
});
