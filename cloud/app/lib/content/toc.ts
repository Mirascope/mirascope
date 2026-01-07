import type { TOCItem } from "@/app/lib/content/types";

/**
 * Extract table of contents from MDX content
 */
export function extractTOC(content: string): Array<TOCItem> {
  const headingRegex = /^(#{1,6})\s+(.+)$/gm;

  return Array.from(content.matchAll(headingRegex)).map((match) => {
    const level = match[1].length;
    const content = match[2].trim();
    const id = content
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-|-$/g, "");

    return { id, content, level };
  });
}
