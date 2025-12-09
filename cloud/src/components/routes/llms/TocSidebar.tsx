import { TableOfContents, type TOCItem } from "@/src/components";
import { LLMContent } from "@/src/lib/content/llm-content";
import { formatTokenCount, tokenBadge } from "./utils";

interface TocSidebarProps {
  content: LLMContent;
}

export default function TocSidebar({ content }: TocSidebarProps) {
  // Convert to hierarchical TOC items
  const tocItems: TOCItem[] = [];

  // Process content items
  for (const item of content.getChildren()) {
    tocItems.push({
      id: `section-${item.slug}`,
      content: (
        <div className="flex items-center gap-2">
          <div className="flex w-10 justify-end">
            <span className={tokenBadge}>{formatTokenCount(item.tokenCount)}</span>
          </div>
          <span className="font-medium">{item.title}</span>
        </div>
      ),
      level: 1,
    });

    // Add child items if this is a container
    for (const child of item.getChildren()) {
      tocItems.push({
        id: `subsection-${child.slug}`,
        content: (
          <div className="flex items-center gap-2">
            <div className="flex w-10 justify-end">
              <span className={tokenBadge}>{formatTokenCount(child.tokenCount)}</span>
            </div>
            <span>{child.title}</span>
          </div>
        ),
        level: 2,
      });
    }
  }

  return (
    <div className="py-6">
      <h3 className="mb-4 text-sm font-semibold">
        <button
          onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
          className="text-muted-foreground hover:text-foreground font-inherit cursor-pointer border-none bg-transparent p-0 transition-colors"
        >
          Table of Contents
        </button>
      </h3>
      <TableOfContents headings={tocItems} observeHeadings />
    </div>
  );
}
