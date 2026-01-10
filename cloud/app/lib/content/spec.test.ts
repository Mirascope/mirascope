import { describe, test, expect } from "vitest";
import {
  validateSlug,
  validateDocSpec,
  validateSectionSpec,
  validateDocsSpec,
  getDocsFromSpec,
  type DocSpec,
  type SectionSpec,
  type FullDocsSpec,
} from "./spec";

describe("validateSlug", () => {
  test("valid slugs pass validation", () => {
    expect(validateSlug("valid-slug").isValid).toBe(true);
    expect(validateSlug("valid_slug").isValid).toBe(true);
    expect(validateSlug("validslug123").isValid).toBe(true);
    expect(validateSlug("index").isValid).toBe(true); // Special case
  });

  test("invalid slugs fail validation", () => {
    expect(validateSlug("").isValid).toBe(false);
    expect(validateSlug("Invalid").isValid).toBe(false); // Contains uppercase
    expect(validateSlug("invalid/slug").isValid).toBe(false); // Contains slash
    expect(validateSlug("invalid slug").isValid).toBe(false); // Contains space
    expect(validateSlug("invalid.slug").isValid).toBe(false); // Contains period
  });

  test("error messages are descriptive", () => {
    const result = validateSlug("Invalid/slug");
    expect(result.isValid).toBe(false);
    expect(result.errors.length).toBe(2);
    expect(result.errors[0]).toContain("must contain only lowercase");
    expect(result.errors[1]).toContain("cannot contain slashes");
  });
});

describe("validateDocSpec", () => {
  test("valid DocSpec passes validation", () => {
    const validDoc: DocSpec = {
      slug: "valid-slug",
      label: "Valid Document",
    };
    expect(validateDocSpec(validDoc).isValid).toBe(true);
  });

  test("invalid slug fails validation", () => {
    const invalidDoc: DocSpec = {
      slug: "Invalid/slug",
      label: "Invalid Document",
    };
    expect(validateDocSpec(invalidDoc).isValid).toBe(false);
  });

  test("nested children are validated", () => {
    const docWithInvalidChild: DocSpec = {
      slug: "valid-parent",
      label: "Parent",
      children: [
        {
          slug: "invalid/child",
          label: "Invalid Child",
        },
      ],
    };
    const result = validateDocSpec(docWithInvalidChild);
    expect(result.isValid).toBe(false);
    expect(result.errors[0]).toContain('In child "Invalid Child"');
  });

  test("duplicate child slugs fail validation", () => {
    const docWithDupeChildren: DocSpec = {
      slug: "valid-parent",
      label: "Parent",
      children: [
        { slug: "dupe", label: "Child 1" },
        { slug: "dupe", label: "Child 2" },
      ],
    };
    const result = validateDocSpec(docWithDupeChildren);
    expect(result.isValid).toBe(false);
    expect(result.errors[0]).toContain("Duplicate slug");
  });
});

describe("validateSectionSpec", () => {
  test("valid section passes validation", () => {
    const validSection: SectionSpec = {
      slug: "valid-section",
      label: "Valid Section",
      children: [
        { slug: "child1", label: "Child 1" },
        { slug: "child2", label: "Child 2" },
      ],
    };
    expect(validateSectionSpec(validSection).isValid).toBe(true);
  });

  test("section without children fails validation", () => {
    const emptySection: SectionSpec = {
      slug: "empty-section",
      label: "Empty Section",
      children: [],
    };
    const result = validateSectionSpec(emptySection);
    expect(result.isValid).toBe(false);
    expect(result.errors[0]).toContain("must have at least one child");
  });
});

describe("validateDocsSpec", () => {
  test("valid docs spec passes validation", () => {
    const validDocs: FullDocsSpec = {
      sections: [
        {
          slug: "api",
          label: "API",
          children: [{ slug: "overview", label: "Overview" }],
        },
      ],
    };
    expect(validateDocsSpec(validDocs).isValid).toBe(true);
  });

  test("docs spec with duplicate sections fails validation", () => {
    const docsWithDupeSections: FullDocsSpec = {
      sections: [
        {
          slug: "api",
          label: "API",
          children: [{ slug: "overview", label: "Overview" }],
        },
        {
          slug: "api", // Duplicate slug
          label: "API Reference",
          children: [{ slug: "reference", label: "Reference" }],
        },
      ],
    };
    const result = validateDocsSpec(docsWithDupeSections);
    expect(result.isValid).toBe(false);
    expect(result.errors[0]).toContain("Duplicate section slugs");
  });
});

