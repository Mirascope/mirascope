#!/usr/bin/env bun
/**
 * Build script for the Mirascope registry.
 *
 * Reads registry items from the registry/ directory and generates
 * static JSON files in public/r/ for serving.
 *
 * Usage: bun run scripts/registry/build.ts
 */

import { readdir, readFile, writeFile, mkdir } from "fs/promises";
import { join, dirname } from "path";

const REGISTRY_DIR = join(import.meta.dir, "../../registry");
const OUTPUT_DIR = join(import.meta.dir, "../../cloud/public/r");

interface RegistryItemFile {
  path: string;
  target: string;
  content?: string;
}

interface RegistryItem {
  name: string;
  type: string;
  title: string;
  description: string;
  version: string;
  categories: string[];
  mirascope: {
    python?: { minVersion: string };
    typescript?: { minVersion: string };
  };
  files: {
    python?: RegistryItemFile[];
    typescript?: RegistryItemFile[];
  };
  dependencies: {
    pip: string[];
    npm: string[];
  };
  registryDependencies: string[];
}

interface RegistryIndexItem {
  name: string;
  type: string;
  path: string;
  description?: string;
}

interface RegistryIndex {
  name: string;
  version: string;
  homepage: string;
  items: RegistryIndexItem[];
}

async function readJsonFile<T>(path: string): Promise<T> {
  const content = await readFile(path, "utf-8");
  return JSON.parse(content) as T;
}

async function writeJsonFile(path: string, data: unknown): Promise<void> {
  await mkdir(dirname(path), { recursive: true });
  await writeFile(path, JSON.stringify(data, null, 2) + "\n");
}

async function buildItem(
  itemPath: string,
  language: "python" | "typescript"
): Promise<{
  name: string;
  type: string;
  language: string;
  title: string;
  description: string;
  files: RegistryItemFile[];
  dependencies: { pip: string[]; npm: string[] };
  registryDependencies: string[];
} | null> {
  const itemJsonPath = join(itemPath, "registry-item.json");
  const item = await readJsonFile<RegistryItem>(itemJsonPath);

  const files = item.files[language];
  if (!files || files.length === 0) {
    return null;
  }

  // Read file contents
  const filesWithContent: RegistryItemFile[] = [];
  for (const file of files) {
    const filePath = join(itemPath, file.path);
    try {
      const content = await readFile(filePath, "utf-8");
      filesWithContent.push({
        path: file.path,
        target: file.target,
        content,
      });
    } catch (e) {
      console.warn(`Warning: Could not read ${filePath}`);
    }
  }

  return {
    name: item.name,
    type: item.type,
    language,
    title: item.title,
    description: item.description,
    files: filesWithContent,
    dependencies: item.dependencies,
    registryDependencies: item.registryDependencies,
  };
}

async function findItems(dir: string): Promise<string[]> {
  const items: string[] = [];

  async function walk(currentDir: string): Promise<void> {
    const entries = await readdir(currentDir, { withFileTypes: true });

    for (const entry of entries) {
      const entryPath = join(currentDir, entry.name);

      if (entry.isDirectory()) {
        // Check if this directory contains a registry-item.json
        try {
          await readFile(join(entryPath, "registry-item.json"));
          items.push(entryPath);
        } catch {
          // Not a registry item, recurse into it
          await walk(entryPath);
        }
      }
    }
  }

  await walk(dir);
  return items;
}

async function main(): Promise<void> {
  console.log("Building Mirascope registry...\n");

  // Read the main registry.json
  const registryJsonPath = join(REGISTRY_DIR, "registry.json");
  const registry = await readJsonFile<RegistryIndex>(registryJsonPath);

  // Find all registry items
  const itemPaths = await findItems(REGISTRY_DIR);
  console.log(`Found ${itemPaths.length} registry item(s)\n`);

  // Build each item for both languages
  const indexItems: RegistryIndexItem[] = [];

  for (const itemPath of itemPaths) {
    const itemJsonPath = join(itemPath, "registry-item.json");
    const item = await readJsonFile<RegistryItem>(itemJsonPath);

    console.log(`Building ${item.name}...`);

    // Build Python version
    const pythonItem = await buildItem(itemPath, "python");
    if (pythonItem) {
      const outputPath = join(OUTPUT_DIR, `${item.name}.python.json`);
      await writeJsonFile(outputPath, pythonItem);
      console.log(`  Created ${outputPath}`);
    }

    // Build TypeScript version
    const tsItem = await buildItem(itemPath, "typescript");
    if (tsItem) {
      const outputPath = join(OUTPUT_DIR, `${item.name}.typescript.json`);
      await writeJsonFile(outputPath, tsItem);
      console.log(`  Created ${outputPath}`);
    }

    // Add to index
    indexItems.push({
      name: item.name,
      type: item.type.replace("registry:", ""),
      path: itemPath.replace(REGISTRY_DIR + "/", ""),
      description: item.description,
    });
  }

  // Write the index file
  const indexOutput = {
    name: registry.name,
    version: registry.version,
    homepage: registry.homepage,
    items: indexItems,
  };
  const indexPath = join(OUTPUT_DIR, "index.json");
  await writeJsonFile(indexPath, indexOutput);
  console.log(`\nCreated ${indexPath}`);

  console.log("\nRegistry build complete!");
}

main().catch((e) => {
  console.error("Build failed:", e);
  process.exit(1);
});
