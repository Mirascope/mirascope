import React from "react";
import { Link, useRouterState } from "@tanstack/react-router";
import { cn } from "@/app/lib/utils";
import { ChevronDown, ChevronRight } from "lucide-react";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "@tanstack/react-router";

// Breakpoint definitions - matching Tailwind's defaults
export const BREAKPOINTS = {
  md: 768, // Medium breakpoint (tablet)
  sm: 640, // Small breakpoint
  lg: 1024, // Large breakpoint
};

// Shared media query strings
export const MEDIA_QUERIES = {
  mdAndUp: `(min-width: ${BREAKPOINTS.md}px)`,
  mdAndDown: `(max-width: ${BREAKPOINTS.md - 1}px)`,
};

// Helper functions for responsive checks
export const isMobileView = (): boolean => {
  return (
    typeof window !== "undefined" &&
    window.matchMedia(MEDIA_QUERIES.mdAndDown).matches
  );
};

export const isDesktopView = (): boolean => {
  return (
    typeof window !== "undefined" &&
    window.matchMedia(MEDIA_QUERIES.mdAndUp).matches
  );
};

export interface UseSidebarOptions {
  /**
   * Function to call when this sidebar opens (to close another one)
   */
  onOpen?: () => void;

  /**
   * Whether to close the sidebar when the route changes
   * @default true
   */
  closeOnRouteChange?: boolean;
}

/**
 * Simple hook for managing mobile sidebar state
 * Desktop visibility is handled purely with CSS
 */
export function useSidebar({
  onOpen,
  closeOnRouteChange = true,
}: UseSidebarOptions = {}) {
  // Only tracks the mobile state - desktop visibility is CSS-driven
  const [isOpen, setIsOpen] = useState(false);

  // Refs for focus management
  const closeBtnRef = useRef<HTMLButtonElement>(null);
  const previouslyFocusedElementRef = useRef<HTMLElement | null>(null);

  // Router for navigation tracking
  const router = useRouter();

  // Close on route change (mobile only)
  useEffect(() => {
    if (!closeOnRouteChange) return;

    const unsubscribe = router.subscribe("onResolved", () => {
      // Always close on navigation, but only on mobile
      if (isMobileView() && isOpen) {
        setIsOpen(false);
      }
    });

    return () => {
      unsubscribe();
    };
  }, [router, isOpen, closeOnRouteChange]);

  // Handle toggling with focus management
  const toggle = () => {
    // Save the currently focused element when opening
    if (!isOpen) {
      previouslyFocusedElementRef.current =
        document.activeElement as HTMLElement;

      // Notify when opening
      if (onOpen) {
        onOpen();
      }
    }

    const newState = !isOpen;
    setIsOpen(newState);

    // Manage focus
    if (newState) {
      // Focus the close button when sidebar opens
      setTimeout(() => {
        closeBtnRef.current?.focus();
      }, 100);
    } else {
      // Restore focus when sidebar closes
      setTimeout(() => {
        previouslyFocusedElementRef.current?.focus();
      }, 100);
    }
  };

  // Force open/close functions
  const open = () => {
    if (!isOpen) toggle();
  };

  const close = () => {
    if (isOpen) setIsOpen(false);
  };

  // Auto-close on ESC key (mobile only)
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape" && isOpen) {
        setIsOpen(false);
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen]);

  return {
    isOpen,
    setIsOpen,
    toggle,
    open,
    close,
    closeBtnRef,
    previouslyFocusedElementRef,
  };
}

/**
 * Generic section item data structure for sidebar navigation
 */
export interface SidebarItem {
  slug: string; // URL-friendly identifier
  label: string; // Display label for sidebar
  routePath?: string; // Optional explicit route path (overrides constructed path)
  items?: Record<string, SidebarItem>; // Nested items
  hasContent: boolean; // If true, this item has its own content page (not just a folder)
}

/**
 * Group of related sidebar items
 */
export interface SidebarGroup {
  slug: string; // URL-friendly identifier for path construction
  label: string; // Display label
  items: Record<string, SidebarItem>;
}

/**
 * Section of sidebar (like "API", "Guides", etc.)
 */
export interface SidebarSection {
  slug: string;
  label: string;
  basePath: string;
  items?: Record<string, SidebarItem>;
  groups?: Record<string, SidebarGroup>;
}

/**
 * Main sidebar configuration with theme support
 */
export interface SidebarConfig {
  label?: string;
  sections: SidebarSection[];
}

interface SidebarProps {
  config: SidebarConfig;
  headerContent?: React.ReactNode;
  footerContent?: React.ReactNode;
}

/**
 * Reusable link component for sidebar items
 */
