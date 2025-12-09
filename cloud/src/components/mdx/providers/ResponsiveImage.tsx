import React, { useState, useEffect, useCallback } from "react";
import { cn } from "@/src/lib/utils";

interface ResponsiveImageProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  src?: string;
  alt?: string;
  className?: string;
}

/**
 * Responsive image component for MDX content
 * - Automatically serves WebP versions of images
 * - Provides responsive versions based on viewport size
 * - Falls back to original image if WebP not supported
 * - Supports click-to-expand functionality
 */
export const ResponsiveImage: React.FC<ResponsiveImageProps> = ({
  src,
  alt,
  className,
  ...props
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  // Toggle expanded state
  const toggleExpanded = useCallback(() => {
    setIsExpanded((prev) => !prev);
  }, []);

  // Handle escape key to close expanded image
  useEffect(() => {
    const handleEscapeKey = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isExpanded) {
        setIsExpanded(false);
      }
    };

    document.addEventListener("keydown", handleEscapeKey);

    // Prevent scrolling when modal is open
    if (isExpanded) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }

    return () => {
      document.removeEventListener("keydown", handleEscapeKey);
      document.body.style.overflow = "";
    };
  }, [isExpanded]);

  // Handle missing src or non-assets paths
  if (!src || !src.startsWith("/assets/")) {
    return <img src={src} alt={alt} className={className} {...props} />;
  }

  // Extract base path and extension
  const extension = src.split(".").pop()?.toLowerCase() || "";

  // Skip responsive handling for SVG or GIF files
  if (["svg", "gif"].includes(extension)) {
    return (
      <img
        src={src}
        alt={alt}
        className={cn("cursor-pointer", className)}
        onClick={toggleExpanded}
        {...props}
      />
    );
  }

  // Prepare paths for WebP versions
  let basePath = src;

  // For non-WebP images, convert the path to WebP format
  if (extension !== "webp") {
    basePath = src.replace(`.${extension}`, "");
  } else {
    // For WebP images, just remove the extension
    basePath = src.replace(".webp", "");
  }

  // Construct WebP paths for different sizes
  const largeWebp = `${basePath}.webp`;
  const mediumWebp = `${basePath}-medium.webp`;
  const smallWebp = `${basePath}-small.webp`;

  return (
    <>
      <picture
        className={cn("cursor-pointer", isExpanded ? "pointer-events-none" : "")}
        onClick={toggleExpanded}
      >
        {/* Small viewport */}
        <source media="(max-width: 640px)" srcSet={smallWebp} type="image/webp" />
        {/* Medium viewport */}
        <source media="(max-width: 1024px)" srcSet={mediumWebp} type="image/webp" />
        {/* Large viewport - WebP */}
        <source srcSet={largeWebp} type="image/webp" />
        {/* Original fallback */}
        <img
          src={src}
          alt={alt}
          className={cn("rounded-lg", className)}
          loading="lazy"
          {...props}
        />
      </picture>

      {/* Expanded image modal */}
      {isExpanded && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm md:p-8"
          onClick={toggleExpanded}
        >
          <div
            className="relative max-h-[90vh] max-w-[90vw] overflow-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <picture>
              {/* Using the large version of the image */}
              <source srcSet={largeWebp} type="image/webp" />
              <img
                src={src}
                alt={alt}
                className="max-h-[90vh] max-w-full rounded-lg object-contain"
                loading="eager"
              />
            </picture>
            <button
              onClick={toggleExpanded}
              className="absolute top-2 right-2 flex h-8 w-8 items-center justify-center rounded-full bg-black/50 text-xl leading-none font-medium text-white transition-colors hover:bg-black/70"
              aria-label="Close expanded image"
            >
              X
            </button>
          </div>
        </div>
      )}
    </>
  );
};

export default ResponsiveImage;
