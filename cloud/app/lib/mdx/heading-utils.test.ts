import React from "react";
import { describe, it, expect } from "vitest";

import {
  extractHeadings,
  extractHeadingText,
  generateHeadingId,
  extractTextFromReactChildren,
  idSlugFromChildren,
} from "./heading-utils";

describe("extractHeadingText", () => {
  it("returns original text when no ApiType is present", () => {
    const text = "Normal heading";
    expect(extractHeadingText(text)).toBe(text);
  });

  it("replaces ApiType component with bracketed type value", () => {
    const text =
      '<ApiType type="Function" path="core/call" symbolName="call" /> callFunction';
    expect(extractHeadingText(text)).toBe("[Function] callFunction");
  });

  it("handles multiple ApiType components", () => {
    const text =
      '<ApiType type="Class" path="x" symbolName="x" /> <ApiType type="Function" path="y" symbolName="y" />';
    // Note: Currently only handles the first match - this is a limitation
    expect(extractHeadingText(text)).toBe(
      '[Class] <ApiType type="Function" path="y" symbolName="y" />',
    );
  });
});

describe("generateHeadingId", () => {
  it("converts text to kebab-case slug", () => {
    expect(generateHeadingId("Hello World")).toBe("hello-world");
    expect(generateHeadingId("Function(param1, param2)")).toBe(
      "function-param1-param2",
    );
    expect(generateHeadingId("Multiple   spaces")).toBe("multiple-spaces");
  });

  it("strips ApiType components for ID generation", () => {
    const text =
      '<ApiType type="Function" path="x" symbolName="x" /> callFunction';
    expect(generateHeadingId(text)).toBe("callfunction");
  });
});

describe("extractHeadings", () => {
  it("extracts headings with levels", () => {
    const content = `
# Heading 1

Some content

## Heading 2

More content

### Heading 3
`;
    const headings = extractHeadings(content);
    expect(headings).toHaveLength(3);
    expect(headings[0]).toEqual({
      id: "heading-1",
      content: "Heading 1",
      level: 1,
    });
    expect(headings[1]).toEqual({
      id: "heading-2",
      content: "Heading 2",
      level: 2,
    });
    expect(headings[2]).toEqual({
      id: "heading-3",
      content: "Heading 3",
      level: 3,
    });
  });

  it("respects explicit heading IDs", () => {
    const content = `
# Heading 1 {#custom-id}

## Another Heading
`;
    const headings = extractHeadings(content);
    expect(headings).toHaveLength(2);
    expect(headings[0].id).toBe("custom-id");
    expect(headings[1].id).toBe("another-heading");
  });

  it("ignores headings in code blocks", () => {
    const content = `
# Real Heading

\`\`\`
# Fake Heading in Code Block
\`\`\`

## Another Real Heading
`;
    const headings = extractHeadings(content);
    expect(headings).toHaveLength(2);
    expect(headings[0].content).toBe("Real Heading");
    expect(headings[1].content).toBe("Another Real Heading");
  });

  it("ignores headings inside component tags", () => {
    const content = `
# Real Heading

<CustomComponent>
# This should be ignored
</CustomComponent>

## Another Real Heading
`;
    const headings = extractHeadings(content);
    expect(headings).toHaveLength(2);
    expect(headings[0].content).toBe("Real Heading");
    expect(headings[1].content).toBe("Another Real Heading");
  });

  it("handles heading with ApiType component", () => {
    const content = `
# Normal Heading

## <ApiType type="Function" path="core/call" symbolName="call" /> callFunction

### Another Heading
`;
    const headings = extractHeadings(content);
    expect(headings).toHaveLength(3);
    expect(headings[1].content).toBe("[Function] callFunction");
    expect(headings[1].id).toBe("callfunction");
  });

  it("handles complex nested components", () => {
    const content = `
# Top Heading

<Outer>
  <Inner>
    ## This heading should be ignored
  </Inner>
</Outer>

## <ApiType type="Class" path="x" symbolName="x" /> Bottom Heading
`;
    const headings = extractHeadings(content);
    expect(headings).toHaveLength(2);
    expect(headings[0].content).toBe("Top Heading");
    expect(headings[1].content).toBe("[Class] Bottom Heading");
  });
});

describe("extractTextFromReactChildren", () => {
  it("extracts text from string children", () => {
    expect(extractTextFromReactChildren("Simple text")).toBe("Simple text");
  });

  it("extracts text from array of children", () => {
    const children = ["Hello", " ", "World"];
    expect(extractTextFromReactChildren(children)).toBe("Hello World");
  });

  it("extracts text from React elements", () => {
    // Mock React elements
    const span = React.createElement("span", {}, "Text in span");
    expect(extractTextFromReactChildren(span)).toBe("Text in span");
  });

  it("handles nested React elements", () => {
    // Mock nested React elements
    const inner = React.createElement("em", {}, "emphasized");
    const outer = React.createElement("p", {}, [
      "Text with ",
      inner,
      " content",
    ]);
    expect(extractTextFromReactChildren(outer)).toBe(
      "Text with emphasized content",
    );
  });

  it("skips ApiType components", () => {
    // Mock ApiType component
    const ApiType = (props: { type: string }) =>
      React.createElement("span", props, props.type);
    ApiType.displayName = "ApiType";

    const apiTypeElement = React.createElement(ApiType, { type: "Function" });
    const children = ["Text with ", apiTypeElement, " component"];

    expect(extractTextFromReactChildren(children)).toBe("Text with  component");
  });
});

describe("idSlugFromChildren", () => {
  it("generates slugs from string children", () => {
    expect(idSlugFromChildren("Hello World")).toBe("hello-world");
  });

  it("generates slugs from React element children", () => {
    const span = React.createElement("span", {}, "Text in span");
    expect(idSlugFromChildren(span)).toBe("text-in-span");
  });

  it("generates slugs from mixed content", () => {
    // Mock component with mixed content
    const em = React.createElement("em", {}, "emphasized");
    const children = ["Text with ", em, " words"];

    expect(idSlugFromChildren(children)).toBe("text-with-emphasized-words");
  });

  it("skips ApiType components when generating slugs", () => {
    // Mock ApiType component
    const ApiType = (props: { type: string }) =>
      React.createElement("span", props, props.type);
    ApiType.displayName = "ApiType";

    const apiTypeElement = React.createElement(ApiType, { type: "Function" });
    const children = [apiTypeElement, " callFunction"];

    expect(idSlugFromChildren(children)).toBe("callfunction");
  });

  it("returns undefined for empty content", () => {
    expect(idSlugFromChildren("")).toBeUndefined();
    expect(idSlugFromChildren(null)).toBeUndefined();
    expect(idSlugFromChildren(undefined)).toBeUndefined();
  });
});
