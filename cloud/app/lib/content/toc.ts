/**
 * Extract table of contents from MDX content
 */
export function extractTOC(content: string): Array<{
  id: string;
  text: string;
  level: number;
}> {
  const headingRegex = /^(#{1,6})\s+(.+)$/gm;

  return Array.from(content.matchAll(headingRegex)).map((match) => {
    const level = match[1].length;
    const text = match[2].trim();
    const id = text
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-|-$/g, "");

    return { id, text, level };
  });
}
