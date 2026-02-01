import { describe, expect, it, vi } from 'vitest';
import {
  Toolkit,
  ContextToolkit,
  createToolkit,
  createContextToolkit,
} from '@/llm/tools/toolkit';
import { defineTool, defineContextTool } from '@/llm/tools/define-tool';
import type { ToolCall } from '@/llm/content/tool-call';
import type { Context } from '@/llm/context';
import type { ToolParameterSchema } from '@/llm/tools/tool-schema';
import { ToolNotFoundError } from '@/llm/exceptions';

// Helper to create a mock schema
function createMockSchema(
  properties: Record<string, { type: string }>,
  required: string[] = []
): ToolParameterSchema {
  return {
    type: 'object',
    properties,
    required,
    additionalProperties: false,
  };
}

// Helper to create a mock ToolCall
function createToolCall(name: string, args: Record<string, unknown>): ToolCall {
  return {
    type: 'tool_call',
    id: `id-${name}`,
    name,
    args: JSON.stringify(args),
  };
}

describe('Toolkit', () => {
  const weatherSchema = createMockSchema({ city: { type: 'string' } }, [
    'city',
  ]);
  const searchSchema = createMockSchema({ query: { type: 'string' } }, [
    'query',
  ]);

  const getWeather = defineTool<{ city: string }>({
    name: 'get_weather',
    description: 'Get weather',
    tool: ({ city }) => ({ temp: 72, city }),
    __schema: weatherSchema,
  });

  const searchWeb = defineTool<{ query: string }>({
    name: 'search_web',
    description: 'Search the web',
    tool: ({ query }) => [`Result for: ${query}`],
    __schema: searchSchema,
  });

  it('creates toolkit with tools', () => {
    const toolkit = new Toolkit([getWeather, searchWeb]);

    expect(toolkit.tools).toHaveLength(2);
    expect(toolkit.toolMap.has('get_weather')).toBe(true);
    expect(toolkit.toolMap.has('search_web')).toBe(true);
  });

  it('returns tools array', () => {
    const toolkit = new Toolkit([getWeather, searchWeb]);

    const tools = toolkit.tools;
    expect(tools).toContain(getWeather);
    expect(tools).toContain(searchWeb);
  });

  it('returns schemas array', () => {
    const toolkit = new Toolkit([getWeather, searchWeb]);

    const schemas = toolkit.schemas;
    expect(schemas).toHaveLength(2);
    expect(schemas[0]?.name).toBe('get_weather');
    expect(schemas[1]?.name).toBe('search_web');
  });

  it('gets tool by tool call', () => {
    const toolkit = new Toolkit([getWeather, searchWeb]);

    expect(toolkit.get(createToolCall('get_weather', {}))).toBe(getWeather);
    expect(toolkit.get(createToolCall('search_web', {}))).toBe(searchWeb);
    expect(toolkit.get(createToolCall('nonexistent', {}))).toBeUndefined();
  });

  it('executes tool call', async () => {
    const toolkit = new Toolkit([getWeather, searchWeb]);
    const toolCall = createToolCall('get_weather', { city: 'NYC' });

    const output = await toolkit.execute(toolCall);

    expect(output.result).toEqual({ temp: 72, city: 'NYC' });
    expect(output.error).toBeNull();
  });

  it('returns error for unknown tool', async () => {
    const toolkit = new Toolkit([getWeather]);
    const toolCall = createToolCall('unknown_tool', {});

    const output = await toolkit.execute(toolCall);

    expect(output.error).toBeInstanceOf(ToolNotFoundError);
    expect((output.error as ToolNotFoundError).toolName).toBe('unknown_tool');
  });

  it('handles empty toolkit', () => {
    const toolkit = new Toolkit([]);

    expect(toolkit.tools).toHaveLength(0);
    expect(toolkit.schemas).toHaveLength(0);
  });
});

