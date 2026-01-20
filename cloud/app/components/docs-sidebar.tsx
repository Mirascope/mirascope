import { useRouter } from "@tanstack/react-router";
import { docRegistry } from "@/app/lib/content/doc-registry";
import type { DocSpec, SectionSpec, VersionSpec } from "@/app/lib/content/spec";
import { type Provider } from "@/app/components/mdx/elements/model-provider-provider";
import Sidebar from "@/app/components/blocks/navigation/sidebar";
import type {
  SidebarConfig,
  SidebarItem,
  SidebarGroup,
  SidebarSection,
} from "@/app/components/blocks/navigation/sidebar";
import { docsSpec } from "@/content/docs/_meta";

interface DocsSidebarProps {
  selectedProvider?: Provider;
  onProviderChange?: (provider: Provider) => void;
}

/**
 * Detect the active version from the current URL path.
 * Returns the version string (e.g., "v1") or undefined for the default version.
 */
function detectActiveVersion(pathname: string): string | undefined {
  // URL pattern: /docs/v1/... or /docs/...
  const match = pathname.match(/^\/docs\/([^/]+)/);
  if (match) {
    const segment = match[1];
    // Check if this segment is a version (e.g., "v1", "v2")
    // A segment is a version if it matches a VersionSpec with that version
    const isVersion = docsSpec.some((v) => v.version === segment);
    if (isVersion) {
      return segment;
    }
  }
  return undefined;
}

/**
 * Find the VersionSpec that matches the active version.
 * If no version is specified, return the first VersionSpec without a version (default).
 */
function getActiveVersionSpec(
  activeVersion: string | undefined,
): VersionSpec | undefined {
  if (activeVersion) {
    return docsSpec.find((v) => v.version === activeVersion);
  }
  // Return the first version without a version string (the default)
  return docsSpec.find((v) => !v.version);
}

/**
 * Helper to convert the spec metadata to the sidebar format
 */
