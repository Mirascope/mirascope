import { Link, useRouterState } from "@tanstack/react-router";

import type { SectionSpec } from "@/app/lib/content/spec";

import { docRegistry } from "@/app/lib/content/doc-registry";
import { cn } from "@/app/lib/utils";

/**
 * Check if a section is active based on the current path
 */
function isSectionActive(section: SectionSpec, currentPath: string): boolean {
  // For the welcome/index section (which maps to /docs root)
  if (section.slug === "index") {
    if (currentPath === "/docs" || currentPath === "/docs/") {
      return true;
    }
    // Check if the path is for a top-level item under this section
    const childSlugs = section.children.map((c) => c.slug);
    const pathAfterDocs = currentPath.replace(/^\/docs\/?/, "");
    const firstSegment = pathAfterDocs.split("/")[0];
    // Active if first segment is a child of this section (not another section)
    return childSlugs.includes(firstSegment) && firstSegment !== "";
  }

  // For other sections, match if path starts with section path
  const sectionPath = `/docs/${section.slug}`;
  return (
    currentPath === sectionPath || currentPath.startsWith(`${sectionPath}/`)
  );
}

/**
 * Get the link path for a section.
 * For sections with products (like Learn), link to the first product.
 */
function getSectionPath(section: SectionSpec): string {
  if (section.slug === "index") {
    return "/docs";
  }

  // If section has products, link to the first product
  if (section.products && section.products.length > 0) {
    return `/docs/${section.slug}/${section.products[0].slug}`;
  }

  return `/docs/${section.slug}`;
}

interface DocsSubNavbarProps {
  className?: string;
}

/**
 * Sub-navbar component for docs pages
 *
 * Shows all sections as tabs for easy navigation.
 */
export default function DocsSubNavbar({ className }: DocsSubNavbarProps) {
  const router = useRouterState();
  const currentPath = router.location.pathname;

  // Get the single version's sections
  const version = docRegistry.getFullSpec()[0];
  if (!version) return null;

  const sections = version.sections;

  return (
    <nav className={cn("flex w-full px-3 pt-3 pb-1 md:px-6", className)}>
      {/* Spacer to match logo width - logo is ~140px with text */}
      <div className="hidden w-[140px] shrink-0 lg:block" />

      {/* Links with same ml-6 as desktop nav - scrollable on mobile */}
      <div className="hide-scrollbar flex space-x-6 overflow-x-auto lg:ml-2">
        {sections.map((section) => {
          const isActive = isSectionActive(section, currentPath);
          const sectionPath = getSectionPath(section);

          return (
            <Link
              key={section.slug}
              to={sectionPath}
              className={cn(
                "shrink-0 whitespace-nowrap text-lg font-medium transition-colors",
                isActive
                  ? "text-primary"
                  : "text-muted-foreground hover:text-foreground",
              )}
            >
              {section.label}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
