/**
 * Anthropic provider implementation.
 *
 * The AnthropicProvider handles routing between standard and beta APIs internally.
 * AnthropicBetaProvider can also be selected explicitly with the anthropic-beta prefix.
 */

export type { AnthropicModelId } from "@/llm/providers/anthropic/model-id";
export { modelName } from "@/llm/providers/anthropic/model-id";
export type { AnthropicKnownModels } from "@/llm/providers/anthropic/model-info";
export {
  ANTHROPIC_KNOWN_MODELS,
  MODELS_WITHOUT_STRICT_STRUCTURED_OUTPUTS,
} from "@/llm/providers/anthropic/model-info";

export { AnthropicProvider } from "@/llm/providers/anthropic/provider";
