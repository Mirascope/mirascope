import { describe, test, expect } from "bun:test";
import { parseFrontmatter, mergeFrontmatter } from "./mdx-processing";

describe("Frontmatter Parser", () => {
  describe("parseFrontmatter", () => {
    test("extracts frontmatter and content using regex", () => {
      const input = `---
title: Test Document
description: This is a test
author: Test Author
---

# Test Document

This is the content.`;

      const result = parseFrontmatter(input);

      expect(result.frontmatter).toEqual({
        title: "Test Document",
        description: "This is a test",
        author: "Test Author",
      });
      expect(result.content.trim()).toBe(
        "# Test Document\n\nThis is the content.",
      );
    });

    test("handles frontmatter with quoted values", () => {
      const input = `---
title: "Test Document with Quotes"
description: 'Single quoted description'
---

Content here.`;

      const result = parseFrontmatter(input);

      expect(result.frontmatter.title).toBe("Test Document with Quotes");
      expect(result.frontmatter.description).toBe("Single quoted description");
    });

    test("handles content without frontmatter", () => {
      const input = `# Just Content
      
No frontmatter here.`;

      const result = parseFrontmatter(input);

      expect(result.frontmatter).toEqual({});
      expect(result.content).toBe(input);
    });

    test("handles empty frontmatter", () => {
      const input = `---
---

Content after empty frontmatter.`;

      const result = parseFrontmatter(input);

      expect(result.frontmatter).toEqual({});
      expect(result.content.trim()).toBe("Content after empty frontmatter.");
    });

    test("handles frontmatter with empty lines", () => {
      const input = `---
title: Document with Empty Lines

description: Has a blank line in frontmatter
---

Content here.`;

      const result = parseFrontmatter(input);

      expect(result.frontmatter.title).toBe("Document with Empty Lines");
      expect(result.frontmatter.description).toBe(
        "Has a blank line in frontmatter",
      );
    });

    test("handles documents containing triple dashes in content", () => {
      const input = `---
title: Document with Dashes
---

Content with --- dashes in the middle should be preserved.

---
This should be part of the content too.`;

      const result = parseFrontmatter(input);

      expect(result.frontmatter.title).toBe("Document with Dashes");
      expect(result.content).toContain("Content with --- dashes");
      expect(result.content).toContain(
        "This should be part of the content too.",
      );
    });

    test("handles malformed frontmatter gracefully", () => {
      const input = `---
This is not proper frontmatter
No colons here
---

Content after malformed frontmatter.`;

      const result = parseFrontmatter(input);

      expect(result.frontmatter).toEqual({});
      expect(result.content.trim()).toBe(
        "Content after malformed frontmatter.",
      );
    });
  });

  describe("mergeFrontmatter", () => {
    test("merges two frontmatter objects without overwriting", () => {
      const target = {
        title: "Original Title",
        description: "Original Description",
      };
      const source = { title: "New Title", author: "Test Author" };

      const result = mergeFrontmatter(target, source);

      expect(result.title).toBe("Original Title"); // Not overwritten
      expect(result.description).toBe("Original Description"); // Kept
      expect(result.author).toBe("Test Author"); // Added
    });

    test("merges with overwrite when specified", () => {
      const target = {
        title: "Original Title",
        description: "Original Description",
      };
      const source = { title: "New Title", author: "Test Author" };

      const result = mergeFrontmatter(target, source, true);

      expect(result.title).toBe("New Title"); // Overwritten
      expect(result.description).toBe("Original Description"); // Kept
      expect(result.author).toBe("Test Author"); // Added
    });

    test("handles empty source", () => {
      const target = { title: "Original Title" };
      const source = {};

      const result = mergeFrontmatter(target, source);

      expect(result).toEqual(target);
    });

    test("handles empty target", () => {
      const target = {};
      const source = { title: "New Title" };

      const result = mergeFrontmatter(target, source);

      expect(result).toEqual(source);
    });
  });
});
