import { docRegistry } from "@/app/lib/content/doc-registry";
import type { DocSpec, SectionSpec } from "@/app/lib/content/spec";
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

// No product selector needed in sidebar - now in header

/**
 * Helper to convert the spec metadata to the sidebar format
 */
function createSidebarConfig(): SidebarConfig {
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

  // Get all sections and order them appropriately
  const allSections = [...docsSpec.sections];

  // Find index section to ensure it appears first
  const defaultIndex = allSections.findIndex((s) => s.slug === "index");
  if (defaultIndex > 0) {
    // Move index section to the front
    const defaultSection = allSections.splice(defaultIndex, 1)[0];
    allSections.unshift(defaultSection);
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
    const versionPrefix = section.version || "";
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
  const sidebarSections: SidebarSection[] = allSections.map((section) => {
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

  // Inject LLM Documentation section
  // Use the first section's version for the LLM docs path
  // const firstVersion = allSections[0]?.version || "";
  // const llmBasePath = firstVersion ? `/docs/${firstVersion}` : "/docs";

  // todo(sebastian): add LLM section back in
  // const llmItem: SidebarItem = {
  //   slug: "llms",
  //   label: "LLMs Text",
  //   routePath: `${llmBasePath}/llms-full`,
  //   hasContent: true,
  // };
  // const llmSection: SidebarSection = {
  //   slug: "llms",
  //   label: "LLMs Text",
  //   basePath: `${llmBasePath}/llms-full`,
  //   items: { llms: llmItem },
  // };

  // Add the LLM section to the end
  // sidebarSections.push(llmSection);

  // Return the complete sidebar config
  return {
    label: "Documentation",
    sections: sidebarSections,
  };
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const DocsSidebar = (_props: DocsSidebarProps) => {
  // Create sidebar configuration
  const sidebarConfig = createSidebarConfig();

  // No header content needed since product links are in the main header now
  return <Sidebar config={sidebarConfig} />;
};

export default DocsSidebar;
