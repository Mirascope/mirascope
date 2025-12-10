import React from "react";
import { Link, useNavigate } from "@tanstack/react-router";
import { Link as LinkIcon } from "lucide-react";
import {
  InstallSnippet,
  ProviderCodeBlock,
  Callout,
  Note,
  Warning,
  Info,
  Success,
  TabbedSection,
  Tab,
  MermaidDiagram,
  Icon,
} from "@/src/components/mdx/elements";
import {
  ApiType,
  ApiSignature,
  ParametersTable,
  ReturnTable,
  AttributesTable,
  TypeLink,
} from "@/src/components/docs/api";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/mirascope-ui/ui/tabs";
import { Button } from "@/mirascope-ui/ui/button";
import { ButtonLink } from "@/mirascope-ui/ui/button-link";
import { ProductLogo, MirascopeLogo, LilypadLogo } from "@/src/components/core/branding";
import { ProviderCodeWrapper } from "./ProviderCodeWrapper";
import { ResponsiveImage } from "@/src/components/mdx/providers/ResponsiveImage";
import { devComponents } from "@/src/components/mdx/elements/DevComponents";
import { idSlugFromChildren } from "@/src/lib/mdx/heading-utils";

// -----------------------------------------------------------------------------
// Helper Components
// -----------------------------------------------------------------------------

// MDX-specific ButtonLink wrapper that bypasses type checking at the MDX boundary
// and handles nested paragraph tags that MDX generates
const MDXButtonLink = (props: React.ComponentProps<typeof ButtonLink>) => {
  // Extract children from paragraph tags that MDX might add
  return (
    <ButtonLink {...props}>
      {React.Children.map(props.children, (child) => {
        // If it's a paragraph element, extract its children
        if (
          React.isValidElement(child) &&
          (child.type === "p" || (typeof child.type === "function" && child.type.name === "p"))
        ) {
          // Type assertion to access props safely
          const elementProps = (child as React.ReactElement<{ children?: React.ReactNode }>).props;
          return elementProps.children;
        }
        return child;
      })}
    </ButtonLink>
  );
};

// Heading anchor link component
const HeadingAnchor = ({ id }: { id?: string }) => {
  const navigate = useNavigate();

  if (!id) return null;

  const handleClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
    // Prevent default browser behavior
    e.preventDefault();

    // Use TanStack Router's navigate to update the hash
    // This leverages the router's built-in scroll restoration
    navigate({
      hash: id,
      // Use replace to avoid adding to history stack
      replace: true,
    });
  };

  return (
    <a
      href={`#${id}`}
      onClick={handleClick}
      aria-label="Link to this heading"
      className="heading-anchor text-muted-foreground hover:text-primary ml-2 opacity-0 transition-opacity group-hover:opacity-100"
    >
      <LinkIcon size={16} />
    </a>
  );
};

// -----------------------------------------------------------------------------
// Custom Components & UI Elements
// -----------------------------------------------------------------------------

const customComponents = {
  // Custom components for docs
  InstallSnippet,
  ProviderCodeBlock,
  TabbedSection,
  Tab,
  Callout,
  Note,
  Warning,
  Info,
  Success,
  MermaidDiagram,
  Icon,

  // API documentation components
  ApiType,
  ApiSignature,
  AttributesTable,
  ParametersTable,
  ReturnTable,
  TypeLink,

  // UI Components
  Button,
  ButtonLink: MDXButtonLink, // Use the MDX-specific wrapper for ButtonLink
  Tabs,
  TabsList,
  TabsTrigger,
  TabsContent,
  ProductLogo,
  MirascopeLogo,
  LilypadLogo,

  // Dev components
  ...devComponents,
};

// -----------------------------------------------------------------------------
// HTML Elements
// -----------------------------------------------------------------------------

