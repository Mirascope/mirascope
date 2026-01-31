/**
 * Add command - Install registry items into a project.
 */

import { join } from "path";

import type { RegistryItem } from "@/cli/registry/types";

import { RegistryClient } from "@/cli/registry/client";
import { loadConfig } from "@/cli/utils/config";
import { writeFile } from "@/cli/utils/file-ops";

async function loadLocalItem(itemPath: string): Promise<RegistryItem | null> {
  try {
    // eslint-disable-next-line no-undef
    const file = Bun.file(itemPath);
    if (!(await file.exists())) {
      return null;
    }
    return (await file.json()) as RegistryItem;
  } catch {
    return null;
  }
}

export async function addCommand(
  items: string[],
  path: string | undefined,
  overwrite: boolean,
  registryUrl: string,
): Promise<void> {
  const config = await loadConfig();
  const basePath = path ?? process.cwd();
  const client = new RegistryClient(registryUrl);

  const allDependencies: { pip: string[]; npm: string[] } = {
    pip: [],
    npm: [],
  };
  const filesWritten: string[] = [];

  for (const itemName of items) {
    console.log(`Adding ${itemName}...`);

    let item: RegistryItem | null = null;

    // Check if it's a local file path
    if (
      itemName.startsWith("./") ||
      itemName.startsWith("/") ||
      itemName.endsWith(".json")
    ) {
      item = await loadLocalItem(itemName);
      if (!item) {
        console.error(`Error: Local file '${itemName}' not found.`);
        process.exit(1);
        return;
      }
    } else {
      try {
        item = await client.fetchItem(itemName, "typescript");
      } catch (e) {
        console.error(`Error: Failed to fetch '${itemName}': ${String(e)}`);
        process.exit(1);
        return;
      }

      if (!item) {
        console.error(`Error: Item '${itemName}' not found in registry.`);
        process.exit(1);
        return;
      }
    }

    // Write each file from the registry item
    for (const fileInfo of item.files ?? []) {
      let target = fileInfo.target ?? fileInfo.path ?? "";
      const content = fileInfo.content ?? "";

      // Use configured paths based on item type
      if (config?.paths) {
        const itemType = (item.type ?? "").replace("registry:", "");
        const typePath = config.paths[`${itemType}s`];
        if (typePath) {
          // Replace the first directory component with the configured path
          const targetParts = target.split("/");
          if (targetParts.length > 1) {
            target = [typePath, ...targetParts.slice(1)].join("/");
          } else if (targetParts.length === 1) {
            target = `${typePath}/${targetParts[0]}`;
          }
        }
      }

      const targetPath = join(basePath, target);

      // eslint-disable-next-line no-undef
      const file = Bun.file(targetPath);
      if ((await file.exists()) && !overwrite) {
        console.error(
          `Warning: ${targetPath} already exists. Use --overwrite to replace.`,
        );
        continue;
      }

      try {
        await writeFile(targetPath, content);
        filesWritten.push(targetPath);
        console.log(`  Created ${targetPath}`);
      } catch (e) {
        console.error(`Error: Failed to write ${targetPath}: ${String(e)}`);
        process.exit(1);
        return;
      }
    }

    // Collect dependencies
    const deps = item.dependencies ?? {};
    for (const pipDep of deps.pip ?? []) {
      if (!allDependencies.pip.includes(pipDep)) {
        allDependencies.pip.push(pipDep);
      }
    }
    for (const npmDep of deps.npm ?? []) {
      if (!allDependencies.npm.includes(npmDep)) {
        allDependencies.npm.push(npmDep);
      }
    }
  }

  if (filesWritten.length > 0) {
    console.log(`\nSuccessfully added ${filesWritten.length} file(s).`);
  }

  if (allDependencies.npm.length > 0) {
    console.log("\nInstall required npm dependencies:");
    console.log(`  bun add ${allDependencies.npm.join(" ")}`);
  }
}
