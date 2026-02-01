/**
 * Code generation for Google model info from test results.
 *
 * Reads python/scripts/model_features/data/google.yaml and generates
 * typescript/src/llm/providers/google/model-info.ts
 *
 * See index.ts for explanation of why codegen exists in both Python and TypeScript.
 */

import {
  getPaths,
  readYamlData,
  writeGeneratedFile,
  generateFileHeader,
  generateKnownModelsExports,
  generateFeatureSet,
} from "./utils";

interface FeatureResult {
  status?: string;
}

interface ModelInfo {
  features?: {
    chat_model?: FeatureResult;
    structured_output_with_tools?: FeatureResult;
  };
}

interface YamlData {
  models?: Record<string, ModelInfo>;
}

/**
 * Collect model IDs and models without structured output + tools support.
 */
function collectModelData(data: YamlData): {
  modelIds: string[];
  modelsWithoutSupport: string[];
} {
  const modelIds: string[] = [];
  const modelsWithoutSupport = new Set<string>();

  const modelsData = data.models ?? {};

  for (const [modelId, modelInfo] of Object.entries(modelsData).sort()) {
    const features = modelInfo.features ?? {};

    // Check if model supports chat
    const chatResult = features.chat_model ?? {};
    const chatSupported = chatResult.status === "supported";

    // Skip models that don't support chat
    if (!chatSupported) {
      continue;
    }

    // Add model ID
    modelIds.push(`google/${modelId}`);

    // Check structured output with tools support
    const structuredOutputToolsResult =
      features.structured_output_with_tools ?? {};
    const supportsStructuredOutputAndTools =
      structuredOutputToolsResult.status === "supported";

    if (!supportsStructuredOutputAndTools) {
      modelsWithoutSupport.add(modelId);
    }
  }

  return {
    modelIds,
    modelsWithoutSupport: [...modelsWithoutSupport].sort(),
  };
}

/**
 * Generate the TypeScript model-info.ts file content.
 */
function generateModelInfoContent(
  modelIds: string[],
  modelsWithoutSupport: string[],
): string {
  const lines: string[] = [
    ...generateFileHeader("Google", "typescript/scripts/codegen/google.ts"),
    "",
    ...generateKnownModelsExports(
      "GOOGLE",
      "Google",
      modelIds,
      "Valid Google model IDs.",
    ),
    "",
    ...generateFeatureSet(
      "MODELS_WITHOUT_STRUCTURED_OUTPUT_AND_TOOLS_SUPPORT",
      "Models that do not support structured outputs when tools are present.",
      null,
      modelsWithoutSupport,
    ),
    "",
  ];

  return lines.join("\n");
}

/**
 * Generate Google model info from YAML test data.
 */
export function generateGoogleModelInfo(): void {
  const { inputPath, outputPath } = getPaths("google", import.meta.dirname);

  // Load YAML
  const data = readYamlData<YamlData>(inputPath, "google");

  // Collect model data
  console.log("Collecting model data...");
  const { modelIds, modelsWithoutSupport } = collectModelData(data);

  // Generate TypeScript code
  console.log("Generating TypeScript model info...");
  const content = generateModelInfoContent(modelIds, modelsWithoutSupport);

  // Write file
  writeGeneratedFile(outputPath, content);

  // Show stats
  const modelsData = data.models ?? {};
  const discoveredModelCount = Object.keys(modelsData).length;
  const chatModelCount = Object.values(modelsData).filter(
    (info) => info.features?.chat_model?.status === "supported",
  ).length;

  console.log(`  Discovered models: ${discoveredModelCount}`);
  console.log(`  Chat models (generated): ${chatModelCount}`);
  console.log(
    `  Models without structured output + tools support: ${modelsWithoutSupport.length}`,
  );
}

// Run if executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  generateGoogleModelInfo();
}