const SidebarLink = ({
  to,
  isActive,
  className = "",
  style,
  params,
  children,
}: {
  to: string;
  isActive: boolean;
  className?: string;
  style?: React.CSSProperties;
  params?: Record<string, unknown>;
  children: React.ReactNode;
}) => {
  const activeClass = `bg-primary text-primary-foreground font-medium`;
  const inactiveClass = `text-muted-foreground hover:bg-muted hover:text-muted-foreground`;

  return (
    <Link
      to={to}
      params={params}
      style={style}
      className={cn(
        "font-handwriting-descent block rounded-md py-1 text-base",
        className,
        isActive ? activeClass : inactiveClass,
      )}
    >
      {children}
    </Link>
  );
};

/**
 * Tab for selecting sections
 */
const SectionTab = ({
  to,
  isActive,
  className = "",
  params,
  children,
}: {
  to: string;
  isActive: boolean;
  className?: string;
  params?: Record<string, unknown>;
  children: React.ReactNode;
}) => {
  const activeClass = `bg-primary text-white font-medium`;
  const inactiveClass = `text-muted-foreground hover:bg-muted hover:text-muted-foreground`;

  return (
    <Link
      to={to}
      params={params}
      className={cn(
        "font-handwriting-descent w-full rounded-md px-3 py-1 text-base",
        className,
        isActive ? activeClass : inactiveClass,
      )}
    >
      {children}
    </Link>
  );
};

/**
 * Group label header
 */
const GroupLabel = ({ label }: { label: string }) => {
  return (
    <div
      className={cn(
        "text-primary font-handwriting block cursor-default px-3 py-1 font-semibold",
      )}
    >
      {label}
    </div>
  );
};

/**
 * Chevron button component for expand/collapse
 */
const ChevronButton = ({
  isExpanded,
  onClick,
}: {
  isExpanded: boolean;
  onClick: () => void;
}) => {
  return (
    <button
      onClick={onClick}
      className={cn("mr-1 flex h-5 w-5 items-center justify-center")}
      aria-label={isExpanded ? "Collapse" : "Expand"}
    >
      {isExpanded ? (
        <ChevronDown size={16} className="text-muted-foreground" />
      ) : (
        <ChevronRight size={16} className="text-muted-foreground" />
      )}
    </button>
  );
};

/**
 * Hook for managing expansion state with auto-expand on active
 */
const useExpansion = (isActive: boolean) => {
  const [isExpanded, setIsExpanded] = React.useState(isActive);

  // Auto-expand when active
  React.useEffect(() => {
    if (isActive && !isExpanded) {
      setIsExpanded(true);
    }
  }, [isActive]);

  const toggleExpand = () => setIsExpanded(!isExpanded);

  return { isExpanded, toggleExpand };
};

/**
 * Component for rendering nested items (folders)
 */
interface NestedItemsProps {
  items: Record<string, SidebarItem>;
  basePath: string;
  isActivePath: (path: string, routePath?: string) => boolean;
  indentLevel?: number;
}

/**
 * Regular item component (with optional nested items for hybrid items)
 */
const SidebarItemLink = ({
  itemSlug,
  item,
  basePath,
  isActivePath,
  indentLevel,
}: {
  itemSlug: string;
  item: SidebarItem;
  basePath: string;
  isActivePath: (path: string, routePath?: string) => boolean;
  indentLevel: number;
}) => {
  // For navigation: Use routePath if provided, otherwise construct the path
  const navigationUrl = item.routePath || `${basePath}/${itemSlug}`;
  // For active state determination: Use the logical path which may include /index
  const logicalPath = `${basePath}/${itemSlug}`;
  // Determine if this item is active
  const isActive = isActivePath(logicalPath, item.routePath);

  // Check if this item has children (hybrid case)
  const hasChildren = item.items && Object.keys(item.items).length > 0;
  const { isExpanded, toggleExpand } = useExpansion(isActive);

  if (!hasChildren) {
    // Simple link without children
    return (
      <SidebarLink
        to={navigationUrl}
        isActive={isActive}
        className=""
        style={{
          paddingLeft: `${0.75 + indentLevel * 0.5}rem`,
          paddingRight: "0.75rem",
          flex: 1,
        }}
      >
        {item.label}
      </SidebarLink>
    );
  }

  // Hybrid: link with children
  return (
    <div>
      <div className="flex items-center">
        <SidebarLink
          to={navigationUrl}
          isActive={isActive}
          className="flex items-center gap-1"
          style={{
            paddingLeft: `${0.75 + indentLevel * 0.5}rem`,
            paddingRight: "0.75rem",
            flex: 1,
          }}
        >
          <span>{item.label}</span>
          <button
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              toggleExpand();
            }}
            className="flex shrink-0 items-center justify-center"
            aria-label={isExpanded ? "Collapse" : "Expand"}
          >
            {isExpanded ? (
              <ChevronDown size={16} />
            ) : (
              <ChevronRight size={16} />
            )}
          </button>
        </SidebarLink>
      </div>

      {/* Render nested items if expanded */}
      {isExpanded && (
        <div className="pt-1 pb-2">
          <NestedItems
            items={item.items!}
            basePath={logicalPath}
            isActivePath={isActivePath}
            indentLevel={indentLevel + 1}
          />
        </div>
      )}
    </div>
  );
};