function createSidebarConfig(activeVersion: string | undefined): SidebarConfig {
  // Get all DocInfo objects
  const allDocInfo = docRegistry.getAllDocs();

  // Create a map from slug pattern to routePath for quick lookup
  // Key format: version/section/slug or version/slug for root items
  const slugToRoutePathMap: Map<string, string> = new Map();

  allDocInfo.forEach((doc) => {
    // Extract the slug pattern from the path
    // Strip "docs/" prefix to match the lookup format
    const prefix = "docs/";
    const keyPath = doc.path.startsWith(prefix)
      ? doc.path.slice(prefix.length)
      : doc.path;
    slugToRoutePathMap.set(keyPath, doc.routePath);
  });

  // Get the active version's spec
  const versionSpec = getActiveVersionSpec(activeVersion);
  if (!versionSpec) {
    // Fallback to empty config if no matching version found
    return {
      label: "Documentation",
      sections: [],
    };
  }

  const versionPrefix = versionSpec.version ?? "";
  const sections = [...versionSpec.sections];

  // Find index section to ensure it appears first
  const defaultIndex = sections.findIndex((s) => s.slug === "index");
  if (defaultIndex > 0) {
    // Move index section to the front
    const defaultSection = sections.splice(defaultIndex, 1)[0];
    sections.unshift(defaultSection);
  }

  // Convert doc specs to sidebar items
  function convertDocToSidebarItem(
    doc: DocSpec,
    parentPath: string,
  ): SidebarItem {
    // Construct the logical path for this item (used to look up routePath)
    const itemPath = parentPath ? `${parentPath}/${doc.slug}` : doc.slug;

    // Look up the routePath from DocInfo if available
    const routePath = slugToRoutePathMap.get(itemPath);

    // Determine hasContent: explicit value from doc, or default based on children
    const hasContent = doc.hasContent ?? !doc.children;

    const item: SidebarItem = {
      slug: doc.slug,
      label: doc.label,
      hasContent,
    };

    // Add routePath if we found a match
    if (routePath) {
      item.routePath = routePath;
    }

    // Process children if any
    if (doc.children && doc.children.length > 0) {
      item.items = {};

      doc.children.forEach((childDoc) => {
        const childItem = convertDocToSidebarItem(childDoc, itemPath);
        if (item.items) {
          item.items[childDoc.slug] = childItem;
        }
      });
    }

    return item;
  }

  // Helper to build path prefix for a section (matches logic in spec.ts getDocsFromSpec)
  function getSectionPathPrefix(section: SectionSpec): string {
    const isDefaultSection = section.slug === "index";
    const sectionSlug = isDefaultSection ? "" : section.slug;

    if (versionPrefix && sectionSlug) {
      return `${versionPrefix}/${sectionSlug}`;
    } else if (versionPrefix) {
      return versionPrefix;
    } else if (sectionSlug) {
      return sectionSlug;
    }
    return "";
  }

  // Create sidebar sections from spec sections
  const sidebarSections: SidebarSection[] = sections.map((section) => {
    const pathPrefix = getSectionPathPrefix(section);

    // Create basePath for URL routing
    const basePath = pathPrefix ? `/docs/${pathPrefix}` : "/docs";

    // Process direct items (those without children) and create groups for top-level folders
    const items: Record<string, SidebarItem> = {};
    const groups: Record<string, SidebarGroup> = {};

    section.children.forEach((child) => {
      const hasContent = child.hasContent ?? !child.children;

      if (hasContent) {
        // This item has content, add it to items (even if it also has children)
        items[child.slug] = convertDocToSidebarItem(child, pathPrefix);
      } else {
        // This is a pure folder (no content), add it as a group
        const groupItems: Record<string, SidebarItem> = {};

        // Get path for this group's children
        const groupPathPrefix = pathPrefix
          ? `${pathPrefix}/${child.slug}`
          : child.slug;

        // Process all items in this group
        if (child.children) {
          child.children.forEach((grandchild) => {
            // Convert the grandchild and its descendants to sidebar items
            const sidebarItem = convertDocToSidebarItem(
              grandchild,
              groupPathPrefix,
            );
            groupItems[grandchild.slug] = sidebarItem;
          });
        }

        // Add the group
        groups[child.slug] = {
          slug: child.slug,
          label: child.label,
          items: groupItems,
        };
      }
    });

    return {
      slug: section.slug,
      label: section.label,
      basePath,
      items,
      groups: Object.keys(groups).length > 0 ? groups : undefined,
    };
  });

  // Add links to other versions (inactive versions) for version switching
  const inactiveVersionSections: SidebarSection[] = docsSpec
    .filter((v) => {
      // Exclude the active version
      if (activeVersion) {
        return v.version !== activeVersion;
      }
      // If no active version (default), exclude the one without a version
      return v.version !== undefined;
    })
    .map((v) => {
      // Find the index section to get a nice label, or use a default
      const indexSection = v.sections.find((s) => s.slug === "index");
      const label = indexSection?.label ?? `${v.version ?? "Latest"} Docs`;
      const basePath = v.version ? `/docs/${v.version}` : "/docs";

      return {
        slug: v.version ?? "latest",
        label,
        basePath,
        items: {},
      };
    });

  // Return the complete sidebar config with inactive versions at the end
  return {
    label: "Documentation",
    sections: [...sidebarSections, ...inactiveVersionSections],
  };
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const DocsSidebar = (_props: DocsSidebarProps) => {
  const router = useRouter();
  const currentPath = router.state.location.pathname;

  // Detect which version we're viewing based on the URL
  const activeVersion = detectActiveVersion(currentPath);

  // Create sidebar configuration for the active version only
  const sidebarConfig = createSidebarConfig(activeVersion);

  // No header content needed since product links are in the main header now
  return <Sidebar config={sidebarConfig} />;
};

export default DocsSidebar;
