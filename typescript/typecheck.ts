#!/usr/bin/env bun
// TypeScript typecheck script for lint-staged (ignores file arguments)
import { $ } from 'bun';

try {
  await $`bun run typecheck`.cwd('./typescript');
  process.exit(0);
} catch (error) {
  process.exit(1);
}
