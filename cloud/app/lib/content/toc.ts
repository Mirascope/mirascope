/**
 * Extract table of contents from MDX content
 */
export function extractTOC(content: string): Array<{
  id: string;
  text: string;
  level: number;
}> {
  const headingRegex = /^(#{1,6})\s+(.+)$/gm;
  const toc: Array<{ id: string; text: string; level: number }> = [];
  let match;

  while ((match = headingRegex.exec(content)) !== null) {
    const level = match[1].length;
    const text = match[2].trim();
    const id = text
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-|-$/g, "");

    toc.push({ id, text, level });
  }

  return toc;
}
