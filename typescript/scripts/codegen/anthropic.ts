/**
 * Code generation for Anthropic model info from test results.
 *
 * Reads python/scripts/model_features/data/anthropic.yaml and generates
 * typescript/src/llm/providers/anthropic/model-info.ts
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
    strict_structured_output?: FeatureResult;
  };
}

interface YamlData {
  models?: Record<string, ModelInfo>;
}

/**
 * Collect model IDs and models without strict support from test data.
 */
function collectModelData(data: YamlData): {
  modelIds: string[];
  modelsWithoutStrict: string[];
} {
  const modelIds = new Set<string>();
  const modelsWithoutStrict = new Set<string>();

  // Pattern to match date suffixes like -20241022
  const datePattern = /-(\d{8})$/;
  // Pattern to match major version suffixes like -4 (but not -3-5 or -4-0)
  const majorVersionPattern = /-(\d+)$/;

  const modelsData = data.models ?? {};

  for (const [modelId, modelInfo] of Object.entries(modelsData)) {
    const features = modelInfo.features ?? {};
    const strictResult = features.strict_structured_output ?? {};
    const supportsStrict = strictResult.status === 'supported';

    const dateMatch = modelId.match(datePattern);

    if (dateMatch) {
      // Model has a date suffix - generate variants based on base name
      const baseName = modelId.slice(0, dateMatch.index);

      // Add dated version
      modelIds.add(`anthropic/${modelId}`);
      if (!supportsStrict) {
        modelsWithoutStrict.add(modelId);
      }

      // Add -latest alias
      modelIds.add(`anthropic/${baseName}-latest`);
      if (!supportsStrict) {
        modelsWithoutStrict.add(`${baseName}-latest`);
      }

      // Add base name without suffix
      modelIds.add(`anthropic/${baseName}`);
      if (!supportsStrict) {
        modelsWithoutStrict.add(baseName);
      }

      // Check if base name has a major version suffix
      const majorVersionMatch = baseName.match(majorVersionPattern);
      if (majorVersionMatch) {
        // Also add minor version variant (e.g., claude-sonnet-4-0)
        const minorVersion = `${baseName}-0`;
        modelIds.add(`anthropic/${minorVersion}`);
        if (!supportsStrict) {
          modelsWithoutStrict.add(minorVersion);
        }

        // And its -latest alias (e.g., claude-sonnet-4-0-latest)
        modelIds.add(`anthropic/${minorVersion}-latest`);
        if (!supportsStrict) {
          modelsWithoutStrict.add(`${minorVersion}-latest`);
        }

        // And its dated version (e.g., claude-sonnet-4-0-20250929)
        const datedMinorVersion = `${minorVersion}-${dateMatch[1]}`;
        modelIds.add(`anthropic/${datedMinorVersion}`);
        if (!supportsStrict) {
          modelsWithoutStrict.add(datedMinorVersion);
        }
      }
    } else {
      // Model without date suffix - add as-is
      modelIds.add(`anthropic/${modelId}`);
      if (!supportsStrict) {
        modelsWithoutStrict.add(modelId);
      }
    }
  }

  return {
    modelIds: [...modelIds].sort(),
    modelsWithoutStrict: [...modelsWithoutStrict].sort(),
  };
}

/**
 * Generate the TypeScript model-info.ts file content.
 */
function generateModelInfoContent(
  modelIds: string[],
  modelsWithoutStrict: string[]
): string {
  const lines: string[] = [
    ...generateFileHeader(
      'Anthropic',
      'typescript/scripts/codegen/anthropic.ts'
    ),
    '',
    ...generateKnownModelsExports(
      'ANTHROPIC',
      'Anthropic',
      modelIds,
      'Valid Anthropic model IDs.'
    ),
    '',
    ...generateFeatureSet(
      'MODELS_WITHOUT_STRICT_STRUCTURED_OUTPUTS',
      'Models that do not support strict structured outputs (strict mode tools).',
      null,
      modelsWithoutStrict
    ),
    '',
  ];

  return lines.join('\n');
}

/**
 * Generate Anthropic model info from YAML test data.
 */
export function generateAnthropicModelInfo(): void {
  const { inputPath, outputPath } = getPaths('anthropic', import.meta.dirname);

  // Load YAML
  const data = readYamlData<YamlData>(inputPath, 'anthropic');

  // Collect model data
  console.log('Collecting model data...');
  const { modelIds, modelsWithoutStrict } = collectModelData(data);

  // Generate TypeScript code
  console.log('Generating TypeScript model info...');
  const content = generateModelInfoContent(modelIds, modelsWithoutStrict);

  // Write file
  writeGeneratedFile(outputPath, content);

  // Show stats
  const modelsData = data.models ?? {};
  const discoveredModelCount = Object.keys(modelsData).length;
  const modelsWithoutStrictCount = Object.values(modelsData).filter(
    (info) => info.features?.strict_structured_output?.status !== 'supported'
  ).length;

  console.log(`  Discovered models: ${discoveredModelCount}`);
  console.log(`  Generated model IDs: ${modelIds.length}`);
  console.log(
    `  Models without strict structured outputs: ${modelsWithoutStrictCount}`
  );
}

// Run if executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  generateAnthropicModelInfo();
}
