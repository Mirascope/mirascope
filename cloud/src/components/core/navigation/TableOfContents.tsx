import React, { useState, useEffect, type ReactNode } from "react";
import { cn } from "@/src/lib/utils";

export type TOCItem = {
  id: string;
  content: string | ReactNode;
  level: number;
};

export interface TableOfContentsProps {
  headings: TOCItem[];
  activeId?: string;

  /**
   * Enable automatic tracking of the active heading by observing heading elements in the DOM.
   * When true, the component will use an IntersectionObserver to track which headings
   * are currently visible and update the active heading accordingly.
   * This overrides the activeId prop.
   */
  observeHeadings?: boolean;

  /**
   * Options for the IntersectionObserver when observeHeadings is true.
   */
  observerOptions?: IntersectionObserverInit;
}

/**
 * A table of contents component that renders a list of headings.
 * Takes explicit props instead of extracting content from the DOM.
 * Can optionally track which heading is currently active by observing heading elements.
 */
export const TableOfContents: React.FC<TableOfContentsProps> = ({
  headings,
  activeId: initialActiveId = "",
  observeHeadings = false,
  observerOptions = {
    rootMargin: "-100px 0px -70% 0px",
    threshold: 0,
  },
}) => {
  const [internalActiveId, setInternalActiveId] =
    useState<string>(initialActiveId);

  // The active ID is either controlled externally or tracked internally
  const activeId = observeHeadings ? internalActiveId : initialActiveId;

  // Set up heading observation if enabled
  useEffect(() => {
    if (!observeHeadings || headings.length === 0) return;

    // Set up intersection observer for tracking active heading
    const headingObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          setInternalActiveId(entry.target.id);
        }
      });
    }, observerOptions);

    // Observe all heading elements
    const elements = headings
      .map((heading) => document.getElementById(heading.id))
      .filter(Boolean) as HTMLElement[];

    elements.forEach((el) => headingObserver.observe(el));

    return () => {
      headingObserver.disconnect();
    };
  }, [headings, observeHeadings, observerOptions]);

  if (headings.length === 0) {
    return (
      <p className="text-muted-foreground pl-5 text-sm italic">
        No headings found
      </p>
    );
  }

  return (
    <div className="max-h-[calc(100vh-18rem)] overflow-y-auto">
      <div className="pl-4">
        <nav className="space-y-1">
          {headings.map((heading) => (
            <button
              key={heading.id}
              onClick={(e) => {
                e.preventDefault();
                const element = document.getElementById(heading.id);
                if (element) {
                  element.scrollIntoView({ behavior: "smooth" });
                }
              }}
              className={cn(
                "font-inherit -ml-[1px] block w-full cursor-pointer truncate border-l-2 border-none bg-transparent py-1 text-left text-[13px] transition-colors",
                heading.level === 1 && "pl-0",
                heading.level === 2 && "pl-2",
                heading.level === 3 && "pl-4",
                heading.level === 4 && "pl-6",
                heading.level === 5 && "pl-8",
                heading.level === 6 && "pl-10",
                activeId === heading.id
                  ? "border-primary text-primary font-medium"
                  : "text-muted-foreground hover:bg-muted border-transparent hover:rounded-md",
              )}
            >
              {heading.content}
            </button>
          ))}
        </nav>
      </div>
    </div>
  );
};
