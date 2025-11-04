#!/usr/bin/env bun
/**
 * Regenerate example files from TypeScript generator.
 */

import { writeFileSync, readdirSync, unlinkSync } from "fs";
import { join, dirname, relative } from "path";
import { spawn } from "child_process";
import {
  ExampleGenerator,
  filenameForOptions,
  allOptions,
} from "./example_generator.ts";

async function runCommand(
  command: string,
  args: string[],
  cwd: string
): Promise<void> {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, { cwd, stdio: "inherit" });
    child.on("close", (code) => {
      if (code === 0) {
        resolve();
      } else {
        reject(new Error(`Command failed with exit code ${code}`));
      }
    });
  });
}

async function main(): Promise<void> {
  const scriptPath = import.meta.path;
  const outputDir = join(dirname(scriptPath), "..", "examples", "sazed");

  // Remove existing Python files
  const files = readdirSync(outputDir);
  for (const file of files) {
    if (file.match(/^sazed.*\.py$/)) {
      unlinkSync(join(outputDir, file));
    }
  }

  // Generate all combinations
  const generatedFiles: string[] = [];
  for (const options of allOptions()) {
    const filename = filenameForOptions(options);

    const generator = new ExampleGenerator(options);
    const content = generator.generate();
    const filepath = join(outputDir, filename);

    writeFileSync(filepath, content);
    generatedFiles.push(filepath);
  }

  // Check formatting with ruff (without fixing)
  if (generatedFiles.length > 0) {
    const pythonDir = join(dirname(scriptPath), "..");
    try {
      await runCommand(
        "uv",
        ["run", "ruff", "check", "--fix", ...generatedFiles],
        pythonDir
      );
      await runCommand(
        "uv",
        ["run", "ruff", "format", ...generatedFiles],
        pythonDir
      );
    } catch (error) {
      console.error(
        "Ruff check failed! Generated code needs formatting fixes."
      );
      throw error;
    }
  }

  // Generate MDX file with all generated examples
  const docsRoot = join(dirname(scriptPath), "..", "..", "docs");
  const outputPath = join(docsRoot, "content", "examples.mdx");
  generateExamplesMdx(
    generatedFiles,
    join(dirname(scriptPath), "..", "examples"),
    outputPath
  );

  console.log(`Generated ${generatedFiles.length} example files`);
}

function generateExamplesMdx(
  generatedFiles: string[],
  examplesRoot: string,
  outputPath: string
): void {
  const content: string[] = [];
  content.push("---");
  content.push("title: Examples");
  content.push(
    "description: Unified doc with diverse examples, intended as a primer for LLMs on common Mirascope patterns."
  );
  content.push("---");
  content.push("");
  content.push("# Mirascope v2: Progressive Examples");
  content.push("");
  content.push(
    "The following examples show how to use Mirascope v2 with a variety of usage patterns."
  );
  content.push(
    "These are intended to give LLMs a primer on Mirascope's interface."
  );
  content.push("");

  for (const pyFile of generatedFiles) {
    const relPath = relative(examplesRoot, pyFile);
    content.push(`## \`${relPath}\``);
    content.push("");
    content.push(`<CodeExample file="examples/${relPath}" />`);
    content.push("");
  }

  writeFileSync(outputPath, content.join("\n"));
}

if (import.meta.main) {
  main().catch(console.error);
}
