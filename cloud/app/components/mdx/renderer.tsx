/**
 * MDX Renderer
 *
 * Component that renders compiled MDX content using runtime evaluation.
 * Uses runSync from @mdx-js/mdx to evaluate the compiled JSX code string.
 */

import React, { useMemo } from "react";
import { runSync } from "@mdx-js/mdx";
import * as jsxRuntime from "react/jsx-runtime";
import type { CompiledMDX } from "@/app/lib/mdx/types";
import type { MDXComponents } from "mdx/types";
import componentRegistry from "@/app/components/mdx/component-registry";

interface MDXRendererProps {
  /** Compiled MDX content with code string */
  mdx: CompiledMDX;
  /** Optional custom components to override defaults */
  components?: MDXComponents;
  /** Optional className for the wrapper div */
  className?: string;
}

/**
 * Default components for MDX rendering
 * These will be used unless overridden via components prop
 */
const defaultComponents = {
  h1: (props: React.HTMLAttributes<HTMLHeadingElement>) => (
    <h1 className="mb-4 mt-8 text-4xl font-bold" {...props} />
  ),
  h2: (props: React.HTMLAttributes<HTMLHeadingElement>) => (
    <h2 className="mb-3 mt-6 text-3xl font-bold" {...props} />
  ),
  h3: (props: React.HTMLAttributes<HTMLHeadingElement>) => (
    <h3 className="mb-2 mt-4 text-2xl font-semibold" {...props} />
  ),
  h4: (props: React.HTMLAttributes<HTMLHeadingElement>) => (
    <h4 className="mb-2 mt-3 text-xl font-semibold" {...props} />
  ),
  h5: (props: React.HTMLAttributes<HTMLHeadingElement>) => (
    <h5 className="mb-1 mt-2 text-lg font-semibold" {...props} />
  ),
  h6: (props: React.HTMLAttributes<HTMLHeadingElement>) => (
    <h6 className="mb-1 mt-2 text-base font-semibold" {...props} />
  ),
  p: (props: React.HTMLAttributes<HTMLParagraphElement>) => (
    <p className="mb-4 leading-7" {...props} />
  ),
  a: (props: React.AnchorHTMLAttributes<HTMLAnchorElement>) => (
    <a className="text-blue-600 underline hover:text-blue-800" {...props} />
  ),
  ul: (props: React.HTMLAttributes<HTMLUListElement>) => (
    <ul className="mb-4 ml-6 list-disc space-y-2" {...props} />
  ),
  ol: (props: React.HTMLAttributes<HTMLOListElement>) => (
    <ol className="mb-4 ml-6 list-decimal space-y-2" {...props} />
  ),
  li: (props: React.HTMLAttributes<HTMLLIElement>) => (
    <li className="leading-7" {...props} />
  ),
  code: (props: React.HTMLAttributes<HTMLElement>) => {
    const { className, children, ...rest } = props;
    // Inline code (not in a pre block)
    if (!className) {
      return (
        <code
          className="rounded bg-gray-100 px-1.5 py-0.5 font-mono text-sm"
          {...rest}
        >
          {children}
        </code>
      );
    }
    // Block code (inside pre)
    return (
      <code className={className} {...rest}>
        {children}
      </code>
    );
  },
  pre: (props: React.HTMLAttributes<HTMLPreElement>) => (
    <pre
      className="mb-4 overflow-x-auto rounded-lg bg-gray-900 p-4"
      {...props}
    />
  ),
  blockquote: (props: React.HTMLAttributes<HTMLQuoteElement>) => (
    <blockquote
      className="mb-4 border-l-4 border-gray-300 pl-4 italic text-gray-700"
      {...props}
    />
  ),
  table: (props: React.HTMLAttributes<HTMLTableElement>) => (
    <div className="mb-4 overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200" {...props} />
    </div>
  ),
  thead: (props: React.HTMLAttributes<HTMLTableSectionElement>) => (
    <thead className="bg-gray-50" {...props} />
  ),
  tbody: (props: React.HTMLAttributes<HTMLTableSectionElement>) => (
    <tbody className="divide-y divide-gray-200 bg-white" {...props} />
  ),
  tr: (props: React.HTMLAttributes<HTMLTableRowElement>) => <tr {...props} />,
  th: (props: React.ThHTMLAttributes<HTMLTableCellElement>) => (
    <th
      className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500"
      {...props}
    />
  ),
  td: (props: React.TdHTMLAttributes<HTMLTableCellElement>) => (
    <td
      className="whitespace-nowrap px-6 py-4 text-sm text-gray-900"
      {...props}
    />
  ),
  strong: (props: React.HTMLAttributes<HTMLElement>) => (
    <strong className="font-bold" {...props} />
  ),
  em: (props: React.HTMLAttributes<HTMLElement>) => (
    <em className="italic" {...props} />
  ),
};

/**
 * Renders compiled MDX content by evaluating the JSX code string at runtime
 */
export function MDXRenderer({ mdx, components, className }: MDXRendererProps) {
  // Evaluate compiled code to get React component
  // useMemo ensures we only re-evaluate when the code changes
  const MDXContent = useMemo(() => {
    const { default: Component } = runSync(mdx.code, {
      ...jsxRuntime,
      baseUrl: import.meta.url,
    });
    return Component as React.ComponentType<{ components?: MDXComponents }>;
  }, [mdx.code]);

  // Merge component registries: defaults < registry < props
  const mergedComponents = useMemo(
    () => ({
      ...defaultComponents,
      ...componentRegistry,
      ...components,
    }),
    [components],
  );

  return (
    <div className={className || "prose max-w-none"} id="mdx-container">
      <MDXContent components={mergedComponents} />
    </div>
  );
}
