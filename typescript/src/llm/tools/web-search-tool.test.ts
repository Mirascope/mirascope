import { describe, expect, it } from 'vitest';
import { WebSearchTool, isWebSearchTool } from '@/llm/tools/web-search-tool';
import { ProviderTool, isProviderTool } from '@/llm/tools/provider-tool';

describe('WebSearchTool', () => {
  it('creates a web search tool with default name', () => {
    const tool = new WebSearchTool();

    expect(tool.name).toBe('web_search');
  });

  it('extends ProviderTool', () => {
    const tool = new WebSearchTool();

    expect(tool).toBeInstanceOf(ProviderTool);
    expect(isProviderTool(tool)).toBe(true);
  });
});

describe('isWebSearchTool', () => {
  it('returns true for WebSearchTool instances', () => {
    const tool = new WebSearchTool();

    expect(isWebSearchTool(tool)).toBe(true);
  });

  it('returns false for ProviderTool instances that are not WebSearchTool', () => {
    const tool = new ProviderTool('some_other_tool');

    expect(isWebSearchTool(tool)).toBe(false);
  });

  it('returns false for non-WebSearchTool values', () => {
    expect(isWebSearchTool(null)).toBe(false);
    expect(isWebSearchTool(undefined)).toBe(false);
    expect(isWebSearchTool({})).toBe(false);
    expect(isWebSearchTool({ name: 'web_search' })).toBe(false);
    expect(isWebSearchTool('string')).toBe(false);
    expect(isWebSearchTool(123)).toBe(false);
  });
});
