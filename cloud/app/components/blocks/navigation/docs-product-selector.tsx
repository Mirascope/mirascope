import { Link, useRouterState } from "@tanstack/react-router";
import { cn } from "@/app/lib/utils";
import type { ProductOption } from "@/app/lib/content/spec";

// Styles for product selector
const PRODUCT_SELECTOR_STYLES = {
  container: cn("bg-muted/50 mb-4 flex gap-1 rounded-lg p-1"),
  pill: cn(
    "text-muted-foreground hover:text-foreground flex-1 rounded-md px-3 py-1.5 text-center text-sm font-medium transition-all",
  ),
  activePill: cn("bg-primary/10 text-primary shadow-sm"),
};

interface DocsProductSelectorProps {
  /**
   * Available products for this section
   */
  products: ProductOption[];
  /**
   * Base path for product URLs (e.g., "/docs/learn")
   */
  basePath: string;
  /**
   * Optional className for the container
   */
  className?: string;
}

/**
 * Determine the selected product from the URL path
 */
function getSelectedProduct(
  pathname: string,
  basePath: string,
  products: ProductOption[],
): string | undefined {
  // Extract the segment after the base path
  // e.g., for /docs/learn/llm/messages, basePath=/docs/learn, extract "llm"
  const pathAfterBase = pathname.replace(basePath, "").replace(/^\//, "");
  const productSlug = pathAfterBase.split("/")[0];

  // Check if this matches a product
  const matchedProduct = products.find((p) => p.slug === productSlug);
  return matchedProduct?.slug;
}

/**
 * Product selector component for docs sidebar
 *
 * Renders a horizontal pill/tab selector at the top of the sidebar.
 * Only renders when the section has products defined.
 */
export default function DocsProductSelector({
  products,
  basePath,
  className,
}: DocsProductSelectorProps) {
  const router = useRouterState();
  const currentPath = router.location.pathname;

  const selectedProduct = getSelectedProduct(currentPath, basePath, products);

  // If no products, don't render anything
  if (!products || products.length === 0) {
    return null;
  }

  return (
    <div className={cn(PRODUCT_SELECTOR_STYLES.container, className)}>
      {products.map((product) => {
        const isActive = selectedProduct === product.slug;
        const productPath = `${basePath}/${product.slug}`;

        return (
          <Link
            key={product.slug}
            to={productPath}
            className={cn(
              PRODUCT_SELECTOR_STYLES.pill,
              isActive && PRODUCT_SELECTOR_STYLES.activePill,
            )}
          >
            {product.label}
          </Link>
        );
      })}
    </div>
  );
}
