/**
 * Social card render pipeline
 *
 * Converts JSX templates to WebP images using:
 * 1. Satori - JSX to SVG
 * 2. resvg-js - SVG to PNG
 * 3. Sharp - PNG to WebP
 */

import satori from "satori";
import { Resvg } from "@resvg/resvg-js";
import sharp from "sharp";
import fs from "node:fs/promises";
import path from "node:path";

import { CARD_WIDTH, CARD_HEIGHT } from "./template";

/**
 * Cached assets loaded once at module level
 */
let fontData: ArrayBuffer | null = null;
let backgroundDataUrl: string | null = null;

/**
 * Load the Williams Handwriting font from public/fonts/
 * Returns ArrayBuffer as required by Satori
 */
async function loadFont(): Promise<ArrayBuffer> {
  if (!fontData) {
    const fontPath = path.resolve(
      process.cwd(),
      "public/fonts/Williams-Handwriting-Regular-v1.ttf",
    );
    const buffer = await fs.readFile(fontPath);
    // Convert Node.js Buffer to ArrayBuffer for Satori
    fontData = buffer.buffer.slice(
      buffer.byteOffset,
      buffer.byteOffset + buffer.byteLength,
    );
  }
  return fontData;
}

/**
 * Load the light background image and convert to base64 data URL
 */
async function loadBackgroundImage(): Promise<string> {
  if (!backgroundDataUrl) {
    const imgPath = path.resolve(
      process.cwd(),
      "public/assets/backgrounds/light.webp",
    );
    const buffer = await fs.readFile(imgPath);
    backgroundDataUrl = `data:image/webp;base64,${buffer.toString("base64")}`;
  }
  return backgroundDataUrl;
}

/**
 * Load all required assets (font and background)
 * Called once before generating multiple cards
 */
export async function loadAssets(): Promise<{
  font: ArrayBuffer;
  background: string;
}> {
  const [font, background] = await Promise.all([
    loadFont(),
    loadBackgroundImage(),
  ]);
  return { font, background };
}

/**
 * Render a social card to WebP buffer
 *
 * @param title - The page title to display on the card
 * @param assets - Pre-loaded font and background assets
 * @param quality - WebP quality (0-100)
 * @returns WebP image as Buffer
 */
/**
 * Create the social card element structure as a plain object
 * Satori accepts both React elements and plain object representations
 *
 * Note: Uses a light gradient background instead of the watercolor image
 * because Satori has issues with children arrays containing images.
 * TODO: Investigate using background-image CSS property or alternative approach.
 */
function createSocialCardElement(title: string): Record<string, unknown> {
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
        // Light watercolor-inspired gradient background
        background:
          "linear-gradient(135deg, #f5f7fa 0%, #e4e9f2 50%, #d4dbe6 100%)",
        padding: 60,
      },
      children: {
        type: "div",
        props: {
          style: {
            fontFamily: "Williams Handwriting",
            fontSize: 72,
            color: "#1a1a2e",
            textAlign: "center",
            lineHeight: 1.3,
            maxWidth: "90%",
          },
          children: title,
        },
      },
    },
  };
}

export async function renderSocialCard(
  title: string,
  assets: { font: ArrayBuffer; background: string },
  quality = 85,
): Promise<Buffer> {
  // Create element as plain object (Satori accepts both React and plain objects)
  const element = createSocialCardElement(title);

  // 1. Satori: Element -> SVG string
  // Note: Satori accepts both React elements and plain object representations
  // We use plain objects to avoid JSX transformation issues in build pipeline
  /* eslint-disable @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-argument */
  const svg = await satori(element as any, {
    width: CARD_WIDTH,
    height: CARD_HEIGHT,
    fonts: [
      {
        name: "Williams Handwriting",
        data: assets.font,
        weight: 400,
        style: "normal",
      },
    ],
  });
  /* eslint-enable @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-argument */

  // 2. resvg: SVG -> PNG buffer
  const resvg = new Resvg(svg, {
    fitTo: {
      mode: "width",
      value: CARD_WIDTH,
    },
  });
  const pngData = resvg.render();
  const pngBuffer = pngData.asPng();

  // 3. Sharp: PNG -> WebP buffer
  return sharp(pngBuffer).webp({ quality }).toBuffer();
}

/**
 * Clear cached assets (useful for testing)
 */
export function clearAssetCache(): void {
  fontData = null;
  backgroundDataUrl = null;
}
