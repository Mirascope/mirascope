#!/usr/bin/env bun
/**
 * Standalone script for generating test social cards.
 *
 * Generates a few sample cards without Vite or thread pools.
 * Useful for quickly testing the social card rendering pipeline.
 *
 * Usage: bun run generate:social-cards-test
 */

import fs from "node:fs/promises";
import path from "node:path";

import { loadAssets, renderSocialCard } from "../app/lib/social-cards/render";

const TEST_CARDS = [
  { filename: "docs.webp", title: "Quickstart" },
  { filename: "pricing.webp", title: "Pricing" },
  {
    filename: "blog-prompt-orchestration.webp",
    title: "Prompt Orchestration: Techniques, Challenges, and Best Practices",
  },
  {
    filename: "docs-v1-api-core-cohere-call.webp",
    title: "mirascope.core.cohere.call",
  },
];

async function main() {
  const outputDir = path.resolve(
    process.cwd(),
    "dist/client/debug-social-cards",
  );
  await fs.mkdir(outputDir, { recursive: true });

  console.log("[social-cards] Loading assets...");
  const assets = await loadAssets();

  console.log(`[social-cards] Generating ${TEST_CARDS.length} test cards...`);
  for (const card of TEST_CARDS) {
    const outputPath = path.join(outputDir, card.filename);
    const buffer = await renderSocialCard(card.title, assets);
    await fs.writeFile(outputPath, buffer);
    console.log(`[social-cards] Generated ${card.filename}`);
  }

  console.log("[social-cards] Done!");
}

main().catch(console.error);