describe('ContextToolkit', () => {
  interface TestDeps {
    db: { search: (q: string) => string[] };
    api: { fetch: (url: string) => Promise<string> };
  }

  const searchSchema = createMockSchema({ query: { type: 'string' } }, [
    'query',
  ]);
  const fetchSchema = createMockSchema({ url: { type: 'string' } }, ['url']);

  const searchDb = defineContextTool<{ query: string }, TestDeps>({
    name: 'search_db',
    description: 'Search database',
    tool: (ctx, { query }) => ctx.deps.db.search(query),
    __schema: searchSchema,
  });

  const fetchUrl = defineContextTool<{ url: string }, TestDeps>({
    name: 'fetch_url',
    description: 'Fetch URL',
    tool: async (ctx, { url }) => ctx.deps.api.fetch(url),
    __schema: fetchSchema,
  });

  const createMockContext = (): Context<TestDeps> => ({
    deps: {
      db: { search: vi.fn((q: string) => [`db: ${q}`]) },
      api: {
        fetch: vi.fn((url: string) => Promise.resolve(`fetched: ${url}`)),
      },
    },
  });

  it('creates context toolkit with tools', () => {
    const toolkit = new ContextToolkit<TestDeps>([searchDb, fetchUrl]);

    expect(toolkit.tools).toHaveLength(2);
    expect(toolkit.toolMap.has('search_db')).toBe(true);
    expect(toolkit.toolMap.has('fetch_url')).toBe(true);
  });

  it('returns schemas array', () => {
    const toolkit = new ContextToolkit<TestDeps>([searchDb, fetchUrl]);

    const schemas = toolkit.schemas;
    expect(schemas).toHaveLength(2);
    expect(schemas.map((s) => s.name)).toContain('search_db');
    expect(schemas.map((s) => s.name)).toContain('fetch_url');
  });

  it('gets tool by tool call', () => {
    const toolkit = new ContextToolkit<TestDeps>([searchDb]);

    expect(toolkit.get(createToolCall('search_db', {}))).toBe(searchDb);
    expect(toolkit.get(createToolCall('nonexistent', {}))).toBeUndefined();
  });

  it('executes tool call with context', async () => {
    const ctx = createMockContext();
    const toolkit = new ContextToolkit<TestDeps>([searchDb]);
    const toolCall = createToolCall('search_db', { query: 'test' });

    const output = await toolkit.execute(ctx, toolCall);

    expect(output.result).toEqual(['db: test']);
    expect(output.error).toBeNull();
    expect(ctx.deps.db.search).toHaveBeenCalledWith('test');
  });

  it('returns error for unknown tool', async () => {
    const ctx = createMockContext();
    const toolkit = new ContextToolkit<TestDeps>([searchDb]);
    const toolCall = createToolCall('unknown', {});

    const output = await toolkit.execute(ctx, toolCall);

    expect(output.error).toBeInstanceOf(ToolNotFoundError);
  });

  it('executes multiple tool calls in parallel', async () => {
    const ctx = createMockContext();
    const toolkit = new ContextToolkit<TestDeps>([searchDb, fetchUrl]);

    const toolCalls = [
      createToolCall('search_db', { query: 'hello' }),
      createToolCall('fetch_url', { url: 'https://example.com' }),
    ];

    const outputs = await toolkit.executeAll(ctx, toolCalls);

    expect(outputs).toHaveLength(2);
    expect(outputs[0]?.result).toEqual(['db: hello']);
    expect(outputs[1]?.result).toBe('fetched: https://example.com');
  });
});

describe('createToolkit', () => {
  it('creates toolkit from tools array', () => {
    const schema = createMockSchema({ x: { type: 'string' } });
    const tool = defineTool<{ x: string }>({
      name: 'test',
      description: 'Test',
      tool: () => null,
      __schema: schema,
    });

    const toolkit = createToolkit([tool]);

    expect(toolkit).toBeInstanceOf(Toolkit);
    expect(toolkit.toolMap.has('test')).toBe(true);
  });
});

describe('createContextToolkit', () => {
  it('creates context toolkit from tools array', () => {
    interface Deps {
      value: number;
    }
    const schema = createMockSchema({ x: { type: 'string' } });
    const tool = defineContextTool<{ x: string }, Deps>({
      name: 'test',
      description: 'Test',
      tool: (ctx) => ctx.deps.value,
      __schema: schema,
    });

    const toolkit = createContextToolkit<Deps>([tool]);

    expect(toolkit).toBeInstanceOf(ContextToolkit);
    expect(toolkit.toolMap.has('test')).toBe(true);
  });
});
