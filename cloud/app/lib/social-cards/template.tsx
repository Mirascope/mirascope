/**
 * Social card template for Satori rendering
 *
 * This component is rendered by Satori to generate SVG,
 * which is then converted to PNG and WebP.
 *
 * Note: Satori requires inline styles (no external CSS/Tailwind).
 * All styles must be specified as React CSSProperties objects.
 */

import type { ReactNode } from "react";
import type { SocialCardProps } from "./types";

/**
 * Social card dimensions (standard OG image size)
 */
export const CARD_WIDTH = 1200;
export const CARD_HEIGHT = 630;

/**
 * Social card template component
 *
 * Renders a title over the light background image from the homepage.
 * Uses Williams Handwriting font for brand consistency.
 */
export function SocialCardTemplate({
  title,
  backgroundImage,
}: SocialCardProps): ReactNode {
  // Minimal template for Satori compatibility
  return (
    <div
      style={{
        width: CARD_WIDTH,
        height: CARD_HEIGHT,
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        backgroundColor: "#f0f0f0",
      }}
    >
      {/* Background image */}
      <img
        src={backgroundImage}
        width={CARD_WIDTH}
        height={CARD_HEIGHT}
        style={{
          position: "absolute",
          top: 0,
          left: 0,
        }}
      />
      {/* Title text */}
      <div
        style={{
          fontFamily: "Williams Handwriting",
          fontSize: 72,
          color: "#1a1a2e",
          textAlign: "center",
          padding: 60,
        }}
      >
        {title}
      </div>
    </div>
  );
}
