import DOMPurify from "dompurify";
import mermaid, { type MermaidConfig } from "mermaid";
import { useEffect, useRef, useState } from "react";

import LoadingContent from "@/app/components/blocks/loading-content";

import styles from "./mermaid-diagram.module.css";

interface MermaidDiagramProps {
  chart: string;
  className?: string;
}

type ThemeName = "dark" | "default";

/**
 * Renders mermaid diagrams in MDX content
 */
export default function MermaidDiagram({
  chart,
  className = "",
}: MermaidDiagramProps) {
  const [svgContent, setSvgContent] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const mermaidRef = useRef<HTMLDivElement>(null);
  const uniqueId = useRef(
    `mermaid-${Math.random().toString(36).substring(2, 11)}`,
  );
  const themeRef = useRef<ThemeName>(getThemeConfig());

  // Determine which theme config to use based on current theme
  function getThemeConfig(): ThemeName {
    if (typeof window === "undefined" || typeof document === "undefined") {
      return "default"; // Server-side rendering, use default theme
    }
    if (document.documentElement.classList.contains("dark")) {
      return "dark";
    } else {
      return "default";
    }
  }

  // Custom theme configuration
  function getThemeOptions(themeName: ThemeName): MermaidConfig {
    const baseConfig: MermaidConfig = {
      startOnLoad: false,
      securityLevel: "strict",
      fontFamily: "inherit",
    };

    if (themeName === "dark") {
      return {
        ...baseConfig,
        theme: "dark",
      };
    } else {
      // Default light theme
      return {
        ...baseConfig,
        theme: "default",
      };
    }
  }

  const renderDiagram = async () => {
    if (!chart) return;

    try {
      // Get current theme and update theme reference
      const currentTheme = getThemeConfig();
      themeRef.current = currentTheme;

      // Initialize mermaid with theme-specific configuration
      mermaid.initialize(getThemeOptions(currentTheme));

      // Reset svg content to force re-rendering
      setSvgContent(null);

      // Use a new ID for each render to avoid caching issues
      const renderId = `${uniqueId.current}-${Date.now()}`;
      const { svg } = await mermaid.render(renderId, chart);
      // Sanitize SVG output to prevent XSS attacks
      // Allow foreignObject and its HTML contents (needed for mermaid labels)
      const sanitizedSvg = DOMPurify.sanitize(svg, {
        USE_PROFILES: { svg: true, svgFilters: true },
        ADD_TAGS: ["foreignObject", "p"],
        ADD_ATTR: ["requiredFeatures", "dominant-baseline"],
      });
      setSvgContent(sanitizedSvg);
      setError(null);
    } catch (err) {
      console.error("Mermaid rendering error:", err);
      setError(
        `Failed to render diagram: ${err instanceof Error ? err.message : String(err)}`,
      );
    }
  };

  // Initial render
  useEffect(() => {
    void renderDiagram();
  }, [chart]);

  // Listen for theme changes
  useEffect(() => {
    const handleThemeChange = () => {
      const currentTheme = getThemeConfig();

      // Only re-render if theme actually changed
      if (themeRef.current !== currentTheme) {
        themeRef.current = currentTheme;
        void renderDiagram();
      }
    };

    // Use MutationObserver to detect theme changes
    const observer = new MutationObserver((mutations) => {
      for (const mutation of mutations) {
        if (
          mutation.type === "attributes" &&
          mutation.attributeName === "class"
        ) {
          handleThemeChange();
          break;
        }
      }
    });

    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["class"],
    });

    return () => observer.disconnect();
  }, [chart]);

  if (error) {
    return (
      <div className="bg-destructive/10 border-destructive/20 text-destructive rounded-md border p-4">
        <p className="font-medium">Diagram Error</p>
        <p className="font-mono text-sm whitespace-pre-wrap">{error}</p>
      </div>
    );
  }

  return (
    <div
      className={`mermaid-diagram ${styles.mermaidWrapper} ${className}`}
      ref={mermaidRef}
    >
      {svgContent ? (
        <div dangerouslySetInnerHTML={{ __html: svgContent }} />
      ) : (
        <LoadingContent spinnerClassName="h-12 w-12" fullHeight={false} />
      )}
    </div>
  );
}
