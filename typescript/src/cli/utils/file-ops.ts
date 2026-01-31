/**
 * File operations for the Mirascope CLI.
 */

import { mkdir } from "fs/promises";
import { dirname } from "path";

export async function writeFile(path: string, content: string): Promise<void> {
  // Create parent directories if they don't exist
  const dir = dirname(path);
  await mkdir(dir, { recursive: true });

  // Write the file
  // eslint-disable-next-line no-undef
  await Bun.write(path, content);
}

export async function ensureDirectory(path: string): Promise<void> {
  await mkdir(path, { recursive: true });
}
