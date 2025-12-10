import { Outlet, createFileRoute, useSearch } from "@tanstack/react-router";
import { useEffect } from "react";
import { z } from "zod";
import { getAllDevMeta } from "@/src/lib/content";
import { setDevProductPreference } from "@/src/lib/utils";
import type { ProductName } from "@/src/lib/content/spec";

// Define the search schema with Zod validation
const devSearchSchema = z.object({
  product: z.enum(["mirascope", "lilypad"]).optional(),
});

// Session storage key
const DEV_PRODUCT_STORAGE_KEY = "devProductPreference";

export const Route = createFileRoute("/dev")({
  ssr: false, // Client-side rendered
  // Validate search params against the schema
  validateSearch: devSearchSchema,

  // Load dev pages data for all child routes
  loader: async () => {
    try {
      const devPages = await getAllDevMeta();
      return { devPages };
    } catch (error) {
      console.error("Error loading dev pages:", error);
      return { devPages: [] };
    }
  },

  // Before loading any dev route, check if we need to add the product param
  beforeLoad: ({ search, location }) => {
    // If we're on a dev route and there's no product param in the URL...
    if (location.pathname.startsWith("/dev") && !search.product) {
      // ... but we have a stored preference, redirect to add it
      if (typeof sessionStorage !== "undefined") {
        const storedProduct = sessionStorage.getItem(DEV_PRODUCT_STORAGE_KEY) as ProductName;
        if (storedProduct && (storedProduct === "mirascope" || storedProduct === "lilypad")) {
          // Return the search params - TanStack will redirect with these params added
          return {
            search: {
              ...search,
              product: storedProduct,
            },
          };
        }
      }
    }
  },

  // Component that serves as a wrapper for all dev routes
  component: DevParentRoute,
});

function DevParentRoute() {
  // Get the product from search params
  const { product } = useSearch({ from: "/dev" });

  // When product search param changes, store it in session storage
  useEffect(() => {
    if (product) {
      setDevProductPreference(product);
    }
  }, [product]);

  // The Outlet component renders the child route component
  return <Outlet />;
}

