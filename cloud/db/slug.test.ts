import { Schema } from "effect";
import { describe, it, expect } from "vitest";

import { generateSlug, isValidSlug, createSlugSchema } from "@/db/slug";

describe("generateSlug", () => {
  it("should convert a simple name to lowercase", () => {
    expect(generateSlug("Mirascope")).toBe("mirascope");
  });

  it("should replace spaces with hyphens", () => {
    expect(generateSlug("My Project Name")).toBe("my-project-name");
  });

  it("should handle company names with punctuation", () => {
    expect(generateSlug("Mirascope, Inc.")).toBe("mirascope-inc");
  });

  it("should remove consecutive hyphens", () => {
    expect(generateSlug("Test  --  Name")).toBe("test-name");
  });

  it("should remove leading and trailing hyphens", () => {
    expect(generateSlug("  -Test-  ")).toBe("test");
  });

  it("should preserve underscores", () => {
    expect(generateSlug("test_environment")).toBe("test_environment");
  });

  it("should handle mixed case", () => {
    expect(generateSlug("MyProjectName")).toBe("myprojectname");
  });

  it("should handle special characters", () => {
    expect(generateSlug("Project #1 (Beta)!")).toBe("project-1-beta");
  });

  it("should handle numbers", () => {
    expect(generateSlug("Project 123")).toBe("project-123");
  });

  it("should handle empty string", () => {
    expect(generateSlug("")).toBe("");
  });

  it("should handle only spaces", () => {
    expect(generateSlug("   ")).toBe("");
  });

  it("should handle only special characters", () => {
    expect(generateSlug("!!!")).toBe("");
  });
});

describe("isValidSlug", () => {
  it("should accept lowercase letters (minimum 3 chars)", () => {
    expect(isValidSlug("test")).toBe(true);
    expect(isValidSlug("abc")).toBe(true);
  });

  it("should accept numbers", () => {
    expect(isValidSlug("test123")).toBe(true);
    expect(isValidSlug("123")).toBe(true);
  });

  it("should accept hyphens in middle", () => {
    expect(isValidSlug("test-slug")).toBe(true);
  });

  it("should accept underscores in middle", () => {
    expect(isValidSlug("test_slug")).toBe(true);
  });

  it("should accept combination of valid characters", () => {
    expect(isValidSlug("my-project_123")).toBe(true);
    expect(isValidSlug("a-b-c")).toBe(true);
  });

  it("should reject uppercase letters", () => {
    expect(isValidSlug("Test")).toBe(false);
  });

  it("should reject spaces", () => {
    expect(isValidSlug("test slug")).toBe(false);
  });

  it("should reject special characters", () => {
    expect(isValidSlug("test!")).toBe(false);
  });

  it("should reject empty string", () => {
    expect(isValidSlug("")).toBe(false);
  });

  it("should reject punctuation", () => {
    expect(isValidSlug("test.slug")).toBe(false);
  });

  it("should reject slugs shorter than 3 characters", () => {
    expect(isValidSlug("ab")).toBe(false);
    expect(isValidSlug("a")).toBe(false);
  });

  it("should reject slugs starting with hyphen", () => {
    expect(isValidSlug("-abc")).toBe(false);
    expect(isValidSlug("-test-slug")).toBe(false);
  });

  it("should reject slugs ending with hyphen", () => {
    expect(isValidSlug("abc-")).toBe(false);
    expect(isValidSlug("test-slug-")).toBe(false);
  });

  it("should reject slugs starting with underscore", () => {
    expect(isValidSlug("_abc")).toBe(false);
    expect(isValidSlug("_test_slug")).toBe(false);
  });

  it("should reject slugs ending with underscore", () => {
    expect(isValidSlug("abc_")).toBe(false);
    expect(isValidSlug("test_slug_")).toBe(false);
  });

  it("should reject slugs with only hyphens", () => {
    expect(isValidSlug("---")).toBe(false);
  });

  it("should reject slugs with only underscores", () => {
    expect(isValidSlug("___")).toBe(false);
  });

  it("should reject slugs with only special characters in middle", () => {
    expect(isValidSlug("a-_-b")).toBe(true); // This is valid - starts/ends with alphanumeric
    expect(isValidSlug("_a_")).toBe(false); // Invalid - starts/ends with underscore
  });
});

describe("createSlugSchema", () => {
  it("accepts valid slug", () => {
    const TestSlugSchema = createSlugSchema("Test");
    const result = Schema.decodeUnknownSync(TestSlugSchema)("valid-slug");
    expect(result).toBe("valid-slug");
  });

  it("rejects slug shorter than 3 characters", () => {
    const TestSlugSchema = createSlugSchema("Test");
    expect(() => Schema.decodeUnknownSync(TestSlugSchema)("ab")).toThrow(
      "Test slug must be at least 3 characters",
    );
  });

  it("rejects slug longer than 100 characters", () => {
    const TestSlugSchema = createSlugSchema("Test");
    const longSlug = "a".repeat(101);
    expect(() => Schema.decodeUnknownSync(TestSlugSchema)(longSlug)).toThrow(
      "Test slug must be at most 100 characters",
    );
  });

  it("rejects slug with invalid pattern", () => {
    const TestSlugSchema = createSlugSchema("Test");
    expect(() =>
      Schema.decodeUnknownSync(TestSlugSchema)("Invalid-Slug"),
    ).toThrow(/must start and end with a letter or number/);
  });

  it("accepts slug of exactly 3 characters", () => {
    const TestSlugSchema = createSlugSchema("Test");
    const result = Schema.decodeUnknownSync(TestSlugSchema)("abc");
    expect(result).toBe("abc");
  });

  it("accepts slug of exactly 100 characters", () => {
    const TestSlugSchema = createSlugSchema("Test");
    const slug = "a".repeat(100);
    const result = Schema.decodeUnknownSync(TestSlugSchema)(slug);
    expect(result).toBe(slug);
  });
});
