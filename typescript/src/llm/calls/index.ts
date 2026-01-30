/**
 * Call utilities for defining LLM calls with bundled models.
 *
 * The unified `defineCall` function automatically detects whether a call
 * is context-aware based on whether the template type T includes `ctx: Context<DepsT>`.
 */

export {
  defineCall,
  type Call,
  type CallArgs,
  // Context-aware types (now in unified call.ts)
  type ContextCall,
  type ContextCallArgs,
  // Type utilities
  type UnifiedCall,
} from '@/llm/calls/call';
