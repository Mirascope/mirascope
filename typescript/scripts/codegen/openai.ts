/**
 * Code generation for OpenAI model info from test results.
 *
 * Reads python/scripts/model_features/data/openai.yaml and generates
 * typescript/src/llm/providers/openai/model-info.ts
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
} from './utils';

interface FeatureResult {
  status?: string;
}

interface ModelInfo {
  features?: {
    completions_api?: FeatureResult;
    responses_api?: FeatureResult;
    audio_input?: FeatureResult;
    reasoning?: FeatureResult;
    structured_output?: FeatureResult;
    json_object?: FeatureResult;
  };
}

interface YamlData {
  models?: Record<string, ModelInfo>;
}

interface OpenAIModelData {
  modelIds: string[];
  modelsWithoutAudioSupport: string[];
  nonReasoningModels: string[];
  modelsWithoutJsonSchemaSupport: string[];
  modelsWithoutJsonObjectSupport: string[];
}

/**
 * Collect model data from YAML test results.
 */
function collectModelData(data: YamlData): OpenAIModelData {
  const modelIds: string[] = [];
  const modelsWithoutAudio = new Set<string>();
  const nonReasoning = new Set<string>();
  const withoutJsonSchema = new Set<string>();
  const withoutJsonObject = new Set<string>();

  const modelsData = data.models ?? {};

  for (const [modelId, modelInfo] of Object.entries(modelsData).sort()) {
    const features = modelInfo.features ?? {};

    // Check API support
    const completionsResult = features.completions_api ?? {};
    const responsesResult = features.responses_api ?? {};
    const audioResult = features.audio_input ?? {};
    const reasoningResult = features.reasoning ?? {};
    const structuredOutputResult = features.structured_output ?? {};
    const jsonObjectResult = features.json_object ?? {};

    const completionsSupported = completionsResult.status === 'supported';
    const responsesSupported = responsesResult.status === 'supported';

    // Skip if neither API is supported
    if (!completionsSupported && !responsesSupported) {
      continue;
    }

    // Add base model ID
    const baseId = `openai/${modelId}`;
    modelIds.push(baseId);

    // Add API-specific variants
    if (completionsSupported) {
      modelIds.push(`${baseId}:completions`);
    }
    if (responsesSupported) {
      modelIds.push(`${baseId}:responses`);
    }

    // Categorize audio support (for completions API)
    const audioStatus = audioResult.status;
    if (audioStatus === 'not_supported' || audioStatus === 'unavailable') {
      modelsWithoutAudio.add(modelId);
    }

    // Categorize reasoning support (for responses API)
    const reasoningStatus = reasoningResult.status;
    if (reasoningStatus === 'not_supported') {
      nonReasoning.add(modelId);
    }

    // Categorize JSON schema support (structured outputs)
    const structuredOutputStatus = structuredOutputResult.status;
    if (
      structuredOutputStatus === 'not_supported' ||
      structuredOutputStatus === 'unavailable'
    ) {
      withoutJsonSchema.add(modelId);
    }

    // Categorize JSON object support
    const jsonObjectStatus = jsonObjectResult.status;
    if (
      jsonObjectStatus === 'not_supported' ||
      jsonObjectStatus === 'unavailable'
    ) {
      withoutJsonObject.add(modelId);
    }
  }

  return {
    modelIds,
    modelsWithoutAudioSupport: [...modelsWithoutAudio].sort(),
    nonReasoningModels: [...nonReasoning].sort(),
    modelsWithoutJsonSchemaSupport: [...withoutJsonSchema].sort(),
    modelsWithoutJsonObjectSupport: [...withoutJsonObject].sort(),
  };
}

/**
 * Generate the TypeScript model-info.ts file content.
 */
function generateModelInfoContent(modelData: OpenAIModelData): string {
  const lines: string[] = [
    ...generateFileHeader('OpenAI', 'typescript/scripts/codegen/openai.ts'),
    '',
    ...generateKnownModelsExports(
      'OPENAI',
      'OpenAI',
      modelData.modelIds,
      'Valid OpenAI model IDs including API-specific variants.'
    ),
    '',
    ...generateFeatureSet(
      'MODELS_WITHOUT_AUDIO_SUPPORT',
      'Models that do not support audio inputs.',
      'Models not in this set are assumed to support audio (optimistic default).',
      modelData.modelsWithoutAudioSupport
    ),
    '',
    ...generateFeatureSet(
      'NON_REASONING_MODELS',
      'Models that do not support the reasoning parameter.',
      'Models not in this set are assumed to support reasoning (optimistic default).',
      modelData.nonReasoningModels
    ),
    '',
    ...generateFeatureSet(
      'MODELS_WITHOUT_JSON_SCHEMA_SUPPORT',
      'Models that do not support JSON schema (structured outputs).',
      'Models not in this set are assumed to support JSON schema (optimistic default).',
      modelData.modelsWithoutJsonSchemaSupport
    ),
    '',
    ...generateFeatureSet(
      'MODELS_WITHOUT_JSON_OBJECT_SUPPORT',
      'Models that do not support JSON object mode.',
      'Models not in this set are assumed to support JSON object mode (optimistic default).',
      modelData.modelsWithoutJsonObjectSupport
    ),
    '',
  ];

  return lines.join('\n');
}

/**
 * Generate OpenAI model info from YAML test data.
 */
export function generateOpenAIModelInfo(): void {
  const { inputPath, outputPath } = getPaths('openai', import.meta.dirname);

  // Load YAML
  const data = readYamlData<YamlData>(inputPath, 'openai');

  // Collect model data
  console.log('Collecting model data...');
  const modelData = collectModelData(data);

  // Generate TypeScript code
  console.log('Generating TypeScript model info...');
  const content = generateModelInfoContent(modelData);

  // Write file
  writeGeneratedFile(outputPath, content);

  // Show stats
  console.log(`  Total model IDs: ${modelData.modelIds.length}`);
  console.log(
    `  Models without audio support: ${modelData.modelsWithoutAudioSupport.length}`
  );
  console.log(`  Non-reasoning models: ${modelData.nonReasoningModels.length}`);
  console.log(
    `  Models without JSON schema support: ${modelData.modelsWithoutJsonSchemaSupport.length}`
  );
  console.log(
    `  Models without JSON object support: ${modelData.modelsWithoutJsonObjectSupport.length}`
  );
}

// Run if executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  generateOpenAIModelInfo();
}
