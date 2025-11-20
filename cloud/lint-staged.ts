#!/usr/bin/env bun
// Cloud lint-staged script
import { $ } from "bun";

const files = process.argv.slice(2);

try {
  // Run typecheck first on whole project (fails fast)
  await $`bun run typecheck`.cwd("./cloud");

  // Run formatter on specific files
  if (files.length > 0) {
    await $`bunx prettier --write ${files}`.cwd("./cloud");
  }

  // Run ESLint with fix on specific files
  if (files.length > 0) {
    await $`bunx eslint --fix ${files}`.cwd("./cloud");
  }

  process.exit(0);
} catch (error) {
  process.exit(1);
}
