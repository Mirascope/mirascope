/**
 * Closure data structure for function versioning.
 *
 * Represents a complete closure including the function's code, dependencies,
 * and metadata for consistent hashing and versioning.
 */

import { execSync } from "child_process";
import { createHash } from "crypto";
import * as fs from "fs";
import * as os from "os";
import * as path from "path";

/**
 * Information about a package dependency.
 */
export interface DependencyInfo {
  /** The package version */
  version: string;
  /** Optional extras/features enabled */
  extras?: string[];
}

/**
 * Complete closure information for a versioned function.
 *
 * Contains all the information needed to uniquely identify a function version,
 * including its source code, dependencies, and computed hashes.
 */
export interface Closure {
  /** The function's qualified name */
  name: string;
  /** Function signature (parameters and return type) */
  signature: string;
  /** Complete source code including all dependencies */
  code: string;
  /** SHA256 hash of the formatted code */
  hash: string;
  /** SHA256 hash of the signature only */
  signatureHash: string;
  /** Package dependencies with their versions */
  dependencies: Record<string, DependencyInfo>;
}

/**
 * Raw closure data before formatting and hashing.
 */
export interface RawClosure {
  /** The function's name */
  name: string;
  /** Function signature */
  signature: string;
  /** Import statements */
  imports: string[];
  /** Global variable assignments */
  globals: string[];
  /** Dependency function/class definitions */
  definitions: string[];
  /** The main function declaration */
  mainDeclaration: string;
  /** Package dependencies */
  dependencies: Record<string, DependencyInfo>;
}

/**
 * Format TypeScript code using oxfmt for consistent output.
 *
 * Uses synchronous CLI invocation to match the synchronous nature
 * of TypeScript transformers.
 *
 * @param code - The TypeScript code to format
 * @returns The formatted code
 */
export function formatWithOxfmt(code: string): string {
  const tmpFile = path.join(
    os.tmpdir(),
    `closure-${Date.now()}-${Math.random().toString(36).slice(2)}.ts`,
  );

  try {
    fs.writeFileSync(tmpFile, code, "utf-8");

    try {
      // Run oxfmt via bunx - it modifies the file in place
      execSync(`bunx oxfmt "${tmpFile}"`, {
        stdio: "pipe",
        encoding: "utf-8",
      });
      return fs.readFileSync(tmpFile, "utf-8");
    } catch {
      // If oxfmt fails, return the original code
      // This allows graceful degradation when oxfmt is unavailable
      return code;
    }
  } finally {
    try {
      fs.unlinkSync(tmpFile);
    } catch {
      // Ignore cleanup errors
    }
  }
}

/**
 * Compute SHA256 hash of a string.
 *
 * @param content - The content to hash
 * @returns The hex-encoded hash
 */
export function computeHash(content: string): string {
  return createHash("sha256").update(content).digest("hex");
}

/**
 * Assemble raw closure data into complete code.
 *
 * Combines imports, globals, definitions, and the main declaration
 * into a single code string, formatted with oxfmt.
 *
 * @param raw - The raw closure data
 * @returns The assembled and formatted code
 */
export function assembleCode(raw: RawClosure): string {
  const parts: string[] = [];

  // Add imports (sorted for consistency)
  if (raw.imports.length > 0) {
    parts.push(raw.imports.sort().join("\n"));
  }

  // Add global assignments
  if (raw.globals.length > 0) {
    parts.push(raw.globals.join("\n"));
  }

  // Add dependency definitions
  if (raw.definitions.length > 0) {
    parts.push(raw.definitions.join("\n\n"));
  }

  // Add main function declaration
  parts.push(raw.mainDeclaration);

  // Join with double newlines and format
  const assembled = parts.join("\n\n");
  return formatWithOxfmt(assembled);
}

/**
 * Create a Closure from raw closure data.
 *
 * Assembles the code, formats it, and computes hashes.
 *
 * @param raw - The raw closure data
 * @returns The complete Closure
 */
export function createClosure(raw: RawClosure): Closure {
  const code = assembleCode(raw);
  const hash = computeHash(code);
  const signatureHash = computeHash(raw.signature);

  return {
    name: raw.name,
    signature: raw.signature,
    code,
    hash,
    signatureHash,
    dependencies: raw.dependencies,
  };
}