const headingElements = {
  h1: ({ children, ...props }: React.ComponentPropsWithoutRef<"h1">) => {
    // Generate an ID from the text content if not provided
    const id = props.id || idSlugFromChildren(children);
    return (
      <h1
        id={id}
        className="group my-6 flex scroll-mt-[120px] items-center text-3xl font-bold first:mt-0"
        {...props}
      >
        {children}
        <HeadingAnchor id={id} />
      </h1>
    );
  },
  h2: ({ children, ...props }: React.ComponentPropsWithoutRef<"h2">) => {
    const id = props.id || idSlugFromChildren(children);
    return (
      <h2
        id={id}
        className="group my-5 flex scroll-mt-[120px] items-center text-2xl font-semibold"
        {...props}
      >
        {children}
        <HeadingAnchor id={id} />
      </h2>
    );
  },
  h3: ({ children, ...props }: React.ComponentPropsWithoutRef<"h3">) => {
    const id = props.id || idSlugFromChildren(children);
    return (
      <h3
        id={id}
        className="group my-4 flex scroll-mt-[120px] items-center text-xl font-medium"
        {...props}
      >
        {children}
        <HeadingAnchor id={id} />
      </h3>
    );
  },
  h4: ({ children, ...props }: React.ComponentPropsWithoutRef<"h4">) => {
    const id = props.id || idSlugFromChildren(children);
    return (
      <h4
        id={id}
        className="group my-3 flex scroll-mt-[120px] items-center text-lg font-medium"
        {...props}
      >
        {children}
        <HeadingAnchor id={id} />
      </h4>
    );
  },
  h5: ({ children, ...props }: React.ComponentPropsWithoutRef<"h5">) => {
    const id = props.id || idSlugFromChildren(children);
    return (
      <h5
        id={id}
        className="group my-3 flex scroll-mt-[120px] items-center text-base font-medium"
        {...props}
      >
        {children}
        <HeadingAnchor id={id} />
      </h5>
    );
  },
};

const textElements = {
  p: (props: React.ComponentPropsWithoutRef<"p">) => <p className="my-3 text-base" {...props} />,
  strong: (props: React.ComponentPropsWithoutRef<"strong">) => <strong {...props} />,
  em: (props: React.ComponentPropsWithoutRef<"em">) => <em {...props} />,
  blockquote: (props: React.ComponentPropsWithoutRef<"blockquote">) => (
    <blockquote className="border-border my-4 border-l-4 pl-4 italic" {...props} />
  ),
  hr: (props: React.ComponentPropsWithoutRef<"hr">) => (
    <hr className="border-border my-6" {...props} />
  ),
};

const listElements = {
  ul: (props: React.ComponentPropsWithoutRef<"ul">) => (
    <ul className="my-4 list-disc pl-5" {...props} />
  ),
  ol: (props: React.ComponentPropsWithoutRef<"ol">) => (
    <ol className="my-4 list-decimal pl-5" {...props} />
  ),
  li: (props: React.ComponentPropsWithoutRef<"li">) => <li className="mb-2" {...props} />,
};

const tableElements = {
  table: (props: React.ComponentPropsWithoutRef<"table">) => (
    <div className="table-container">
      <table className="divide-border my-6 min-w-full divide-y" {...props} />
    </div>
  ),
  th: (props: React.ComponentPropsWithoutRef<"th">) => (
    <th
      className="bg-card text-card-foreground px-4 py-2 text-left text-sm font-medium"
      {...props}
    />
  ),
  td: (props: React.ComponentPropsWithoutRef<"td">) => (
    <td className="border-border border-t px-4 py-2" {...props} />
  ),
};

