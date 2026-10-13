/**
 * Node.js preload script for Mirascope transformation.
 *
 * Registers the Mirascope ESM loader to apply runtime transformations
 * (tool schema injection, format schemas, versioning metadata).
 *
 * ## Usage
 *
 * Run with --import flag:
 * ```bash
 * node --import mirascope/loader your-script.ts
 * ```
 *
 * Or set NODE_OPTIONS:
 * ```bash
 * NODE_OPTIONS='--import mirascope/loader' node your-script.ts
 * ```
 */

import { register } from "node:module";

register("mirascope/node-loader", import.meta.url);
