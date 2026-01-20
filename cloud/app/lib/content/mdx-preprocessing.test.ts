import { describe, test, expect, vi, beforeEach } from "vitest";
import { preprocessMdx } from "./mdx-preprocessing";

// Mock fs/promises
vi.mock("fs/promises", () => ({
  readFile: vi.fn(),
}));

import { readFile } from "fs/promises";

const mockedReadFile = vi.mocked(readFile);

describe("preprocessMdx", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test("strips frontmatter from content - frontmatter should NOT appear in returned content", async () => {
    const mdxWithFrontmatter = `---
title: "Test Blog Post"
description: "A test description"
date: "2025-01-15"
author: "Test Author"
---

# Hello World

This is the actual content.`;

    mockedReadFile.mockResolvedValue(mdxWithFrontmatter);

    const result = await preprocessMdx("/fake/path/content/docs/test.mdx");

    // Frontmatter should be extracted to the frontmatter object
    expect(result.frontmatter).toEqual({
      title: "Test Blog Post",
      description: "A test description",
      date: "2025-01-15",
      author: "Test Author",
    });

    // Content should NOT contain frontmatter delimiters or frontmatter values
    expect(result.content).not.toContain("---");
    expect(result.content).not.toContain("title:");
    expect(result.content).not.toContain("description:");
    expect(result.content).not.toContain("date:");
    expect(result.content).not.toContain("author:");
    expect(result.content).not.toContain("Test Blog Post");
    expect(result.content).not.toContain("A test description");

    // Content SHOULD contain the actual MDX content
    expect(result.content).toContain("# Hello World");
    expect(result.content).toContain("This is the actual content.");
  });

  test("extracts table of contents from content without frontmatter", async () => {
    const mdxWithFrontmatter = `---
title: "Document with Headings"
---

# Main Title

Some intro text.

## Section One

Content for section one.

## Section Two

Content for section two.

### Subsection

Nested content.`;

    mockedReadFile.mockResolvedValue(mdxWithFrontmatter);

    const result = await preprocessMdx("/fake/path/content/docs/test.mdx");

    // Table of contents should be extracted from the headings
    expect(result.tableOfContents).toHaveLength(4);
    expect(result.tableOfContents[0]).toEqual({
      id: "main-title",
      content: "Main Title",
      level: 1,
    });
    expect(result.tableOfContents[1]).toEqual({
      id: "section-one",
      content: "Section One",
      level: 2,
    });
    expect(result.tableOfContents[2]).toEqual({
      id: "section-two",
      content: "Section Two",
      level: 2,
    });
    expect(result.tableOfContents[3]).toEqual({
      id: "subsection",
      content: "Subsection",
      level: 3,
    });

    // Frontmatter title should NOT be in the table of contents
    expect(result.tableOfContents.map((t) => t.content)).not.toContain(
      "Document with Headings",
    );
  });

  test("handles content without frontmatter", async () => {
    const mdxWithoutFrontmatter = `# Just Content

No frontmatter here, just markdown.`;

    mockedReadFile.mockResolvedValue(mdxWithoutFrontmatter);

    const result = await preprocessMdx("/fake/path/content/docs/test.mdx");

    expect(result.frontmatter).toEqual({});
    expect(result.content).toBe(mdxWithoutFrontmatter);
    expect(result.tableOfContents).toHaveLength(1);
    expect(result.tableOfContents[0].content).toBe("Just Content");
  });

  test("returns PreprocessedMDX with all required fields", async () => {
    const mdx = `---
title: "Complete Example"
---

# Heading

Content.`;

    mockedReadFile.mockResolvedValue(mdx);

    const result = await preprocessMdx("/fake/path/content/docs/test.mdx");

    // Verify the shape of PreprocessedMDX
    expect(result).toHaveProperty("frontmatter");
    expect(result).toHaveProperty("tableOfContents");
    expect(result).toHaveProperty("content");

    // Verify types
    expect(typeof result.frontmatter).toBe("object");
    expect(Array.isArray(result.tableOfContents)).toBe(true);
    expect(typeof result.content).toBe("string");
  });
});
