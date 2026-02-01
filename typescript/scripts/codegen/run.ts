#!/usr/bin/env bun
/**
 * Run all code generation scripts.
 *
 * Usage:
 *   bun run typescript/scripts/codegen/run.ts
 *   # or via package.json script:
 *   bun run codegen
 */

import { generateAnthropicModelInfo } from "./anthropic";
import { generateGoogleModelInfo } from "./google";
import { generateOpenAIModelInfo } from "./openai";

console.log("=== Generating TypeScript model info ===\n");

console.log("--- Anthropic ---");
generateAnthropicModelInfo();
console.log("");

console.log("--- Google ---");
generateGoogleModelInfo();
console.log("");

console.log("--- OpenAI ---");
generateOpenAIModelInfo();
console.log("");

console.log("=== Done ===");
