#!/usr/bin/env bun
// Cloud lint-staged script
import { $ } from "bun";

const files = process.argv.slice(2);

try {
  // Run typecheck first on whole project (fails fast)
  await $`bun run typecheck`.cwd("./cloud");

  // Run formatter on specific files
  if (files.length > 0) {
    await $`bunx oxfmt --ignore-path .oxfmtignore ${files}`.cwd("./cloud");
  }

  // Run oxlint with fix on specific files
  if (files.length > 0) {
    await $`bunx oxlint --fix ${files}`.cwd("./cloud");
  }

  process.exit(0);
} catch {
  process.exit(1);
}
