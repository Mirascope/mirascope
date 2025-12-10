import React from "react";

import {
  StorybookThemeProvider,
  ProductProvider,
  type Theme,
} from "@/src/components/core/providers";
import type { Product } from "@/src/lib/content/spec";

interface ProductThemeDecoratorProps {
  children: React.ReactNode;
  product?: Product;
  theme?: "light" | "dark";
  isLandingPage?: boolean;
}

/**
 * A decorator that applies the specified product theme and color theme to its children
 *
 * Note: Instead of manipulating the document root (which doesn't work well with
 * Storybook's iframe-based rendering), we apply classes directly to our container.
 */
export const ProductThemeDecorator = ({
  children,
  product = { name: "mirascope" },
  theme = "light",
  isLandingPage = false,
}: ProductThemeDecoratorProps) => {
  // Standard style for component theming
  const baseStyle = {
    padding: "1rem",
    width: "100%",
    height: "100%",
    minHeight: "50px",
    background: "var(--color-background)",
    color: "var(--color-foreground)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  };

  // Landing page background style
  const landingPageStyle = {
    padding: "1.5rem",
    width: "100%",
    height: "100%",
    minHeight: "50px",
    background: theme === "dark" ? "#6366f1" : "#f5f5f5",
    backgroundImage: `url(/assets/backgrounds/${theme}.png)`,
    backgroundSize: "cover",
    backgroundPosition: "center",
    color: "white",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  };

  // Choose style based on isLandingPage flag
  const style = isLandingPage ? landingPageStyle : baseStyle;

  return (
    <StorybookThemeProvider
      initialTheme={theme as Theme}
      initialCurrent={theme}
      isLandingPage={isLandingPage}
    >
      <ProductProvider product={product}>
        {/* Add watercolor background for landing pages, just like in __root.tsx */}
        {isLandingPage && <div className="watercolor-bg"></div>}

        <div
          className={theme}
          style={style as React.CSSProperties}
          data-landing-page={isLandingPage ? "true" : undefined}
        >
          {children}
        </div>
      </ProductProvider>
    </StorybookThemeProvider>
  );
};

/**
 * Storybook decorator that applies product theme and color theme
 * @param product The product theme to apply
 * @param theme Light or dark theme
 * @param isLandingPage Whether to apply landing page styling
 */
export const withProductTheme =
  (
    product: Product = { name: "mirascope" },
    theme: "light" | "dark" = "light",
    isLandingPage = false
  ) =>
  (Story: any) => {
    return (
      <ProductThemeDecorator product={product} theme={theme} isLandingPage={isLandingPage}>
        <Story />
      </ProductThemeDecorator>
    );
  };
