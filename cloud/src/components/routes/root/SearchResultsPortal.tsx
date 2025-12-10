import React, { useEffect, useState } from "react";
import { createPortal } from "react-dom";

interface PortalProps {
  /**
   * Content to render in the portal
   */
  children: React.ReactNode;
}

/**
 * Renders its children in a portal at the root of the DOM tree,
 * outside any stacking contexts created by parent elements.
 *
 * This allows for positioning elements like dropdowns and tooltips
 * that need to appear above all other content regardless of z-index
 * stacking contexts in the component hierarchy.
 */
export default function SearchResultsPortal({ children }: PortalProps) {
  // State to hold the DOM element reference
  const [portalRoot, setPortalRoot] = useState<HTMLDivElement | null>(null);

  // Create portal container on mount and clean it up on unmount
  useEffect(() => {
    // Create portal container element
    const portalElement = document.createElement("div");

    // Apply styles to ensure proper positioning
    portalElement.style.position = "fixed";
    portalElement.style.top = "0";
    portalElement.style.left = "0";
    portalElement.style.width = "100%";
    portalElement.style.height = "0";
    portalElement.style.overflow = "visible";
    portalElement.style.zIndex = "9999"; // Very high z-index
    portalElement.setAttribute("data-search-results-portal", "true");

    // Add to DOM
    document.body.appendChild(portalElement);

    // Store reference
    setPortalRoot(portalElement);

    // Clean up on unmount
    return () => {
      if (document.body.contains(portalElement)) {
        document.body.removeChild(portalElement);
      }
    };
  }, []);

  // Only render the portal when we have a container
  if (!portalRoot) {
    return null;
  }

  // Create a portal to render children into the container
  return createPortal(children, portalRoot);
}
