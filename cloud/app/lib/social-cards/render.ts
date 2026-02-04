/**
 * Social card render pipeline (Node.js)
 *
 * Converts JSX templates to WebP images using:
 * 1. Satori - JSX to SVG
 * 2. resvg-js - SVG to PNG
 * 3. Sharp - PNG to WebP
 */

import { Resvg } from "@resvg/resvg-js";
import fs from "node:fs/promises";
import path from "node:path";
import satori from "satori";
import sharp from "sharp";

import { CARD_WIDTH, CARD_HEIGHT, createSocialCardElement } from "./element";

// Re-export for backwards compatibility
export { CARD_WIDTH, CARD_HEIGHT, createSocialCardElement };

/**
 * Cached assets loaded once at module level
 */
let fontData: ArrayBuffer | null = null;
let logoDataUrl: string | null = null;
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
      "public/assets/social-cards/background.png",
    );
    const buffer = await fs.readFile(imgPath);
    backgroundDataUrl = `data:image/png;base64,${buffer.toString("base64")}`;
  }
  return backgroundDataUrl;
}

async function loadLogoImage(): Promise<string> {
  if (!logoDataUrl) {
    const imgPath = path.resolve(
      process.cwd(),
      "public/assets/social-cards/logo.png",
    );
    const buffer = await fs.readFile(imgPath);
    logoDataUrl = `data:image/png;base64,${buffer.toString("base64")}`;
  }
  return logoDataUrl;
}

/**
 * Load all required assets (font and background)
 * Called once before generating multiple cards
 */
export async function loadAssets(): Promise<{
  font: ArrayBuffer;
  logo: string;
  background: string;
}> {
  const [font, logo, background] = await Promise.all([
    loadFont(),
    loadLogoImage(),
    loadBackgroundImage(),
  ]);
  return { font, logo, background };
}

/**
 * Render a social card element to PNG buffer
 * Common pipeline: Satori (Element -> SVG) -> resvg (SVG -> PNG)
 */
async function renderElementToPng(
  element: Record<string, unknown>,
  font: ArrayBuffer,
): Promise<Buffer> {
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
        data: font,
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
  return resvg.render().asPng();
}

/**
 * Render a social card to PNG buffer (for preview)
 *
 * @param title - The page title to display on the card
 * @param assets - Pre-loaded font and background assets
 * @returns PNG image as Buffer
 */
export async function renderSocialCardAsPng(
  title: string,
  assets: { font: ArrayBuffer; logo: string; background: string },
): Promise<Buffer> {
  const element = createSocialCardElement(
    title,
    assets.logo,
    assets.background,
  );
  return renderElementToPng(element, assets.font);
}

/**
 * Render a social card to WebP buffer (for production)
 *
 * @param title - The page title to display on the card
 * @param assets - Pre-loaded font and background assets
 * @param quality - WebP quality (0-100)
 * @returns WebP image as Buffer
 */
export async function renderSocialCard(
  title: string,
  assets: { font: ArrayBuffer; logo: string; background: string },
  quality = 85,
): Promise<Buffer> {
  const element = createSocialCardElement(
    title,
    assets.logo,
    assets.background,
  );
  const pngBuffer = await renderElementToPng(element, assets.font);
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
