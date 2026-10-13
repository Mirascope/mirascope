import { useRouter } from "@tanstack/react-router";

import type {
  SidebarConfig,
  SidebarGroup,
  SidebarItem,
  SidebarSection,
} from "@/app/components/blocks/navigation/sidebar";
import type { DocSpec, SectionSpec, VersionSpec } from "@/app/lib/content/spec";

import DocsProductSelector from "@/app/components/blocks/navigation/docs-product-selector";
import Sidebar from "@/app/components/blocks/navigation/sidebar";
import { type Provider } from "@/app/components/mdx/elements/model-provider-provider";
import { docRegistry } from "@/app/lib/content/doc-registry";

interface DocsSidebarProps {
  selectedProvider?: Provider;
  onProviderChange?: (provider: Provider) => void;
}

/**
 * Detect the active version from the current URL path.
 * Returns the version string (e.g., "v1") or undefined for the default version.
 */
function detectActiveVersion(pathname: string): string | undefined {
  const match = pathname.match(/^\/docs\/([^/]+)/);
  if (match) {
    const segment = match[1];
    const isVersion = docRegistry
      .getFullSpec()
      .some((v) => v.version === segment);
    if (isVersion) {
      return segment;
    }
  }
  return undefined;
}

/**
 * Find the VersionSpec that matches the active version.
 */
function getActiveVersionSpec(
  activeVersion: string | undefined,
): VersionSpec | undefined {
  const fullSpec = docRegistry.getFullSpec();
  if (activeVersion) {
    return fullSpec.find((v) => v.version === activeVersion);
  }
  return fullSpec.find((v) => !v.version);
}

/**
 * Detect the active section from the current URL path.
 */
