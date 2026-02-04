/**
 * Shared types for the Mirascope CLI and registry.
 */

/** A file within a registry item. */
export interface RegistryFile {
  /** Source path within the registry item. */
  path: string;
  /** Target path where the file will be written. */
  target: string;
  /** File content (populated in built registry items). */
  content: string;
  /** Optional file type annotation. */
  type?: string;
}

/** Dependencies required by a registry item. */
export interface RegistryDependencies {
  /** Python pip packages. */
  pip: string[];
  /** npm packages. */
  npm: string[];
}

/** Version constraints for Mirascope compatibility. */
export interface RegistryVersionConstraint {
  /** Minimum compatible version. */
  minVersion?: string;
  /** Maximum compatible version. */
  maxVersion?: string;
}

/** A registry item (tool, agent, prompt, or integration). */
export interface RegistryItem {
  /** Unique item name. */
  name: string;
  /** Item type (e.g., "registry:tool", "registry:agent"). */
  type: string;
  /** Human-readable title. */
  title?: string;
  /** Description of the item. */
  description?: string;
  /** Item version. */
  version?: string;
  /** Language this item is for (python or typescript). */
  language?: string;
  /** Categories for filtering/searching. */
  categories?: string[];
  /** Mirascope version constraints by language. */
  mirascope?: Record<string, RegistryVersionConstraint>;
  /** Files included in this item. */
  files: RegistryFile[];
  /** External dependencies. */
  dependencies: RegistryDependencies;
  /** Other registry items this depends on. */
  registryDependencies?: string[];
}

/** An item entry in the registry index. */
export interface RegistryIndexItem {
  /** Item name. */
  name: string;
  /** Item type. */
  type: string;
  /** Path within the registry. */
  path: string;
  /** Optional description. */
  description?: string;
}

/** The registry index containing all available items. */
export interface RegistryIndex {
  /** Registry name. */
  name: string;
  /** Registry version. */
  version: string;
  /** Registry homepage URL. */
  homepage?: string;
  /** All items in the registry. */
  items: RegistryIndexItem[];
}

/** Mirascope project configuration (mirascope.json). */
export interface MirascopeConfig {
  /** JSON schema URL. */
  $schema?: string;
  /** Project language (python or typescript). */
  language?: string;
  /** Registry URL. */
  registry?: string;
  /** Path mappings for item types. */
  paths?: Record<string, string>;
}
