#!/usr/bin/env bun
// Cloud lint-staged script
import { $ } from "bun";

const files = process.argv.slice(2);

try {
  // Run typecheck first on whole project (fails fast)
  await $`bun run typecheck`.cwd("./cloud");

  // If any staged files are in dispatch-worker, also typecheck it
  const hasDispatchWorker = files.some((f) =>
    f.includes("claws/dispatch-worker"),
  );
  if (hasDispatchWorker) {
    await $`bun run typecheck`.cwd("./cloud/claws/dispatch-worker");
  }

  // Run formatter on specific files
  if (files.length > 0) {
    await $`bunx oxfmt --ignore-path .oxfmtignore ${files}`.cwd("./cloud");
  }

  // Run oxlint with fix on specific files
  if (files.length > 0) {
    await $`bunx oxlint --fix ${files}`.cwd("./cloud");
  }

  // Run dispatch-worker oxlint on its own files
  if (hasDispatchWorker) {
    const dispatchWorkerFiles = files.filter((f) =>
      f.includes("claws/dispatch-worker"),
    );
    if (dispatchWorkerFiles.length > 0) {
      await $`bunx oxlint --fix ${dispatchWorkerFiles}`.cwd(
        "./cloud/claws/dispatch-worker",
      );
    }
  }

  process.exit(0);
} catch {
  process.exit(1);
}
