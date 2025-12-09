import React from "react";
import ErrorContent from "./ErrorContent";
import { PageMeta } from "@/src/components/core/meta";
import { DocumentNotFoundError, ContentError, type ContentType } from "@/src/lib/content/content";

interface ContentErrorHandlerProps {
  error: Error;
  contentType: ContentType;
}

const ContentErrorHandler: React.FC<ContentErrorHandlerProps> = ({ error, contentType }) => {
  // Check if it's a DocumentNotFoundError (404)
  const isNotFound = error instanceof DocumentNotFoundError;
  // Check if it's any type of ContentError
  const isContentError = error instanceof ContentError;

  // Configure content-specific settings
  const contentTypeConfig = {
    blog: {
      title: isNotFound ? "Post Not Found" : "Error Loading Post",
      notFoundMessage: "The blog post you're looking for doesn't exist or has been moved.",
      backTo: "/blog",
      backLabel: "Back to Blog",
    },
    docs: {
      title: isNotFound ? "Page Not Found" : "Error Loading Page",
      notFoundMessage: "The documentation page you're looking for doesn't exist or has been moved.",
      backTo: "/docs",
      backLabel: "Back to Documentation",
    },
    policy: {
      title: isNotFound ? "Page Not Found" : "Error Loading Page",
      notFoundMessage: "The policy page you're looking for doesn't exist or has been moved.",
      backTo: "/",
      backLabel: "Back to Home",
    },
    dev: {
      title: isNotFound ? "Page Not Found" : "Error Loading Page",
      notFoundMessage: "The development page you're looking for doesn't exist or has been moved.",
      backTo: "/dev",
      backLabel: "Back to Dev Tools",
    },
    "llm-docs": {
      title: isNotFound ? "LLM Document Not Found" : "Error Loading LLM Document",
      notFoundMessage: "The LLM document you're looking for doesn't exist or has been moved.",
      backTo: "/docs",
      backLabel: "Back to Documentation",
    },
  };

  const config = contentTypeConfig[contentType];

  // Create a user-friendly message based on error type
  const message = isNotFound
    ? config.notFoundMessage
    : isContentError
      ? `Error loading content: ${error.message}`
      : "An unexpected error occurred while loading this page.";

  return (
    <div className="relative">
      {/* SEO metadata */}
      <PageMeta
        title={isNotFound ? `404 - ${config.title}` : config.title}
        description={message}
        robots="noindex, nofollow"
      />

      <ErrorContent
        title={config.title}
        message={message}
        showBackButton={true}
        backTo={config.backTo}
        backLabel={config.backLabel}
      />
    </div>
  );
};

export default ContentErrorHandler;
