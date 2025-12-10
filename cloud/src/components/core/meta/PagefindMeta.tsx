import { type ReactNode } from "react";

interface PagefindMetaProps {
  title: string;
  description: string;
  children: ReactNode;
  section?: string;
}

/**
 * PagefindMeta wraps content and adds metadata for Pagefind indexing.
 *
 * Uses the syntax: <meta data-pagefind-meta="key:value" />
 * All metadata is placed inside the data-pagefind-body div, which makes it
 * easier to add more metadata properties in the future.
 */
export function PagefindMeta({ children }: PagefindMetaProps) {
  return (
    <div data-pagefind-body>
      <div>{children}</div>
    </div>
  );
}

export default PagefindMeta;
