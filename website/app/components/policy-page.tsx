import React from "react";

import { MDXRenderer } from "@/app/components/mdx/renderer";
import { type PolicyContent } from "@/app/lib/content/types";

/**
 * Format a date string to "Month Day, Year" format
 * The source date string (YYYY-MM-DD) represents a date in Los Angeles timezone
 */
const formatDate = (dateString: string): string => {
  if (!dateString) return "";
  try {
    // Validate ISO 8601 date format (YYYY-MM-DD)
    if (!/^\d{4}-\d{2}-\d{2}$/.test(dateString)) {
      return dateString;
    }
    // Parse date components
    const [year, month, day] = dateString.split("-").map(Number);

    // Create date at noon UTC to avoid DST edge cases, then format in LA timezone
    // This ensures the date is preserved correctly when formatting
    const date = new Date(Date.UTC(year, month - 1, day, 12, 0, 0));

    // Check if date is valid
    if (isNaN(date.getTime())) {
      return dateString;
    }

    // Format in Los Angeles timezone to match the source timezone
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
      timeZone: "America/Los_Angeles",
    });
  } catch (e) {
    console.error("Error formatting date:", e);
    return dateString;
  }
};

interface PolicyPageProps {
  content: PolicyContent;
}

/**
 * PolicyPage - Reusable component for rendering policy and terms pages
 */
const PolicyPage: React.FC<PolicyPageProps> = ({ content }) => {
  // Content ID for the article element
  const contentId = "policy-content";

  const title = content?.meta?.title ?? "Loading...";
  const lastUpdated = content?.meta?.lastUpdated
    ? formatDate(content.meta.lastUpdated)
    : "";

  return (
    <div className="container mx-auto max-w-4xl px-4 py-8">
      {/* Header with title and fun mode button aligned horizontally */}
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold uppercase">{title}</h1>
          {lastUpdated && (
            <p className="text-muted-foreground mt-1 font-medium">
              Last Updated: {lastUpdated}
            </p>
          )}
        </div>
      </div>

      <div
        id={contentId}
        className="bg-background border-border rounded-xl border p-4 shadow-sm sm:p-6"
      >
        <article className="prose prose-lg max-w-none">
          <MDXRenderer className="mdx-content" mdx={content.mdx} />
        </article>
      </div>
    </div>
  );
};

export default PolicyPage;
