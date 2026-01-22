#!/usr/bin/env bun

import { resolve } from "path";
import { spawnSync } from "child_process";

function run(command: string, args: string[], cwd?: string): void {
  const result = spawnSync(command, args, {
    cwd: cwd || process.cwd(),
    stdio: "inherit",
    shell: false,
  });

  if (result.error) {
    throw new Error(`Failed to execute ${command}: ${result.error.message}`);
  }

  if (result.status !== 0) {
    throw new Error(
      `Command failed with exit code ${result.status}: ${command} ${args.join(" ")}`,
    );
  }
}

function generateApiDocs(): void {
  // Parse CLI arguments
  const args = process.argv.slice(2);
  let sourcePath: string | undefined;
  let outputPath: string | undefined;
  let packageName: string | undefined;
  let apiRoot: string | undefined;
  let productSlug: string | undefined;
  let productLabel: string | undefined;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--source-path" && i + 1 < args.length) {
      sourcePath = resolve(args[i + 1]);
      i++;
    } else if (args[i] === "--output" && i + 1 < args.length) {
      outputPath = resolve(args[i + 1]);
      i++;
    } else if (args[i] === "--package" && i + 1 < args.length) {
      packageName = args[i + 1];
      i++;
    } else if (args[i] === "--api-root" && i + 1 < args.length) {
      apiRoot = args[i + 1];
      i++;
    } else if (args[i] === "--product-slug" && i + 1 < args.length) {
      productSlug = args[i + 1];
      i++;
    } else if (args[i] === "--product-label" && i + 1 < args.length) {
      productLabel = args[i + 1];
      i++;
    }
  }

  // Validate required arguments
  if (
    !sourcePath ||
    !outputPath ||
    !packageName ||
    !apiRoot ||
    !productSlug ||
    !productLabel
  ) {
    console.error("Error: Missing required arguments");
    console.error("\nUsage:");
    console.error(
      "  bun run api2mdx/generate-api-docs.ts --source-path <path> --package <name> --output <path> --api-root <path> --product-slug <slug> --product-label <label>",
    );
    console.error("\nExample:");
    console.error(
      "  bun run api2mdx/generate-api-docs.ts --source-path ../python --package mirascope.llm --output content/docs/api --api-root /docs/api --product-slug llm --product-label LLM",
    );
    process.exit(1);
  }

  console.log("Generating API documentation with api2mdx...");
  console.log(`  Source: ${sourcePath}`);
  console.log(`  Package: ${packageName}`);
  console.log(`  Output: ${outputPath}`);
  console.log(`  API Root: ${apiRoot}`);
  console.log(`  Product: ${productSlug}/ (${productLabel})`);

  const api2mdxDir = resolve(import.meta.dirname, ".");

  const uvArgs = [
    "run",
    "-m",
    "api2mdx.main",
    "--source-path",
    sourcePath,
    "--package",
    packageName,
    "--output",
    outputPath,
    "--api-root",
    apiRoot,
    "--product-slug",
    productSlug,
    "--product-label",
    productLabel,
  ];

  run("uv", uvArgs, api2mdxDir);

  console.log("✓ API documentation generation complete");
}

try {
  generateApiDocs();
} catch (error) {
  console.error(
    "Error generating API docs:",
    error instanceof Error ? error.message : String(error),
  );
  process.exit(1);
}
