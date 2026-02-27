import React, { useState, useEffect, useCallback } from "react";
import { createPortal } from "react-dom";

import { cn } from "@/app/lib/utils";

interface ResponsiveImageProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  src?: string;
  alt?: string;
  className?: string;
}

/** Props for the expanded image modal */
interface ImageModalProps {
  isOpen: boolean;
  onClose: () => void;
  src: string;
  alt?: string;
  /** WebP source for responsive images; if omitted, renders a plain img */
  largeWebp?: string;
}

/** Modal overlay for viewing expanded images */
const ImageModal: React.FC<ImageModalProps> = ({
  isOpen,
  onClose,
  src,
  alt,
  largeWebp,
}) => {
  if (!isOpen) return null;

  // Use a portal to render at document.body so the modal escapes any
  // ancestor stacking contexts created by backdrop-filter, transform, etc.
  return createPortal(
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm md:p-8"
      onClick={onClose}
    >
      <div
        className="relative max-h-[90vh] max-w-[90vw] overflow-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {largeWebp ? (
          <picture>
            <source srcSet={largeWebp} type="image/webp" />
            <img
              src={src}
              alt={alt}
              className="max-h-[90vh] max-w-full rounded-lg object-contain"
              loading="eager"
            />
          </picture>
        ) : (
          <img
            src={src}
            alt={alt}
            className="max-h-[90vh] max-w-full rounded-lg object-contain"
            loading="eager"
          />
        )}
        <button
          onClick={onClose}
          className="absolute top-2 right-2 flex h-8 w-8 items-center justify-center rounded-full bg-black/50 text-xl leading-none font-medium text-white transition-colors hover:bg-black/70"
          aria-label="Close expanded image"
        >
          X
        </button>
      </div>
    </div>,
    document.body,
  );
};

/** Hook to manage expanded image state and keyboard/scroll handling */
const useExpandableImage = () => {
  const [isExpanded, setIsExpanded] = useState(false);

  const toggleExpanded = useCallback(() => {
    setIsExpanded((prev) => !prev);
  }, []);

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

  return { isExpanded, toggleExpanded };
};

/**
 * Responsive image component for MDX content
 * - Automatically serves WebP versions of images
 * - Provides responsive versions based on viewport size
 * - Falls back to original image if WebP not supported
 * - Supports click-to-expand functionality for all image types
 */
export const ResponsiveImage: React.FC<ResponsiveImageProps> = ({
  src,
  alt,
  className,
  ...props
}) => {
  const { isExpanded, toggleExpanded } = useExpandableImage();

  // Handle missing src or non-assets paths
  if (!src || !src.startsWith("/assets/")) {
    return <img src={src} alt={alt} className={className} {...props} />;
  }

  // Extract base path and extension
  const extension = src.split(".").pop()?.toLowerCase() || "";

  // SVG and GIF files don't need responsive handling
  if (["svg", "gif"].includes(extension)) {
    return (
      <>
        <img
          src={src}
          alt={alt}
          className={cn("cursor-pointer", className)}
          onClick={toggleExpanded}
          {...props}
        />
        <ImageModal
          isOpen={isExpanded}
          onClose={toggleExpanded}
          src={src}
          alt={alt}
        />
      </>
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
        className={cn(
          "cursor-pointer",
          isExpanded ? "pointer-events-none" : "",
        )}
        onClick={toggleExpanded}
      >
        {/* Small viewport */}
        <source
          media="(max-width: 640px)"
          srcSet={smallWebp}
          type="image/webp"
        />
        {/* Medium viewport */}
        <source
          media="(max-width: 1024px)"
          srcSet={mediumWebp}
          type="image/webp"
        />
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

      <ImageModal
        isOpen={isExpanded}
        onClose={toggleExpanded}
        src={src}
        alt={alt}
        largeWebp={largeWebp}
      />
    </>
  );
};

export default ResponsiveImage;
