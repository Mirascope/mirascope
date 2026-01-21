#!/usr/bin/env bun
// Python lint-staged script
import { $ } from "bun";

const files = process.argv.slice(2);

try {
  // Check if any template files or examples directory changed
  const hasTemplateChanges = files.some(
    (file) =>
      file.includes("template.j2") ||
      file.includes("examples/") ||
      file.includes("scripts/regenerate_examples.py")
  );

  // Regenerate examples if templates changed
  if (hasTemplateChanges) {
    console.log("Template or example files changed, regenerating examples...");
    await $`bun run scripts/regenerate_examples.ts`.cwd("./python");

    // Stage any newly generated files
    await $`git add examples/`.cwd("./python");
  }

  // Run ruff on specific files (ruff supports individual files)
  if (files.length > 0) {
    await $`uv run ruff check --fix ${files}`.cwd("./python");
    await $`uv run ruff format ${files}`.cwd("./python");
  }

  // Run pyright on the whole project (doesn't work well with individual files)
  await $`uv run pyright .`.cwd("./python");

  await $`bun run codespell`;

  process.exit(0);
} catch (error) {
  process.exit(1);
}
