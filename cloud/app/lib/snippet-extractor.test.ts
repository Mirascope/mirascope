import { describe, test, expect } from "vitest";
import { extractSnippetsFromContent } from "./snippet-extractor";

describe("extractSnippetsFromContent", () => {
  test("extracts simple python code blocks", () => {
    const mdxContent = `
# Test Markdown

Here's a simple Python example:

\`\`\`python
def hello_world():
    print("Hello, world!")
\`\`\`
`;

    const snippets = extractSnippetsFromContent(mdxContent);
    expect(snippets.length).toBe(1);
    expect(snippets[0]).toBe('def hello_world():\n    print("Hello, world!")');
  });

  test("extracts multiple python code blocks", () => {
    const mdxContent = `
# Test Markdown

First Python example:

\`\`\`python
def hello():
    print("Hello")
\`\`\`

Second Python example:

\`\`\`python
def world():
    print("World")
\`\`\`
`;

    const snippets = extractSnippetsFromContent(mdxContent);
    expect(snippets.length).toBe(2);
    expect(snippets[0]).toBe('def hello():\n    print("Hello")');
    expect(snippets[1]).toBe('def world():\n    print("World")');
  });

  test("handles python-snippet-concat blocks", () => {
    const mdxContent = `
# Test Markdown

First part:

\`\`\`python
def hello():
    print("Hello")
\`\`\`

Second part (to be concatenated):

\`\`\`python-snippet-concat
def world():
    print("World")
\`\`\`
`;

    const snippets = extractSnippetsFromContent(mdxContent);
    expect(snippets.length).toBe(1);
    expect(snippets[0]).toBe(
      'def hello():\n    print("Hello")\n\ndef world():\n    print("World")',
    );
  });

  test("handles first block being a python-snippet-concat", () => {
    const mdxContent = `
# Test Markdown

\`\`\`python-snippet-concat
def hello():
    pass
\`\`\`
`;

    const snippets = extractSnippetsFromContent(mdxContent);
    expect(snippets.length).toBe(1);
    expect(snippets[0]).toBe("def hello():\n    pass");
  });

  test("skips python-snippet-skip blocks", () => {
    const mdxContent = `
# Test Markdown

This should be included:

\`\`\`python
def hello():
    print("Hello")
\`\`\`

This should be skipped:

\`\`\`python-snippet-skip
def skipped():
    print("Skipped")
\`\`\`

This should be included:

\`\`\`python
def world():
    print("World")
\`\`\`
`;

    const snippets = extractSnippetsFromContent(mdxContent);
    expect(snippets.length).toBe(2);
    expect(snippets[0]).toBe('def hello():\n    print("Hello")');
    expect(snippets[1]).toBe('def world():\n    print("World")');
  });

  test("handles multiple concat blocks in sequence", () => {
    const mdxContent = `
# Test Markdown

Start:

\`\`\`python
def part1():
    print("Part 1")
\`\`\`

\`\`\`python-snippet-concat
def part2():
    print("Part 2")
\`\`\`

\`\`\`python-snippet-concat
def part3():
    print("Part 3")
\`\`\`
`;

    const snippets = extractSnippetsFromContent(mdxContent);
    expect(snippets.length).toBe(1);
    expect(snippets[0]).toBe(
      'def part1():\n    print("Part 1")\n\ndef part2():\n    print("Part 2")\n\ndef part3():\n    print("Part 3")',
    );
  });

  test("throws error for unsupported python block types", () => {
    const mdxContent = `
# Test Markdown

\`\`\`python-unsupported
def invalid():
    print("This shouldn't work")
\`\`\`
`;

    expect(() => extractSnippetsFromContent(mdxContent)).toThrow(
      'Unsupported Python block type "python-unsupported"',
    );
  });

  test("handles meta directives (no spaces)", () => {
    const mdxContent = `
# Test Markdown

Start:

\`\`\`python{1,2}
foo = 1
\`\`\`

\`\`\`python-snippet-concat{3}
bar = 2
\`\`\`

\`\`\`python-snippet-skip{4}
zod = 3
\`\`\`

\`\`\`python{1}
qux = 4
\`\`\`
`;

    const snippets = extractSnippetsFromContent(mdxContent);
    expect(snippets.length).toBe(2);
    expect(snippets[0]).toBe("foo = 1\n\nbar = 2");
    expect(snippets[1]).toBe("qux = 4");
  });

  test("handles meta directives (with spaces)", () => {
    const mdxContent = `
# Test Markdown

Start:

\`\`\`python {1,2}
foo = 1
\`\`\`

\`\`\`python-snippet-concat {3}
bar = 2
\`\`\`

\`\`\`python-snippet-skip {4}
zod = 3
\`\`\`

\`\`\`python {1}
qux = 4
\`\`\`
`;

    const snippets = extractSnippetsFromContent(mdxContent);
    expect(snippets.length).toBe(2);
    expect(snippets[0]).toBe("foo = 1\n\nbar = 2");
    expect(snippets[1]).toBe("qux = 4");
  });
});
