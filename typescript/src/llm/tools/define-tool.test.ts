import { describe, expect, it, vi } from 'vitest';
import type { ToolCall } from '@/llm/content/tool-call';
import { createContext, type Context } from '@/llm/context';
import {
  defineTool,
  defineContextTool,
  isZodLike,
} from '@/llm/tools/define-tool';
import type { ZodLike } from '@/llm/tools/tools';
import { ToolExecutionError } from '@/llm/exceptions';

// Helper to create a mock ToolCall
function createToolCall(name: string, args: Record<string, unknown>): ToolCall {
  return {
    type: 'tool_call',
    id: 'test-id',
    name,
    args: JSON.stringify(args),
  };
}

// Mock Zod-like schema for testing
function createMockZodSchema(description?: string): ZodLike {
  return {
    _def: { description },
    safeParse: vi.fn((data: unknown) => ({
      success: true,
      data,
    })),
  };
}

describe('isZodLike', () => {
  it('returns true for Zod-like objects', () => {
    const zodLike = createMockZodSchema('test');
    expect(isZodLike(zodLike)).toBe(true);
  });

  it('returns false for strings', () => {
    expect(isZodLike('not a schema')).toBe(false);
  });

  it('returns false for null', () => {
    expect(isZodLike(null)).toBe(false);
  });

  it('returns false for objects without _def', () => {
    expect(isZodLike({ safeParse: vi.fn() })).toBe(false);
  });

  it('returns false for objects without safeParse', () => {
    expect(isZodLike({ _def: {} })).toBe(false);
  });
});

