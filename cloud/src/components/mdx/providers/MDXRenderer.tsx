import { components } from "./mdxComponentRegistry";
import { MDXRemote } from "next-mdx-remote";
import { MDXProvider } from "@mdx-js/react";
import { LoadingContent } from "@/src/components/core/feedback";

interface MDXRendererProps {
  code: string;
  frontmatter: Record<string, any>;
}

// Define interface for what MDXRemote expects - must match MDXRemoteSerializeResult
interface MDXRemoteProps {
  compiledSource: string;
  scope: Record<string, any>;
  frontmatter: Record<string, any>; // Making this required as well
  components?: Record<string, React.ComponentType<any>>;
  [key: string]: any;
}

/**
 * MDXRenderer - Renders MDX content using @mdx-js/react
 */
export function MDXRenderer({ code, frontmatter }: MDXRendererProps) {
  // Handle case when no code is provided
  if (!code) {
    return <LoadingContent spinnerClassName="h-8 w-8" fullHeight={false} />;
  }

  // Use next-mdx-remote for rendering
  try {
    // Create a compatible MDXRemote input that satisfies the type requirements
    const mdxProps: MDXRemoteProps = {
      compiledSource: code,
      frontmatter: frontmatter,
      scope: frontmatter,
      components: components as any,
    };

    return (
      <div
        className="mdx-content prose max-w-none overflow-y-auto"
        id="mdx-container"
      >
        <MDXProvider components={components}>
          <MDXRemote {...mdxProps} />
        </MDXProvider>
      </div>
    );
  } catch (error) {
    console.error("Error rendering MDX with next-mdx-remote:", error);
    return (
      <div className="rounded-md border border-red-500 bg-red-50 p-4 text-red-800">
        <h3 className="mb-2 font-bold">Error rendering MDX</h3>
        <p>{error instanceof Error ? error.message : String(error)}</p>
      </div>
    );
  }
}
