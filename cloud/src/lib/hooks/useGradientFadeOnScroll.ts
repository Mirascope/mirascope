import { useEffect } from "react";

interface TransparentFadeOptions {
  fadeStartDistance?: number; // Distance from top at which fading starts (in px)
  fadeEndDistance?: number; // Distance from top at which opacity reaches zero (in px)
  selector?: string; // CSS selector for elements to fade
}

/**
 * Hook to apply a gradient fade to elements as they approach the top of the viewport
 * Uses CSS masks to create a dynamic transparency gradient across the entire element
 *
 * @param options Configuration options for the transparent fade effect
 * @param options.fadeStartDistance Distance from top at which fading starts (default: 200px)
 * @param options.fadeEndDistance Distance from top at which opacity reaches zero (default: 100px)
 * @param options.selector CSS selector for elements to fade (default: '[data-gradient-fade]')
 */
export function useGradientFadeOnScroll({
  fadeStartDistance = 200,
  fadeEndDistance = 100,
  selector = "[data-gradient-fade]",
}: TransparentFadeOptions = {}) {
  useEffect(() => {
    // Function to update the mask gradient based on scroll position
    const updateElementMasks = () => {
      const elements = document.querySelectorAll<HTMLElement>(selector);

      // If no scroll has happened yet, ensure everything is fully visible
      if (window.scrollY === 0) {
        elements.forEach((element) => {
          element.style.maskImage = "none";
          element.style.webkitMaskImage = "none";
        });
        return;
      }

      // Update mask for each element based on scroll position
      elements.forEach((element) => {
        // Get custom fade settings
        const elementFadeStartDistance = parseFloat(
          element.dataset.fadeStartDistance || fadeStartDistance.toString(),
        );
        const elementFadeEndDistance = parseFloat(
          element.dataset.fadeEndDistance || fadeEndDistance.toString(),
        );

        const rect = element.getBoundingClientRect();
        const elementHeight = rect.height;

        // Calculate positions relative to the element
        let startFadePoint = 0;
        let endFadePoint = 0;

        if (rect.top <= elementFadeStartDistance) {
          // Element has entered the fade zone
          const viewportToStartDistance = elementFadeStartDistance - rect.top;
          const viewportToEndDistance = elementFadeEndDistance - rect.top;

          // Convert viewport positions to element-relative positions (0-100%)
          startFadePoint = Math.max(
            0,
            Math.min(100, (viewportToStartDistance / elementHeight) * 100),
          );
          endFadePoint = Math.max(
            0,
            Math.min(100, (viewportToEndDistance / elementHeight) * 100),
          );

          // Create a CSS gradient that:
          // - Makes content at endFadePoint and above completely transparent (opacity 0)
          // - Makes content at startFadePoint and below completely visible (opacity 1)
          // - Creates a gradient between these two points
          const maskGradient = `linear-gradient(
            to bottom,
            rgba(0,0,0,0) 0%,
            rgba(0,0,0,0) ${endFadePoint}%,
            rgba(0,0,0,1) ${startFadePoint}%,
            rgba(0,0,0,1) 100%
          )`;

          element.style.webkitMaskImage = maskGradient;
          element.style.maskImage = maskGradient;
          element.style.webkitMaskSize = "100% 100%";
          element.style.maskSize = "100% 100%";
        } else {
          // Element is above the fade zone, should be fully visible
          element.style.maskImage = "none";
          element.style.webkitMaskImage = "none";
        }
      });
    };

    // Throttle function to limit execution frequency
    const throttle = (callback: Function, limit: number) => {
      let waiting = false;
      return function () {
        if (!waiting) {
          callback();
          waiting = true;
          setTimeout(() => {
            waiting = false;
          }, limit);
        }
      };
    };

    // Create a throttled version of our update function (16ms ≈ 60fps)
    const throttledUpdate = throttle(updateElementMasks, 16);

    // Need to wait for DOM to be ready before initial calculation
    if (document.readyState === "complete") {
      updateElementMasks();
    } else {
      window.addEventListener("load", updateElementMasks);
    }

    // Add scroll event listener
    window.addEventListener("scroll", throttledUpdate);

    // Also update on resize since viewport dimensions might change
    window.addEventListener("resize", throttledUpdate);

    // Cleanup
    return () => {
      window.removeEventListener("scroll", throttledUpdate);
      window.removeEventListener("resize", throttledUpdate);
      window.removeEventListener("load", updateElementMasks);

      // Remove masks from all elements
      const elements = document.querySelectorAll<HTMLElement>(selector);
      elements.forEach((element) => {
        element.style.maskImage = "none";
        element.style.webkitMaskImage = "none";
      });
    };
  }, [fadeStartDistance, fadeEndDistance, selector]);
}

/**
 * Helper function to mark an element for transparent fading
 */
export function applyTransparentFade(
  element: HTMLElement | null,
  options: TransparentFadeOptions = {},
) {
  if (!element) return;

  // Default values
  const { fadeStartDistance = 200, fadeEndDistance = 100 } = options;

  // Mark element for the transparent fade handler
  element.dataset.gradientFade = "true";

  // Store custom fade values as data attributes
  element.dataset.fadeStartDistance = fadeStartDistance.toString();
  element.dataset.fadeEndDistance = fadeEndDistance.toString();
}
