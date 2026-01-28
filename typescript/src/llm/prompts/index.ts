/**
 * Prompt utilities for defining reusable LLM prompts.
 */

export {
  definePrompt,
  type MessageTemplate,
  type Prompt,
  type PromptArgs,
  type TemplateFunc,
} from '@/llm/prompts/prompt';

export {
  defineContextPrompt,
  type ContextMessageTemplate,
  type ContextPrompt,
  type ContextPromptArgs,
  type ContextTemplateFunc,
} from '@/llm/prompts/context-prompt';
