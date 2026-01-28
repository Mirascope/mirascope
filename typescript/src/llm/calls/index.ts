/**
 * Call utilities for defining LLM calls with bundled models.
 */

export { defineCall, type Call, type CallArgs } from '@/llm/calls/call';

export {
  defineContextCall,
  type ContextCall,
  type ContextCallArgs,
} from '@/llm/calls/context-call';