describe('defineTool', () => {
  it('creates a tool with correct properties', () => {
    const tool = defineTool<{ city: string; units?: string }>({
      name: 'get_weather',
      description: 'Get weather for a city',
      fieldDefinitions: {
        city: 'The city name',
        units: 'Temperature units',
      },
      tool: ({ city }) => ({ temp: 72, city }),
    });

    expect(tool.name).toBe('get_weather');
    expect(tool.description).toBe('Get weather for a city');
    expect(tool.parameters.properties.city?.description).toBe('The city name');
    expect(tool.parameters.properties.units?.description).toBe(
      'Temperature units'
    );
  });

  it('auto-generates schema from type parameter', () => {
    // This test verifies the transformer is working correctly
    const tool = defineTool<{ city: string; count?: number }>({
      name: 'test_tool',
      description: 'Test',
      tool: ({ city }) => city,
    });

    // Schema should be auto-generated with correct types
    expect(tool.parameters.type).toBe('object');
    expect(tool.parameters.properties.city?.type).toBe('string');
    expect(tool.parameters.properties.count?.type).toBe('number');
    expect(tool.parameters.required).toContain('city');
    expect(tool.parameters.required).not.toContain('count');
  });

  it('is callable with args (sync tool)', async () => {
    const tool = defineTool<{ city: string }>({
      name: 'get_weather',
      description: 'Get weather',
      tool: ({ city }) => ({ temp: 72, city }),
    });

    const result = await tool({ city: 'NYC' });
    expect(result).toEqual({ temp: 72, city: 'NYC' });
  });

  it('is callable with args (async tool)', async () => {
    const tool = defineTool<{ city: string }>({
      name: 'get_weather',
      description: 'Get weather',
      tool: async ({ city }) => {
        await Promise.resolve();
        return { temp: 72, city };
      },
    });

    const result = await tool({ city: 'NYC' });
    expect(result).toEqual({ temp: 72, city: 'NYC' });
  });

  it('executes from ToolCall successfully', async () => {
    const tool = defineTool<{ city: string }>({
      name: 'get_weather',
      description: 'Get weather',
      tool: ({ city }) => ({ temp: 72, city }),
    });

    const toolCall = createToolCall('get_weather', { city: 'NYC' });
    const output = await tool.execute(toolCall);

    expect(output.type).toBe('tool_output');
    expect(output.id).toBe('test-id');
    expect(output.name).toBe('get_weather');
    expect(output.result).toEqual({ temp: 72, city: 'NYC' });
    expect(output.error).toBeNull();
  });

  it('returns error output when tool throws', async () => {
    const tool = defineTool<{ city: string }>({
      name: 'get_weather',
      description: 'Get weather',
      tool: () => {
        throw new Error('API failed');
      },
    });

    const toolCall = createToolCall('get_weather', { city: 'NYC' });
    const output = await tool.execute(toolCall);

    expect(output.error).toBeInstanceOf(ToolExecutionError);
    expect(output.result).toBe('API failed');
  });

  it('handles non-Error thrown values', async () => {
    const tool = defineTool<{ city: string }>({
      name: 'get_weather',
      description: 'Get weather',
      tool: () => {
        // eslint-disable-next-line @typescript-eslint/only-throw-error
        throw 'string error';
      },
    });

    const toolCall = createToolCall('get_weather', { city: 'NYC' });
    const output = await tool.execute(toolCall);

    expect(output.error).toBeInstanceOf(ToolExecutionError);
    expect(output.result).toBe('string error');
  });

  it('validates with Zod-like schema', async () => {
    const safeParsespy = vi.fn((data: unknown) => ({
      success: true,
      data,
    }));
    const zodSchema: ZodLike = {
      _def: { description: 'The city name' },
      safeParse: safeParsespy,
    };

    const tool = defineTool<{ city: string }>({
      name: 'get_weather',
      description: 'Get weather',
      fieldDefinitions: {
        city: zodSchema,
      },
      tool: ({ city }) => ({ city }),
    });

    await tool({ city: 'NYC' });
    expect(safeParsespy).toHaveBeenCalledWith('NYC');
  });

  it('fails validation when Zod-like schema returns failure', async () => {
    const zodSchema: ZodLike = {
      _def: { description: 'The city name' },
      safeParse: vi.fn(() => ({
        success: false,
        error: { message: 'Invalid city' },
      })),
    };

    const tool = defineTool<{ city: string }>({
      name: 'get_weather',
      description: 'Get weather',
      fieldDefinitions: {
        city: zodSchema,
      },
      tool: ({ city }) => ({ city }),
    });

    const toolCall = createToolCall('get_weather', { city: '' });
    const output = await tool.execute(toolCall);

    expect(output.error).toBeInstanceOf(ToolExecutionError);
  });

  it('extracts description from Zod-like schema', () => {
    const zodSchema = createMockZodSchema('City from Zod');

    const tool = defineTool<{ city: string }>({
      name: 'get_weather',
      description: 'Get weather',
      fieldDefinitions: {
        city: zodSchema,
      },
      tool: ({ city }) => ({ city }),
    });

    expect(tool.parameters.properties.city?.description).toBe('City from Zod');
  });

  it('works without fieldDefinitions', () => {
    const tool = defineTool<{ city: string }>({
      name: 'get_weather',
      description: 'Get weather',
      tool: ({ city }) => ({ city }),
    });

    expect(tool.fieldDefinitions).toBeUndefined();
    // Original schema should be preserved - tool IS a schema
    expect(tool.parameters.properties.city?.type).toBe('string');
  });

  it('handles invalid field definition gracefully', () => {
    // Test edge case where fieldDefinitions contains something that's
    // neither a string nor a valid ZodLike (e.g., from JavaScript code)
    const tool = defineTool<{ city: string }>({
      name: 'get_weather',
      description: 'Get weather',
      fieldDefinitions: {
        // Pass an object that's not a string and not ZodLike
        city: { notZod: true } as unknown as string,
      },
      tool: ({ city }) => ({ city }),
    });

    // Description should not be added since the field definition is invalid
    expect(tool.parameters.properties.city?.description).toBeUndefined();
  });

  it('sets strict mode on schema', () => {
    const tool = defineTool<{ city: string }>({
      name: 'get_weather',
      description: 'Get weather',
      tool: ({ city }) => ({ city }),
      strict: true,
    });

    expect(tool.strict).toBe(true);
  });
});