describe("getDocsFromSpec", () => {
  test("generates paths without version when version is not set", () => {
    const docsSpec: FullDocsSpec = {
      sections: [
        {
          slug: "api",
          label: "API",
          children: [{ slug: "overview", label: "Overview" }],
        },
      ],
    };

    const result = getDocsFromSpec(docsSpec);

    expect(result).toHaveLength(1);
    expect(result[0]).toMatchObject({
      label: "Overview",
      slug: "overview",
      path: "docs/api/overview",
      routePath: "/docs/api/overview",
      type: "docs",
    });
  });

  test("generates paths with version when version is set on section", () => {
    const docsSpec: FullDocsSpec = {
      sections: [
        {
          slug: "api",
          label: "API",
          version: "v1",
          children: [{ slug: "overview", label: "Overview" }],
        },
      ],
    };

    const result = getDocsFromSpec(docsSpec);

    expect(result).toHaveLength(1);
    expect(result[0]).toMatchObject({
      label: "Overview",
      slug: "overview",
      path: "docs/v1/api/overview",
      routePath: "/docs/v1/api/overview",
      type: "docs",
    });
  });

  test("generates paths with version only for default section (index)", () => {
    const docsSpec: FullDocsSpec = {
      sections: [
        {
          slug: "index",
          label: "Docs",
          version: "v1",
          children: [{ slug: "getting-started", label: "Getting Started" }],
        },
      ],
    };

    const result = getDocsFromSpec(docsSpec);

    expect(result).toHaveLength(1);
    expect(result[0]).toMatchObject({
      label: "Getting Started",
      slug: "getting-started",
      path: "docs/v1/getting-started",
      routePath: "/docs/v1/getting-started",
      type: "docs",
    });
  });

  test("generates paths without version for default section when version not set", () => {
    const docsSpec: FullDocsSpec = {
      sections: [
        {
          slug: "index",
          label: "Docs",
          children: [{ slug: "getting-started", label: "Getting Started" }],
        },
      ],
    };

    const result = getDocsFromSpec(docsSpec);

    expect(result).toHaveLength(1);
    expect(result[0]).toMatchObject({
      label: "Getting Started",
      slug: "getting-started",
      path: "docs/getting-started",
      routePath: "/docs/getting-started",
      type: "docs",
    });
  });

  test("handles nested docs with version", () => {
    const docsSpec: FullDocsSpec = {
      sections: [
        {
          slug: "index",
          label: "Docs",
          version: "v1",
          children: [
            {
              slug: "getting-started",
              label: "Getting Started",
              hasContent: true, // Parent has its own content page
              children: [
                { slug: "why", label: "Why Mirascope?" },
                { slug: "help", label: "Help" },
              ],
            },
          ],
        },
      ],
    };

    const result = getDocsFromSpec(docsSpec);

    expect(result).toHaveLength(3);
    expect(result[0]).toMatchObject({
      label: "Getting Started",
      slug: "getting-started",
      path: "docs/v1/getting-started",
      routePath: "/docs/v1/getting-started",
    });
    expect(result[1]).toMatchObject({
      label: "Why Mirascope?",
      slug: "why",
      path: "docs/v1/getting-started/why",
      routePath: "/docs/v1/getting-started/why",
    });
    expect(result[2]).toMatchObject({
      label: "Help",
      slug: "help",
      path: "docs/v1/getting-started/help",
      routePath: "/docs/v1/getting-started/help",
    });
  });

  test("handles multiple sections with mixed versions", () => {
    const docsSpec: FullDocsSpec = {
      sections: [
        {
          slug: "index",
          label: "Docs",
          version: "v1",
          children: [{ slug: "welcome", label: "Welcome" }],
        },
        {
          slug: "api",
          label: "API",
          version: "v1",
          children: [{ slug: "overview", label: "Overview" }],
        },
      ],
    };

    const result = getDocsFromSpec(docsSpec);

    expect(result).toHaveLength(2);
    expect(result[0]).toMatchObject({
      label: "Welcome",
      slug: "welcome",
      path: "docs/v1/welcome",
      routePath: "/docs/v1/welcome",
    });
    expect(result[1]).toMatchObject({
      label: "Overview",
      slug: "overview",
      path: "docs/v1/api/overview",
      routePath: "/docs/v1/api/overview",
    });
  });

  test("handles sections with and without version in same spec", () => {
    const docsSpec: FullDocsSpec = {
      sections: [
        {
          slug: "index",
          label: "Docs",
          // No version - unversioned section
          children: [{ slug: "getting-started", label: "Getting Started" }],
        },
        {
          slug: "api",
          label: "API",
          version: "v1",
          children: [{ slug: "overview", label: "Overview" }],
        },
      ],
    };

    const result = getDocsFromSpec(docsSpec);

    expect(result).toHaveLength(2);
    expect(result[0]).toMatchObject({
      label: "Getting Started",
      slug: "getting-started",
      path: "docs/getting-started",
      routePath: "/docs/getting-started",
    });
    expect(result[1]).toMatchObject({
      label: "Overview",
      slug: "overview",
      path: "docs/v1/api/overview",
      routePath: "/docs/v1/api/overview",
    });
  });

  test("handles index pages with trailing slashes", () => {
    const docsSpec: FullDocsSpec = {
      sections: [
        {
          slug: "index",
          label: "Docs",
          version: "v1",
          children: [{ slug: "index", label: "Welcome" }],
        },
      ],
    };

    const result = getDocsFromSpec(docsSpec);

    expect(result).toHaveLength(1);
    expect(result[0]).toMatchObject({
      label: "Welcome",
      slug: "index",
      path: "docs/v1/index",
      routePath: "/docs/v1", // Index pages use trailing slash (no /index in route)
    });
  });

  test("handles docs without content (folder only)", () => {
    const docsSpec: FullDocsSpec = {
      sections: [
        {
          slug: "index",
          label: "Docs",
          version: "v1",
          children: [
            {
              slug: "folder",
              label: "Folder",
              hasContent: false,
              children: [{ slug: "child", label: "Child" }],
            },
          ],
        },
      ],
    };

    const result = getDocsFromSpec(docsSpec);

    expect(result).toHaveLength(1); // Only the child, not the folder
    expect(result[0]).toMatchObject({
      label: "Child",
      slug: "child",
      path: "docs/v1/folder/child",
      routePath: "/docs/v1/folder/child",
    });
  });
});
