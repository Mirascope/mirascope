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
              fontFamily: "Williams Handwriting",
              fontSize: 68,
              color: "#ffffff",
              textAlign: "center",
              lineHeight: 1.3,
              maxWidth: "80%",
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
