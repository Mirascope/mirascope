import { describe, expect, it } from 'vitest';
import { createContext, type Context } from '@/llm/context/context';

describe('createContext', () => {
  it('creates a context with deps', () => {
    const deps = { userId: '123', name: 'Alice' };
    const ctx = createContext(deps);

    expect(ctx.deps).toBe(deps);
    expect(ctx.deps.userId).toBe('123');
    expect(ctx.deps.name).toBe('Alice');
  });

  it('creates a typed context', () => {
    interface MyDeps {
      userId: string;
      db: { query: () => string };
    }

    const db = { query: () => 'result' };
    const ctx = createContext<MyDeps>({ userId: '123', db });

    expect(ctx.deps.userId).toBe('123');
    expect(ctx.deps.db.query()).toBe('result');
  });

  it('creates a context with empty deps', () => {
    const ctx = createContext({});

    expect(ctx.deps).toEqual({});
  });

  it('creates a context with primitive deps', () => {
    const ctx = createContext('simple-string');

    expect(ctx.deps).toBe('simple-string');
  });

  it('returns a readonly context structure', () => {
    interface MyDeps {
      value: number;
    }

    const ctx: Context<MyDeps> = createContext({ value: 42 });

    // TypeScript enforces readonly - runtime check that structure is as expected
    expect(ctx).toHaveProperty('deps');
    expect(ctx.deps.value).toBe(42);
  });
});