/**
 * Folder component (with nested items)
 */
const NestedFolder = ({
  itemSlug,
  item,
  basePath,
  isActivePath,
  indentLevel,
}: {
  itemSlug: string;
  item: SidebarItem;
  basePath: string;
  isActivePath: (path: string, routePath?: string) => boolean;
  indentLevel: number;
}) => {
  // For active state determination: Use the logical path which may include /index
  const logicalPath = `${basePath}/${itemSlug}`;
  // Get children items
  const children = item.items || {};

  // Determine if this folder or any of its children are active
  const isActive = isActivePath(logicalPath, item.routePath);

  // Use expansion hook
  const { isExpanded, toggleExpand } = useExpansion(isActive);

  return (
    <div>
      <div
        className={cn(
          "hover:bg-muted flex items-center rounded-md",
          isActive ? "text-accent" : "text-muted-foreground",
        )}
      >
        <ChevronButton isExpanded={isExpanded} onClick={toggleExpand} />

        {/* Folder label button */}
        <button
          onClick={toggleExpand}
          className={cn("block w-full rounded-md py-1 text-left font-medium")}
          style={{
            paddingRight: "0.75rem",
            flex: 1,
          }}
        >
          {item.label}
        </button>
      </div>

      {/* Render nested items if expanded */}
      {isExpanded && (
        <div className="pt-1 pb-2">
          <NestedItems
            items={children}
            basePath={logicalPath}
            isActivePath={isActivePath}
            indentLevel={indentLevel + 1}
          />
        </div>
      )}
    </div>
  );
};

/**
 * Individual nested item component - renders either a folder (no content) or a link (with optional children)
 */
const NestedItem = ({
  itemSlug,
  item,
  basePath,
  isActivePath,
  indentLevel,
}: {
  itemSlug: string;
  item: SidebarItem;
  basePath: string;
  isActivePath: (path: string, routePath?: string) => boolean;
  indentLevel: number;
}) => {
  // Items with content render as links (even if they have children)
  // Items without content render as pure folders
  return item.hasContent ? (
    <SidebarItemLink
      itemSlug={itemSlug}
      item={item}
      basePath={basePath}
      isActivePath={isActivePath}
      indentLevel={indentLevel}
    />
  ) : (
    <NestedFolder
      itemSlug={itemSlug}
      item={item}
      basePath={basePath}
      isActivePath={isActivePath}
      indentLevel={indentLevel}
    />
  );
};

/**
 * Container component for a group of nested items
 */
const NestedItems = ({
  items,
  basePath,
  isActivePath,
  indentLevel = 0,
}: NestedItemsProps) => {
  // Ensure we always have an object, even if items is undefined
  const safeItems = items || {};

  return (
    <div className={`mt-1 space-y-0.5 ${indentLevel > 0 ? "ml-3" : ""}`}>
      {Object.entries(safeItems).map(([itemSlug, item]) => (
        <NestedItem
          key={itemSlug}
          itemSlug={itemSlug}
          item={item}
          basePath={basePath}
          isActivePath={isActivePath}
          indentLevel={indentLevel}
        />
      ))}
    </div>
  );
};

/**
 * Renders content for a specific section
 */
const SectionContent = ({
  section,
  isActivePath,
}: {
  section: SidebarSection;
  isActivePath: (path: string) => boolean;
}) => {
  if (!section) return null;

  return (
    <>
      {/* Section top-level items */}
      {section.items && Object.keys(section.items).length > 0 && (
        <NestedItems
          items={section.items}
          basePath={section.basePath}
          isActivePath={isActivePath}
        />
      )}

      {/* Section groups */}
      {section.groups &&
        Object.entries(section.groups).map(([groupSlug, group]) => {
          return (
            <div key={groupSlug} className="pt-2">
              {/* Group label - not selectable/highlightable */}
              <GroupLabel label={group.label} />

              {/* Group items */}
              <NestedItems
                items={group.items}
                basePath={`${section.basePath}/${groupSlug}`}
                isActivePath={isActivePath}
                indentLevel={1}
              />
            </div>
          );
        })}
    </>
  );
};

/**
 * Generic sidebar component that can be used for any navigation structure
 */
