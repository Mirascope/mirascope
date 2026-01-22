/**
 * Content specification types
 *
 * These types are used to define the structure of content in _meta.ts files.
 * They define which documents are available in the site, and how they are organized in the sidebar.
 * They are distinct from the ContentMeta types used at runtime.
 */

// Type for URL-friendly slugs (no slashes)
export type Slug = string; // In practice: enforced by regex /^[a-z0-9-_]+$/

export interface DocInfo {
  label: string;
  path: string; // Doc-relative path for content loading (section/slug format, may include /index)
  routePath: string; // URL path with /docs/ prefix and index pages represented as trailing slashes
  slug: string;
  type: "docs";
  searchWeight: number; // Computed weight based on hierarchical position
}

/**
 * Item in the documentation structure
 */
export interface DocSpec {
  slug: Slug; // URL slug component (no slashes)
  label: string; // Display name in sidebar
  children?: DocSpec[]; // Child items (if this is a folder)
  weight?: number; // Search weight for this item (multiplicative with parent weights)
  hasContent?: boolean; // If true, this item has its own content page (not just a folder). Defaults to true if no children, false if has children.
}

/**
 * Product option for sections with multiple products (e.g., LLM/Ops in Learn)
 */
export interface ProductOption {
  slug: string;
  label: string;
}

/**
 * Section (top-level navigation)
 */
export interface SectionSpec {
  slug: Slug; // Section slug for URL
  label: string; // Display name
  children: DocSpec[]; // Items in this section
  weight?: number; // Search weight for this section (multiplicative with product weight)
  products?: ProductOption[]; // Optional product selector for sections with multiple products
}

/**
 * Version documentation structure
 */
export interface VersionSpec {
  version?: string; // Optional version (e.g., "v1"). When set, included in URL paths like /docs/v1/section/doc
  // All sections (including the main/default section)
  // A section with slug "index" is treated as the default section (no prefix in URL)
  sections: SectionSpec[];
  weight?: number; // Base search weight for this version
}

/**
 * Overall docs structure (VersionSpec for each version)
 */
export type FullDocsSpec = VersionSpec[];

/**
 * Validation results
 */
export interface ValidationResult {
  isValid: boolean;
  errors: string[];
}

/**
 * Process a doc specification and build DocInfo items
 * @param docSpec Doc specification
 * @param pathPrefix Base path for this doc
 * @param parentWeight Accumulated weight from parent nodes
 * @returns Array of DocInfo items from this doc and its children
 */
export function processDocSpec(
  docSpec: DocSpec,
  pathPrefix: string,
  parentWeight: number = 1.0,
): DocInfo[] {
  const result: DocInfo[] = [];

  const slug = docSpec.slug;

  // Calculate the current weight by multiplying parent weight with this item's weight
  // Important to use nullish coalescing to handle zero vs undefined weights.
  const currentWeight = parentWeight * (docSpec.weight ?? 1.0);

  // Path construction for content loading - always include the slug
  const relativePath = pathPrefix ? `${pathPrefix}/${slug}` : slug;
  const docPath = `docs/${relativePath}`;

  // For URL route path: handle index pages with trailing slashes
  let routePath = pathPrefix ? `/docs/${pathPrefix}` : "/docs";
  if (slug !== "index") {
    routePath += `/${slug}`; // Add the slug for non-index pages
  }

  // Add this doc to the result if it's a page (has content)
  // Default: has content if no children, or if explicitly marked with hasContent: true
  if (docSpec.hasContent ?? !docSpec.children) {
    result.push({
      label: docSpec.label,
      slug: docSpec.slug,
      path: docPath,
      routePath,
      type: "docs",
      searchWeight: currentWeight,
    });
  }

  // Process children recursively with updated section path and weight
  if (docSpec.children && docSpec.children.length > 0) {
    docSpec.children.forEach((childSpec) => {
      const childItems = processDocSpec(childSpec, relativePath, currentWeight);
      result.push(...childItems);
    });
  }

  return result;
}

/**
 * Get all docs metadata from a ProductDocsSpec
 * Processes the ProductDocsSpec and returns DocMeta items
 * @param docsSpec The specification to process
 * @returns Array of DocMeta for all products and docs
 */
export function getDocsFromSpec(fullSpec: FullDocsSpec): DocInfo[] {
  const allDocs: DocInfo[] = [];

  fullSpec.forEach((versionSpec) => {
    const { version, sections, weight: versionWeight = 1.0 } = versionSpec;

    const basePathPrefix = version ?? "";

    // Process all sections
    sections.forEach((section) => {
      // For the default section (index), don't add a section slug prefix
      const isDefaultSection = section.slug === "index";
      const sectionPathPrefix = isDefaultSection
        ? basePathPrefix
        : basePathPrefix
          ? `${basePathPrefix}/${section.slug}`
          : section.slug;

      // Calculate section weight (version weight * section weight)
      const sectionWeight = versionWeight * (section.weight ?? 1.0);

      // Process each document in this section
      section.children.forEach((docSpec) => {
        const docItems = processDocSpec(
          docSpec,
          sectionPathPrefix,
          sectionWeight,
        );
        allDocs.push(...docItems);
      });
    });
  });

  return allDocs;
}

/**
 * Validate a slug to ensure it matches URL-friendly format
 *
 * Rules:
 * - Must be lowercase
 * - Can only contain a-z, 0-9, hyphen, and underscore
 * - Cannot contain slashes
 */
