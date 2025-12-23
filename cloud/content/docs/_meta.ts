/**
 * Documentation structure for all products
 *
 * This file defines the structure, order, and metadata for all documentation.
 * We use the ProductDocsSpec format defined in src/lib/content/spec.ts.
 */

// Import product-specific metadata
import mirascopeSpec from "./mirascope/_meta";
import mirascopeSpecV2 from "./mirascope/v2/_meta";
import lilypadSpec from "./lilypad/_meta";

import type { FullDocsSpec } from "@/app/lib/content/spec";

// Build spec with all products
const spec: FullDocsSpec = [mirascopeSpec, lilypadSpec, mirascopeSpecV2];

// Default export the spec
export default spec;
