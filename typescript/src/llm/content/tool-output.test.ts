import { describe, expect, it } from 'vitest';

import { ToolOutput } from '@/llm/content/tool-output';

describe('ToolOutput', () => {
  describe('type shape', () => {
    it('has correct type discriminator', () => {
      const output = ToolOutput.success('id', 'tool', 'result');
      expect(output.type).toBe('tool_output');
    });
  });

  describe('create', () => {
    it('creates tool output with all fields', () => {
      const output = ToolOutput.create(
        'call_123',
        'my_tool',
        { value: 42 },
        null
      );
      expect(output.id).toBe('call_123');
      expect(output.name).toBe('my_tool');
      expect(output.result).toEqual({ value: 42 });
      expect(output.error).toBeNull();
    });

    it('creates tool output with error', () => {
      const error = new Error('Something went wrong');
      const output = ToolOutput.create('id', 'tool', 'error message', error);
      expect(output.result).toBe('error message');
      expect(output.error).toBe(error);
    });

    it('defaults error to null', () => {
      const output = ToolOutput.create('id', 'tool', 'result');
      expect(output.error).toBeNull();
    });
  });

  describe('success', () => {
    it('creates successful tool output', () => {
      const output = ToolOutput.success('call_456', 'calculator', 42);
      expect(output.id).toBe('call_456');
      expect(output.name).toBe('calculator');
      expect(output.result).toBe(42);
      expect(output.error).toBeNull();
    });

    it('supports complex result types', () => {
      const result = { items: [1, 2, 3], total: 6 };
      const output = ToolOutput.success('id', 'sum', result);
      expect(output.result).toEqual(result);
    });

    it('supports null result', () => {
      const output = ToolOutput.success('id', 'tool', null);
      expect(output.result).toBeNull();
    });

    it('supports string result', () => {
      const output = ToolOutput.success('id', 'tool', 'string result');
      expect(output.result).toBe('string result');
    });

    it('supports boolean result', () => {
      const output = ToolOutput.success('id', 'tool', true);
      expect(output.result).toBe(true);
    });

    it('supports array result', () => {
      const output = ToolOutput.success('id', 'tool', [1, 2, 3]);
      expect(output.result).toEqual([1, 2, 3]);
    });
  });

  describe('failure', () => {
    it('creates failed tool output', () => {
      const error = new Error('Tool failed');
      const output = ToolOutput.failure('call_789', 'failing_tool', error);
      expect(output.id).toBe('call_789');
      expect(output.name).toBe('failing_tool');
      expect(output.result).toBe('Tool failed');
      expect(output.error).toBe(error);
    });

    it('stores error message as result', () => {
      const error = new Error('Custom error message');
      const output = ToolOutput.failure('id', 'tool', error);
      expect(output.result).toBe('Custom error message');
    });
  });
});