export function validateSlug(slug: string): ValidationResult {
  const errors: string[] = [];

  // Check for empty slugs
  if (!slug || slug.trim() === "") {
    errors.push("Slug cannot be empty");
    return { isValid: false, errors };
  }

  // Check for valid characters
  const validSlugRegex = /^[a-z0-9-_]+$/;
  if (!validSlugRegex.test(slug)) {
    errors.push(
      "Slug must contain only lowercase letters, numbers, hyphens, and underscores",
    );
  }

  // Check for slashes
  if (slug.includes("/")) {
    errors.push("Slug cannot contain slashes");
  }

  // Special case for 'index' which is always valid
  if (slug === "index" && errors.length === 0) {
    return { isValid: true, errors: [] };
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
}

/**
 * Checks for duplicate slugs at the same level
 */
function checkDuplicateSlugs(items: DocSpec[]): ValidationResult {
  const errors: string[] = [];
  const slugMap = new Map<string, string[]>();

  // Group items by slug
  items.forEach((item) => {
    if (!slugMap.has(item.slug)) {
      slugMap.set(item.slug, []);
    }
    slugMap.get(item.slug)!.push(item.label);
  });

  // Check for duplicates
  for (const [slug, labels] of slugMap.entries()) {
    if (labels.length > 1) {
      errors.push(
        `Duplicate slug "${slug}" found for items: ${labels.join(", ")}`,
      );
    }
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
}

/**
 * Validate a DocSpec for logical consistency
 */
export function validateDocSpec(spec: DocSpec): ValidationResult {
  const errors: string[] = [];

  // Validate slug
  const slugResult = validateSlug(spec.slug);
  if (!slugResult.isValid) {
    errors.push(
      ...slugResult.errors.map((err) => `Invalid slug "${spec.slug}": ${err}`),
    );
  }

  // Validate children if present
  if (spec.children) {
    // Check for duplicates within children
    const childrenResult = checkDuplicateSlugs(spec.children);
    if (!childrenResult.isValid) {
      errors.push(
        ...childrenResult.errors.map((err) => `In "${spec.label}": ${err}`),
      );
    }

    // Recursively validate each child
    spec.children.forEach((child) => {
      const childResult = validateDocSpec(child);
      if (!childResult.isValid) {
        errors.push(
          ...childResult.errors.map(
            (err) => `In child "${child.label}": ${err}`,
          ),
        );
      }
    });
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
}

/**
 * Validate a SectionSpec
 */
export function validateSectionSpec(spec: SectionSpec): ValidationResult {
  const errors: string[] = [];

  // Validate slug
  const slugResult = validateSlug(spec.slug);
  if (!slugResult.isValid) {
    errors.push(
      ...slugResult.errors.map(
        (err) => `Invalid section slug "${spec.slug}": ${err}`,
      ),
    );
  }

  // Ensure section has children
  if (!spec.children || spec.children.length === 0) {
    errors.push(`Section "${spec.label}" must have at least one child`);
  } else {
    // Check for duplicates within children
    const childrenResult = checkDuplicateSlugs(spec.children);
    if (!childrenResult.isValid) {
      errors.push(
        ...childrenResult.errors.map(
          (err) => `In section "${spec.label}": ${err}`,
        ),
      );
    }

    // Validate each child
    spec.children.forEach((child) => {
      const childResult = validateDocSpec(child);
      if (!childResult.isValid) {
        errors.push(
          ...childResult.errors.map(
            (err) =>
              `In section "${spec.label}", child "${child.label}": ${err}`,
          ),
        );
      }
    });
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
}

/**
 * Validate a VersionSpec
 */
export function validateVersionSpec(spec: VersionSpec): ValidationResult {
  const errors: string[] = [];

  // Validate sections
  if (spec.sections) {
    // Check for duplicate section slugs
    const sectionSlugs = spec.sections.map((s) => s.slug);
    const uniqueSlugs = new Set(sectionSlugs);
    if (uniqueSlugs.size < sectionSlugs.length) {
      errors.push("Duplicate section slugs found");
    }

    // Validate each section
    spec.sections.forEach((section) => {
      const sectionResult = validateSectionSpec(section);
      if (!sectionResult.isValid) {
        errors.push(
          ...sectionResult.errors.map(
            (err) => `In section "${section.label}": ${err}`,
          ),
        );
      }
    });
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
}

/**
 * Validate an entire FullDocsSpec
 */
export function validateDocsSpec(specs: FullDocsSpec): ValidationResult {
  const errors: string[] = [];

  // Check for duplicate versions
  const versionPaths = new Set();
  specs.forEach((versionSpec) => {
    const path = versionSpec.version ? `${versionSpec.version}/` : "";
    if (versionPaths.has(path)) {
      errors.push(`Duplicate version path: ${path}`);
    }
    versionPaths.add(path);
    const versionResult = validateVersionSpec(versionSpec);
    if (!versionResult.isValid) {
      errors.push(
        ...versionResult.errors.map((err) => `In version "${path}": ${err}`),
      );
    }
  });

  return {
    isValid: errors.length === 0,
    errors,
  };
}

/**
 * Validate an entire DocsSpec
 */
export function validateFullDocsSpec(spec: FullDocsSpec): ValidationResult {
  return validateDocsSpec(spec);
}
