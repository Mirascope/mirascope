/**
 * Prompt utilities for defining reusable LLM prompts.
 *
 * The unified `definePrompt` function automatically detects whether a prompt
 * is context-aware based on whether the template type T includes `ctx: Context<DepsT>`.
 */

export {
  definePrompt,
  type MessageTemplate,
  type Prompt,
  type PromptArgs,
  type TemplateFunc,
  // Context-aware types (now in unified prompt.ts)
  type ContextMessageTemplate,
  type ContextPrompt,
  type ContextPromptArgs,
  type ContextTemplateFunc,
  // Type utilities
  type ExtractDeps,
  type ExtractVars,
  type UnifiedPrompt,
} from '@/llm/prompts/prompt';