const mediaElements = {
  // Responsive image component
  img: (props: React.ComponentPropsWithoutRef<"img">) => <ResponsiveImage {...props} />,
  a: (props: React.ComponentPropsWithoutRef<"a">) => {
    const { href, ...rest } = props;
    const navigate = useNavigate();

    // Handle hash-only links (same page)
    if (href?.startsWith("#")) {
      const handleClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
        e.preventDefault();
        navigate({
          hash: href.substring(1), // Remove the # prefix
          replace: true,
        });
      };

      return (
        <a
          href={href}
          onClick={handleClick}
          className="text-primary text-base no-underline hover:underline"
          {...rest}
        />
      );
    }

    // Handle cross-page hash links (path + hash)
    if (
      href?.includes("#") &&
      (href.startsWith("/") ||
        (!href.startsWith("http") &&
          !href.startsWith("https") &&
          !href.startsWith("mailto:") &&
          !href.startsWith("tel:")))
    ) {
      const [path, hash] = href.split("#");
      return (
        <Link
          to={path}
          hash={hash}
          className="text-primary text-base no-underline hover:underline"
          {...rest}
        />
      );
    }

    // Handle regular internal links
    if (
      href &&
      (href.startsWith("/") ||
        (!href.startsWith("http") &&
          !href.startsWith("https") &&
          !href.startsWith("mailto:") &&
          !href.startsWith("tel:")))
    ) {
      return (
        <Link to={href} className="text-primary text-base no-underline hover:underline" {...rest} />
      );
    }

    // Use regular <a> for external links
    return <a className="text-primary text-base no-underline hover:underline" {...props} />;
  },
};

const codeElements = {
  // Inline code - this is only for inline elements, not code blocks
  code: (props: React.ComponentPropsWithoutRef<"code">) => {
    // Don't apply inline code styling to code blocks (which are children of pre tags)
    const isInPre = React.useRef<boolean>(false);
    React.useLayoutEffect(() => {
      // Type assertion for DOM properties access
      const element = props as unknown as { parentElement?: { tagName: string } };
      const parentIsPre =
        props.className?.includes("language-") ||
        props.className?.includes("shiki") ||
        element.parentElement?.tagName === "PRE";
      isInPre.current = !!parentIsPre;
    }, [props]);

    // Only apply inline code styling to actual inline code, not code blocks
    if (isInPre.current) {
      return <code {...props} />;
    }

    return (
      <code
        className="bg-muted text-muted-foreground rounded px-1 py-0.5 font-mono text-[0.9em]"
        {...props}
      />
    );
  },

  // Code blocks - use our custom CodeBlock component with provider substitution
  pre: (props: React.ComponentPropsWithoutRef<"pre">) => {
    // Get meta information from our data attribute or initialize to empty
    let meta = (props as any)["data-meta"] || "";

    // Initialize variables for code content and language
    let codeContent = "";
    let language = "txt";

    // Process children to find code content and language
    if (props.children) {
      const children = React.Children.toArray(props.children);

      // Loop through children to find code content (typically there's only one child)
      for (const child of children) {
        if (!React.isValidElement(child)) continue;

        // Check if this is a code element or has code-like properties
        const childProps = child.props as {
          className?: string;
          children?: React.ReactNode | string;
        };

        // Extract language from className
        if (childProps.className?.includes("language-")) {
          language = (childProps.className.match(/language-(\w+)/) || [])[1] || "txt";

          // Also check for meta in className (legacy approach)
          // This looks for patterns like {1-3} or {1,3} after the language
          if (!meta) {
            const metaMatch = childProps.className.match(/\{([^}]+)\}/);
            meta = metaMatch ? `{${metaMatch[1]}}` : "";
          }
        }

        // Get code content
        if (typeof childProps.children === "string") {
          codeContent = childProps.children;
          break;
        }
      }
    }

    // Handle mermaid diagrams
    if (language === "mermaid" && codeContent) {
      return <MermaidDiagram chart={codeContent.trim()} />;
    }

    return (
      <ProviderCodeWrapper code={codeContent.replace(/\n$/, "")} language={language} meta={meta} />
    );
  },
};

// -----------------------------------------------------------------------------
// Complete Component Registry
// -----------------------------------------------------------------------------

export const components = {
  ...customComponents,
  ...headingElements,
  ...textElements,
  ...listElements,
  ...tableElements,
  ...mediaElements,
  ...codeElements,
};
