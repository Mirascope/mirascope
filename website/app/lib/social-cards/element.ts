/**
 * Shared social card element creation
 *
 * This module contains only the element structure and constants,
 * with no Node.js-specific dependencies. It can be safely imported
 * in both browser and Node.js environments.
 */

/** Open Graph recommended dimensions (1200x630) */
export const CARD_WIDTH = 1200;
export const CARD_HEIGHT = 630;

/** Font size breakpoints based on title length */
const FONT_SIZE_BREAKPOINTS = [
  { maxChars: 13, fontSize: 152, label: "XS" },
  { maxChars: 27, fontSize: 128, label: "S" },
  { maxChars: 42, fontSize: 100, label: "SM" },
  { maxChars: 59, fontSize: 95, label: "M" },
  { maxChars: 80, fontSize: 75, label: "L" },
  { maxChars: Infinity, fontSize: 60, label: "XL" },
] as const;

export function getTitleFontSize(title: string): {
  fontSize: number;
  label: string;
} {
  // Satori renderer limitation: titles with no whitespace can't wrap and may
  // truncate, so use a fixed small font size to ensure they fit
  const hasWhitespace = /\s/.test(title);
  if (!hasWhitespace && title.length > 15) {
    return { fontSize: 50, label: "No Whitespace" };
  }

  const length = title.length;
  for (const { maxChars, fontSize, label } of FONT_SIZE_BREAKPOINTS) {
    if (length <= maxChars) {
      return { fontSize, label };
    }
  }
  return { fontSize: 60, label: "XL" };
}

/**
 * Create the social card element structure as a plain object
 * Satori accepts both React elements and plain object representations
 */
export function createSocialCardElement(
  title: string,
  logoDataUrl: string,
  backgroundDataUrl: string,
): Record<string, unknown> {
  return {
    type: "div",
    props: {
      style: {
        width: CARD_WIDTH,
        height: CARD_HEIGHT,
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        backgroundImage: `url(${backgroundDataUrl})`,
        backgroundSize: "cover",
        backgroundPosition: "center",
        position: "relative",
      },
      children: [
        // Logo positioned absolutely above the centered title
        {
          type: "img",
          props: {
            src: logoDataUrl,
            style: {
              position: "absolute",
              top: 50,
              left: "50%",
              transform: "translateX(-50%)",
              width: Math.round(1281 * 0.3),
              height: Math.round(294 * 0.3),
              objectFit: "contain",
            },
          },
        },
        // Title remains centered via flexbox
        {
          type: "div",
          props: {
            style: {
              // Box model
              maxWidth: "80%",
              paddingTop: 100,
              // Typography
              fontFamily: "Williams Handwriting, cursive",
              fontSize: getTitleFontSize(title).fontSize,
              lineHeight: title.length > 40 ? 1.3 : 1.2,
              color: "#ffffff",
              textAlign: "center",
              // Text wrapping
              overflowWrap: "break-word",
              hyphens: "auto",
              // Effects
              textShadow:
                "0 2px 6px rgba(0, 0, 0, 0.3), 0 4px 14px rgba(0, 0, 0, 0.2)",
            },
            children: title,
          },
        },
      ],
    },
  };
}
