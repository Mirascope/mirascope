/**
 * Parse frontmatter from MDX content
 */
export function parseFrontmatter(content: string): {
  frontmatter: Record<string, string>;
  content: string;
} {
  if (!content.startsWith("---")) {
    return { frontmatter: {}, content };
  }

  const parts = content.split("---");

  if (parts.length >= 3 && parts[1].trim() === "") {
    return {
      frontmatter: {},
      content: parts.slice(2).join("---").trimStart(),
    };
  }

  if (parts.length >= 3) {
    const frontmatterStr = parts[1].trim();
    const contentParts = parts.slice(2).join("---");
    const cleanContent = contentParts.trimStart();

    const frontmatter: Record<string, string> = {};

    frontmatterStr.split("\n").forEach((line) => {
      const trimmedLine = line.trim();
      if (!trimmedLine) return;

      const colonIndex = trimmedLine.indexOf(":");
      if (colonIndex > 0) {
        const key = trimmedLine.slice(0, colonIndex).trim();
        const value = trimmedLine.slice(colonIndex + 1).trim();
        frontmatter[key] = value.replace(/^["'](.*)["']$/, "$1");
      }
    });

    return { frontmatter, content: cleanContent };
  }

  return { frontmatter: {}, content };
}
