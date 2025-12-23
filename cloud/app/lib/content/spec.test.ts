import { describe, it, expect } from "vitest";
import {
  validateSlug,
  validateDocSpec,
  validateSectionSpec,
  validateProductSpec,
  type DocSpec,
  type SectionSpec,
  type ProductSpec,
} from "./spec";

describe("validateSlug", () => {
  it("valid slugs pass validation", () => {
    expect(validateSlug("valid-slug").isValid).toBe(true);
    expect(validateSlug("valid_slug").isValid).toBe(true);
    expect(validateSlug("validslug123").isValid).toBe(true);
    expect(validateSlug("index").isValid).toBe(true); // Special case
  });

  it("invalid slugs fail validation", () => {
    expect(validateSlug("").isValid).toBe(false);
    expect(validateSlug("Invalid").isValid).toBe(false); // Contains uppercase
    expect(validateSlug("invalid/slug").isValid).toBe(false); // Contains slash
    expect(validateSlug("invalid slug").isValid).toBe(false); // Contains space
    expect(validateSlug("invalid.slug").isValid).toBe(false); // Contains period
  });

  it("error messages are descriptive", () => {
    const result = validateSlug("Invalid/slug");
    expect(result.isValid).toBe(false);
    expect(result.errors.length).toBe(2);
    expect(result.errors[0]).toContain("must contain only lowercase");
    expect(result.errors[1]).toContain("cannot contain slashes");
  });
});

describe("validateDocSpec", () => {
  it("valid DocSpec passes validation", () => {
    const validDoc: DocSpec = {
      slug: "valid-slug",
      label: "Valid Document",
    };
    expect(validateDocSpec(validDoc).isValid).toBe(true);
  });

  it("invalid slug fails validation", () => {
    const invalidDoc: DocSpec = {
      slug: "Invalid/slug",
      label: "Invalid Document",
    };
    expect(validateDocSpec(invalidDoc).isValid).toBe(false);
  });

  it("nested children are validated", () => {
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

  it("duplicate child slugs fail validation", () => {
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
  it("valid section passes validation", () => {
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

  it("section without children fails validation", () => {
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

describe("validateProductSpec", () => {
  it("valid product passes validation", () => {
    const validProduct: ProductSpec = {
      product: { name: "mirascope" },
      sections: [
        {
          slug: "api",
          label: "API",
          children: [{ slug: "overview", label: "Overview" }],
        },
      ],
    };
    expect(validateProductSpec(validProduct).isValid).toBe(true);
  });

  it("product with duplicate sections fails validation", () => {
    const productWithDupeSections: ProductSpec = {
      product: { name: "mirascope" },
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
    const result = validateProductSpec(productWithDupeSections);
    expect(result.isValid).toBe(false);
    expect(result.errors[0]).toContain("Duplicate section slugs");
  });
});