describe('defineContextTool', () => {
  interface TestDeps {
    db: { search: (q: string) => string[] };
  }

  const createMockContext = (): Context<TestDeps> =>
    createContext<TestDeps>({
      db: { search: vi.fn((q: string) => [`result for ${q}`]) },
    });

  it('creates a context tool with correct properties', () => {
    const tool = defineContextTool<{ query: string }, TestDeps>({
      name: 'search_db',
      description: 'Search the database',
      fieldDefinitions: {
        query: 'The search query',
      },
      tool: (ctx, { query }) => ctx.deps.db.search(query),
    });

    expect(tool.name).toBe('search_db');
    expect(tool.description).toBe('Search the database');
    expect(tool.parameters.properties.query?.description).toBe(
      'The search query'
    );
  });

  it('auto-generates schema from type parameter', () => {
    // This test verifies the transformer is working correctly
    const tool = defineContextTool<{ query: string; limit?: number }, TestDeps>(
      {
        name: 'test_tool',
        description: 'Test',
        tool: (ctx, { query }) => ctx.deps.db.search(query),
      }
    );

    // Schema should be auto-generated with correct types
    expect(tool.parameters.type).toBe('object');
    expect(tool.parameters.properties.query?.type).toBe('string');
    expect(tool.parameters.properties.limit?.type).toBe('number');
    expect(tool.parameters.required).toContain('query');
    expect(tool.parameters.required).not.toContain('limit');
  });

  it('is callable with context and args', async () => {
    const ctx = createMockContext();

    const tool = defineContextTool<{ query: string }, TestDeps>({
      name: 'search_db',
      description: 'Search',
      tool: (ctx, { query }) => ctx.deps.db.search(query),
    });

    const result = await tool(ctx, { query: 'test' });
    expect(result).toEqual(['result for test']);
    expect(ctx.deps.db.search).toHaveBeenCalledWith('test');
  });

  it('executes from ToolCall with context', async () => {
    const ctx = createMockContext();

    const tool = defineContextTool<{ query: string }, TestDeps>({
      name: 'search_db',
      description: 'Search',
      tool: (ctx, { query }) => ctx.deps.db.search(query),
    });

    const toolCall = createToolCall('search_db', { query: 'hello' });
    const output = await tool.execute(ctx, toolCall);

    expect(output.result).toEqual(['result for hello']);
    expect(output.error).toBeNull();
  });

  it('returns error output when context tool throws', async () => {
    const ctx = createMockContext();

    const tool = defineContextTool<{ query: string }, TestDeps>({
      name: 'search_db',
      description: 'Search',
      tool: () => {
        throw new Error('DB connection failed');
      },
    });

    const toolCall = createToolCall('search_db', { query: 'test' });
    const output = await tool.execute(ctx, toolCall);

    expect(output.error).toBeInstanceOf(ToolExecutionError);
    expect(output.result).toBe('DB connection failed');
  });

  it('handles non-Error thrown values in context tool', async () => {
    const ctx = createMockContext();

    const tool = defineContextTool<{ query: string }, TestDeps>({
      name: 'search_db',
      description: 'Search',
      tool: () => {
        // eslint-disable-next-line @typescript-eslint/only-throw-error
        throw 'context error string';
      },
    });

    const toolCall = createToolCall('search_db', { query: 'test' });
    const output = await tool.execute(ctx, toolCall);

    expect(output.error).toBeInstanceOf(ToolExecutionError);
    expect(output.result).toBe('context error string');
  });

  it('is callable with context and args (async)', async () => {
    const ctx = createMockContext();

    const tool = defineContextTool<{ query: string }, TestDeps>({
      name: 'search_db',
      description: 'Search',
      tool: async (ctx, { query }) => {
        await Promise.resolve();
        return ctx.deps.db.search(query);
      },
    });

    const result = await tool(ctx, { query: 'async test' });
    expect(result).toEqual(['result for async test']);
  });
});
