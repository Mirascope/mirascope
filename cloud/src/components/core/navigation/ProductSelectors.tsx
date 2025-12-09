import { Link, useRouterState } from "@tanstack/react-router";
import { getProductRoute } from "@/src/lib/routes";
import { type Product, productKey } from "@/src/lib/content/spec";
import { useProduct } from "@/src/components";
import { getAllDocInfo } from "@/src/lib/content";
import { canonicalizePath } from "@/src/lib/utils";

// Build cache of valid doc paths at module level
const validDocPaths = new Set<string>();
let pathsInitialized = false;

function buildValidDocPaths() {
  if (pathsInitialized) return;

  try {
    // Dynamically import getAllDocInfo to avoid SSR module resolution issues
    // Check if it's available and is a function
    if (typeof getAllDocInfo !== "function") {
      // Will retry on first access when the function is available
      return;
    }

    const allDocs = getAllDocInfo();
    if (!Array.isArray(allDocs)) {
      // Will retry on first access
      return;
    }

    allDocs.forEach((doc) => {
      validDocPaths.add(canonicalizePath(doc.routePath));
    });

    // Add special llms-full routes manually
    validDocPaths.add("/docs/mirascope/llms-full");
    validDocPaths.add("/docs/mirascope/v2/llms-full");
    validDocPaths.add("/docs/lilypad/llms-full");

    pathsInitialized = true;
  } catch {
    // If docRegistry isn't ready yet, paths will be built on first access
    // Silently fail - will retry when actually needed
  }
}

// Don't initialize at module load - wait until first use
// This avoids SSR module resolution issues

/**
 * Smart navigation: tries to map current path to equivalent path for target product
 * Falls back to progressively shorter paths until finding a valid route
 */
function getSmartProductRoute(
  currentProduct: Product,
  targetProduct: Product,
  currentPath: string
): string {
  // Ensure paths are initialized before use
  if (!pathsInitialized) {
    buildValidDocPaths();
    // If still not initialized after retry, just proceed with empty set
    // The route matching will still work, just won't have the cache
  }

  // If not in docs section, use default product route
  if (!currentPath.startsWith("/docs/")) {
    return getProductRoute(targetProduct);
  }

  const targetKey = productKey(targetProduct);
  const currentKey = productKey(currentProduct);

  // If already on the target product, return current path
  if (currentKey == targetKey) {
    return currentPath;
  }

  const fullTargetPath = currentPath.replace(`/docs/${currentKey}`, `/docs/${targetKey}`);
  if (validDocPaths.has(canonicalizePath(fullTargetPath))) {
    return fullTargetPath;
  }
  const restOfPath = fullTargetPath.replace(`/docs/${targetKey}/`, "").split("/");

  // Try progressively shorter paths
  for (let i = restOfPath.length - 1; i > 0; i--) {
    const shorterPath = `/docs/${targetKey}/${restOfPath.slice(0, i).join("/")}`;
    if (validDocPaths.has(canonicalizePath(shorterPath))) {
      return shorterPath;
    }
  }

  // Fallback to base product route
  return getProductRoute(targetProduct);
}

function V2Badge() {
  const activeClass = "bg-secondary text-secondary-foreground border-secondary";
  const baseClass = "absolute -top-1 -right-2 text-2xs font-semibold border rounded-lg px-1";

  return <span className={`${baseClass} ${activeClass}`}>v2</span>;
}

function MirascopeSelector({
  currentProduct,
  currentPath,
}: {
  currentProduct: Product;
  currentPath: string;
}) {
  const isMirascope = currentProduct.name === "mirascope";
  const isV2 = currentProduct.version === "v2";

  const v1Route = getSmartProductRoute(currentProduct, { name: "mirascope" }, currentPath);

  return (
    <div className={`relative ${isV2 ? "pr-3" : ""}`}>
      {isMirascope ? (
        <span className="text-mirascope-purple text-lg font-medium">Mirascope</span>
      ) : (
        <Link
          to={v1Route}
          className="text-muted-foreground hover:text-mirascope-purple text-lg font-medium"
        >
          Mirascope
        </Link>
      )}

      {isV2 && <V2Badge />}
    </div>
  );
}

/**
 * LilypadSelector - Shows Lilypad as active or link based on current product
 */
function LilypadSelector({
  currentProduct,
  currentPath,
}: {
  currentProduct: Product;
  currentPath: string;
}) {
  const isActive = currentProduct.name === "lilypad";

  if (isActive) {
    return <span className="text-lilypad-green text-lg font-medium">Lilypad</span>;
  }

  const route = getSmartProductRoute(currentProduct, { name: "lilypad" }, currentPath);
  return (
    <Link to={route} className="text-muted-foreground hover:text-lilypad-green text-lg font-medium">
      Lilypad
    </Link>
  );
}

/**
 * DocsProductSelector - Shows current product title and link to other product
 */
export function DocsProductSelector() {
  const router = useRouterState();
  const currentPath = router.location.pathname;
  const currentProduct = useProduct();

  return (
    <div className="flex space-x-4 px-1">
      <MirascopeSelector currentProduct={currentProduct} currentPath={currentPath} />
      <LilypadSelector currentProduct={currentProduct} currentPath={currentPath} />
    </div>
  );
}