function detectActiveSection(
  pathname: string,
  versionSpec: VersionSpec | undefined,
): SectionSpec | undefined {
  if (!versionSpec) return undefined;

  const versionPrefix = versionSpec.version
    ? `/docs/${versionSpec.version}`
    : "/docs";
  const pathAfterVersion = pathname
    .replace(versionPrefix, "")
    .replace(/^\//, "");
  const firstSegment = pathAfterVersion.split("/")[0];

  // Check if this segment matches a non-index section
  for (const section of versionSpec.sections) {
    if (section.slug !== "index" && section.slug === firstSegment) {
      return section;
    }
  }

  // Check if we're at the root or in the index section
  const indexSection = versionSpec.sections.find((s) => s.slug === "index");
  if (indexSection) {
    // Check if the path matches a child of the index section
    const childSlugs = indexSection.children.map((c) => c.slug);
    if (
      firstSegment === "" ||
      childSlugs.includes(firstSegment) ||
      firstSegment === "index"
    ) {
      return indexSection;
    }
  }

  // Default to index section or first section
  return indexSection ?? versionSpec.sections[0];
}

/**
 * Detect the selected product from the URL path for sections with products.
 */
function detectSelectedProduct(
  pathname: string,
  section: SectionSpec,
  versionSpec: VersionSpec | undefined,
): string | undefined {
  if (!section.products || section.products.length === 0) {
    return undefined;
  }

  const versionPrefix = versionSpec?.version
    ? `/docs/${versionSpec.version}`
    : "/docs";
  const sectionPath =
    section.slug === "index"
      ? versionPrefix
      : `${versionPrefix}/${section.slug}`;
  const pathAfterSection = pathname.replace(sectionPath, "").replace(/^\//, "");
  const productSlug = pathAfterSection.split("/")[0];

  const matchedProduct = section.products.find((p) => p.slug === productSlug);
  return matchedProduct?.slug ?? section.products[0]?.slug;
}

/**
 * Create sidebar configuration for the current section.
 * Shows flat items filtered by selected product if applicable.
 */
function createSidebarConfig(
  section: SectionSpec,
  versionSpec: VersionSpec | undefined,
  selectedProduct: string | undefined,
): SidebarConfig {
  const allDocInfo = docRegistry.getAllDocs();
  const slugToRoutePathMap: Map<string, string> = new Map();

  allDocInfo.forEach((doc) => {
    const prefix = "docs/";
    const keyPath = doc.path.startsWith(prefix)
      ? doc.path.slice(prefix.length)
      : doc.path;
    slugToRoutePathMap.set(keyPath, doc.routePath);
  });

  const versionPrefix = versionSpec?.version ?? "";

  // Helper to build path prefix for a section
  function getSectionPathPrefix(): string {
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

  // Convert doc specs to sidebar items
  function convertDocToSidebarItem(
    doc: DocSpec,
    parentPath: string,
  ): SidebarItem {
    const itemPath = parentPath ? `${parentPath}/${doc.slug}` : doc.slug;
    const routePath = slugToRoutePathMap.get(itemPath);
    const hasContent = doc.hasContent ?? !doc.children;

    const item: SidebarItem = {
      slug: doc.slug,
      label: doc.label,
      hasContent,
    };

    if (routePath) {
      item.routePath = routePath;
    }

    // Include nested items for expansion
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

  // Convert a doc with children to a SidebarGroup (always expanded, colored label)
  function convertDocToGroup(doc: DocSpec, parentPath: string): SidebarGroup {
    const groupPath = parentPath ? `${parentPath}/${doc.slug}` : doc.slug;
    const items: Record<string, SidebarItem> = {};

    if (doc.children) {
      doc.children.forEach((childDoc) => {
        items[childDoc.slug] = convertDocToSidebarItem(childDoc, groupPath);
      });
    }

    return {
      slug: doc.slug,
      label: doc.label,
      items,
    };
  }

  const pathPrefix = getSectionPathPrefix();
  const basePath = pathPrefix ? `/docs/${pathPrefix}` : "/docs";

  // Get children to display
  let childrenToDisplay: DocSpec[] = section.children;

  // If section has products and a product is selected, filter to that product's children
  if (section.products && selectedProduct) {
    // Find the product's DocSpec in section.children
    const productDoc = section.children.find((c) => c.slug === selectedProduct);
    if (productDoc && productDoc.children) {
      childrenToDisplay = productDoc.children;
    }
  }

  // Build the correct path prefix for the items
  const itemPathPrefix =
    section.products && selectedProduct
      ? pathPrefix
        ? `${pathPrefix}/${selectedProduct}`
        : selectedProduct
      : pathPrefix;

  // Separate items into flat items (no children) and groups (with children)
  const items: Record<string, SidebarItem> = {};
  const groups: Record<string, SidebarGroup> = {};

  childrenToDisplay.forEach((child) => {
    if (child.children && child.children.length > 0) {
      // Items with children become groups (always expanded, colored label)
      groups[child.slug] = convertDocToGroup(child, itemPathPrefix);
    } else {
      // Items without children are regular sidebar items
      items[child.slug] = convertDocToSidebarItem(child, itemPathPrefix);
    }
  });

  // Create a single section for the sidebar
  const sectionBasePath =
    section.products && selectedProduct
      ? `${basePath}/${selectedProduct}`
      : basePath;

  const sidebarSection: SidebarSection = {
    slug: section.slug,
    label: section.label,
    basePath: sectionBasePath,
    items: Object.keys(items).length > 0 ? items : undefined,
    groups: Object.keys(groups).length > 0 ? groups : undefined,
  };

  return {
    label: section.label,
    sections: [sidebarSection],
  };
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const DocsSidebar = (_props: DocsSidebarProps) => {
  const router = useRouter();
  const currentPath = router.state.location.pathname;

  // Detect which version we're viewing
  const activeVersion = detectActiveVersion(currentPath);
  const versionSpec = getActiveVersionSpec(activeVersion);

  // Detect which section we're in
  const activeSection = detectActiveSection(currentPath, versionSpec);

  // Detect selected product if section has products
  const selectedProduct = activeSection
    ? detectSelectedProduct(currentPath, activeSection, versionSpec)
    : undefined;

  // Create sidebar configuration for the current section only
  const sidebarConfig = activeSection
    ? createSidebarConfig(activeSection, versionSpec, selectedProduct)
    : { label: "Documentation", sections: [] };

  // Compute base path for product selector
  const versionPrefix = versionSpec?.version
    ? `/docs/${versionSpec.version}`
    : "/docs";
  const sectionBasePath =
    activeSection?.slug === "index"
      ? versionPrefix
      : `${versionPrefix}/${activeSection?.slug}`;

  return (
    <div className="flex flex-col">
      {/* Product selector - only show if section has products */}
      {activeSection?.products && activeSection.products.length > 0 && (
        <DocsProductSelector
          products={activeSection.products}
          basePath={sectionBasePath}
        />
      )}

      {/* Sidebar with flat items for current section */}
      <Sidebar config={sidebarConfig} />
    </div>
  );
};

export default DocsSidebar;
