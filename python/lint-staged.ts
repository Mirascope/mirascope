#!/usr/bin/env bun
// Python lint-staged script
import { $ } from 'bun';

const files = process.argv.slice(2);

try {
  // Run ruff on specific files (ruff supports individual files)
  if (files.length > 0) {
    await $`uv run ruff check --fix ${files}`.cwd('./python');
  }
  
  // Run pyright on the whole project (doesn't work well with individual files)
  await $`uv run pyright`.cwd('./python');
  
  process.exit(0);
} catch (error) {
  process.exit(1);
}