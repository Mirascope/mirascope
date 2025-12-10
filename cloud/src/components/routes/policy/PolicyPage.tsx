import React from "react";
import { MDXRenderer, LoadingContent } from "@/src/components";
import { type PolicyContent } from "@/src/lib/content";

import { formatDate } from "@/src/lib/utils";

interface PolicyPageProps {
  content: PolicyContent;
  type?: "privacy" | "terms-use" | "terms-service";
}

/**
 * PolicyPage - Reusable component for rendering policy and terms pages
 */
const PolicyPage: React.FC<PolicyPageProps> = ({
  content,
  type = "privacy",
}) => {
  // Content ID for the article element
  const contentId = "policy-content";

  // Default title based on type
  const defaultTitle = {
    privacy: "PRIVACY POLICY",
    "terms-use": "TERMS OF USE",
    "terms-service": "TERMS OF SERVICE",
  }[type];

  const title = content?.meta?.title ?? defaultTitle;
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
          <MDXRenderer
            code={content.mdx.code}
            frontmatter={content.mdx.frontmatter}
          />
        </article>
      </div>
    </div>
  );
};

/**
 * PolicyPageError - Error state for policy pages
 */
export const PolicyPageError: React.FC<{
  type: "privacy" | "terms-use" | "terms-service";
  error: string;
}> = ({ type, error }) => {
  const defaultTitle = {
    privacy: "PRIVACY POLICY",
    "terms-use": "TERMS OF USE",
    "terms-service": "TERMS OF SERVICE",
  }[type];

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8 text-center">
        <h1 className="text-3xl font-bold uppercase">{defaultTitle}</h1>
      </div>
      <p>This content is currently unavailable. Please check back later.</p>
      {error && <p className="text-destructive mt-2">Error: {error}</p>}
    </div>
  );
};

/**
 * PolicyPageLoading - Loading state for policy pages
 */
export const PolicyPageLoading: React.FC<{
  type: "privacy" | "terms-use" | "terms-service";
}> = ({ type }) => {
  const defaultTitle = {
    privacy: "PRIVACY POLICY",
    "terms-use": "TERMS OF USE",
    "terms-service": "TERMS OF SERVICE",
  }[type];

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8 text-center">
        <h1 className="text-3xl font-bold uppercase">{defaultTitle}</h1>
      </div>
      <LoadingContent spinnerClassName="h-12 w-12" fullHeight={false} />
    </div>
  );
};

export default PolicyPage;
