import { visit } from "unist-util-visit";
import type { Element, Root } from "hast";

/**
 * Type definition for a hast element with data property
 */
interface ElementWithData extends Element {
  data?: {
    meta?: string;
    [key: string]: unknown;
  };
}

/**
 * Rehype plugin to preserve code block meta information
 * by adding it as a data attribute to the pre element
 */
export function rehypeCodeMeta() {
  return (tree: Root) => {
    visit(tree, "element", (node: Element) => {
      // Check for pre > code structure
      if (node.tagName === "pre") {
        const codeNode = node.children.find(
          (child): child is ElementWithData =>
            (child as Element).type === "element" &&
            (child as Element).tagName === "code",
        );

        if (codeNode?.data?.meta) {
          // Ensure properties object exists
          node.properties = node.properties || {};

          // Use standard HTML data-* attribute format which is more likely to be preserved
          node.properties["data-meta"] = codeNode.data.meta;
        }
      }
    });
  };
}
