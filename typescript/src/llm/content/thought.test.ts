import { describe, expect, it } from 'vitest';

import type { Thought } from '@/llm/content/thought';

describe('Thought', () => {
  it('has correct type discriminator', () => {
    const thought: Thought = { type: 'thought', thought: 'reasoning...' };
    expect(thought.type).toBe('thought');
  });

  it('stores thought content', () => {
    const thought: Thought = {
      type: 'thought',
      thought: 'Let me think about this...',
    };
    expect(thought.thought).toBe('Let me think about this...');
  });

  it('supports empty thought', () => {
    const thought: Thought = { type: 'thought', thought: '' };
    expect(thought.thought).toBe('');
  });

  it('supports multiline thought', () => {
    const thought: Thought = {
      type: 'thought',
      thought: 'Step 1: Analyze\nStep 2: Reason\nStep 3: Conclude',
    };
    expect(thought.thought).toContain('\n');
  });
});