const Sidebar = ({ config, headerContent, footerContent }: SidebarProps) => {
  // Get current route from TanStack Router
  const router = useRouterState();
  const currentPath = router.location.pathname;

  // Store and restore scroll position
  const sidebarRef = React.useRef<HTMLDivElement>(null);
  const sidebarId = config.label
    ? config.label.toLowerCase().replace(/\s+/g, "-")
    : "sidebar";

  // Use state to track the last path, to know when navigation happens
  const [lastPath, setLastPath] = React.useState(currentPath);

  // When the current path changes, update lastPath state
  React.useEffect(() => {
    // Save the current scroll position before changing paths
    if (lastPath !== currentPath && sidebarRef.current) {
      const scrollKey = `sidebar-scroll-${sidebarId}`;
      sessionStorage.setItem(
        scrollKey,
        sidebarRef.current.scrollTop.toString(),
      );
    }

    setLastPath(currentPath);
  }, [currentPath, lastPath, sidebarId]);

  // Restore scroll position on mount and after page changes
  React.useEffect(() => {
    const scrollKey = `sidebar-scroll-${sidebarId}`;

    // Restore scroll position with minimal delay to ensure rendering is complete
    // Use requestAnimationFrame for the best timing with browser rendering cycle
    const timer = requestAnimationFrame(() => {
      const savedScroll = sessionStorage.getItem(scrollKey);
      if (savedScroll && sidebarRef.current) {
        sidebarRef.current.scrollTop = parseInt(savedScroll, 10);
      }
    });

    return () => cancelAnimationFrame(timer);
  }, [sidebarId, currentPath]);

  // Helper function to check if a path matches the current path
  const isActivePath = (path: string, routePath?: string) => {
    // If a routePath is provided, check that first
    if (routePath && routePath === currentPath) {
      return true;
    }

    // For index pages, their logical path is e.g. /docs/product/index
    // but the current path will be /docs/product/ in the browser
    // Check for direct match with current path (as-is)
    if (path === currentPath) {
      return true;
    }

    // Then check for index-specific matches
    if (path.endsWith("/index")) {
      // Remove 'index' to get the parent path with trailing slash
      const parentPath = path.slice(0, -5);

      // Check if current path equals the parent path (with or without trailing slash)
      if (parentPath === currentPath || parentPath === currentPath + "/") {
        return true;
      }
    }

    // If it's not an index page, check parent/child relationship
    // Normalize paths by ensuring they end with a slash
    const normalizedPath = path.endsWith("/") ? path : `${path}/`;
    const normalizedCurrentPath = currentPath.endsWith("/")
      ? currentPath
      : `${currentPath}/`;

    // Special case to avoid matching the root path with everything
    if (normalizedPath === "/") {
      return normalizedCurrentPath === "/";
    }

    return normalizedCurrentPath.startsWith(normalizedPath);
  };

  // Find active section by checking which section's base path matches the current path
  // Preserve the original order from config, but find the most specific match (longest path)
  const matchingSections = config.sections
    .filter((section) => currentPath.startsWith(section.basePath))
    .sort((a, b) => b.basePath.length - a.basePath.length);

  // Use the most specific match (if any), otherwise undefined
  const activeSection =
    matchingSections.length > 0 ? matchingSections[0].slug : undefined;

  return (
    <aside className="flex h-full flex-col overflow-hidden">
      {/* Custom header content if provided */}
      {headerContent && <div className="mb-5">{headerContent}</div>}

      {/* Section tabs */}
      {config.sections.length > 1 && (
        <>
          <div className="mb-4 flex flex-col space-y-0.5">
            {config.sections.map((section) => (
              <SectionTab
                key={section.slug}
                to={section.basePath}
                isActive={section.slug === activeSection}
              >
                {section.label}
              </SectionTab>
            ))}
          </div>

          {/* Border line below section buttons */}
          <div className="pb-4">
            <div className="border-muted border border-b"></div>
          </div>
        </>
      )}

      {/* Scrollable content area that flexes to fill remaining space */}
      <div className="flex min-h-0 flex-1 flex-col">
        <div ref={sidebarRef} className="min-h-0 flex-1 overflow-y-auto">
          <nav className="space-y-1 pb-6">
            {/* Show content for active section */}
            {activeSection ? (
              <SectionContent
                section={config.sections.find((s) => s.slug === activeSection)!}
                isActivePath={isActivePath}
              />
            ) : (
              // If no active section, show first section as default
              config.sections.length > 0 && (
                <SectionContent
                  section={config.sections[0]}
                  isActivePath={isActivePath}
                />
              )
            )}
          </nav>
        </div>

        {/* Footer content if provided - natural height */}
        {footerContent && <div className="shrink-0">{footerContent}</div>}
      </div>
    </aside>
  );
};

export default Sidebar;
