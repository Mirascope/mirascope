/**
 * Node.js preload script for Mirascope transformation.
 *
 * This registers the Mirascope ESM loader to apply runtime transformations.
 *
 * ## Usage
 *
 * Run with --import flag:
 * ```bash
 * node --import ./loader.mjs your-script.ts
 * ```
 *
 * Or set NODE_OPTIONS:
 * ```bash
 * NODE_OPTIONS='--import ./loader.mjs' node your-script.ts
 * ```
 */

import { register } from "node:module";

// Register the Mirascope loader
// Note: This requires the package to be built (dist/node-loader.js must exist)
register("mirascope/node-loader", import.meta.url);
