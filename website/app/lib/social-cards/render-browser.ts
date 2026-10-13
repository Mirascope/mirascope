/**
 * Browser-compatible social card preview renderer
 *
 * Uses satori to render social cards as SVG in the browser.
 * This is a lightweight alternative (~200KB) that doesn't require WASM.
 * The SVG output matches the production render pipeline closely.
 */

import satori from "satori";

import { CARD_WIDTH, CARD_HEIGHT, createSocialCardElement } from "./element";

/** Cached assets for browser rendering */
let cachedFont: ArrayBuffer | null = null;
let cachedLogo: string | null = null;
let cachedBackground: string | null = null;

/**
 * Load assets for browser rendering using fetch()
 */
export async function loadAssetsBrowser(): Promise<{
  font: ArrayBuffer;
  logo: string;
  background: string;
}> {
  const [font, logo, background] = await Promise.all([
    cachedFont ??
      fetch("/fonts/Williams-Handwriting-Regular-v1.ttf").then((r) =>
        r.arrayBuffer(),
      ),
    cachedLogo ?? fetchAsDataUrl("/assets/social-cards/logo.png"),
    cachedBackground ?? fetchAsDataUrl("/assets/social-cards/background.png"),
  ]);

  cachedFont = font;
  cachedLogo = logo;
  cachedBackground = background;

  return { font, logo, background };
}

/**
 * Fetch an image and convert to base64 data URL
 */
async function fetchAsDataUrl(url: string): Promise<string> {
  const response = await fetch(url);
  const blob = await response.blob();
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => resolve(reader.result as string);
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}

/**
 * Render a social card to SVG string (browser-compatible)
 *
 * @param title - The page title to display on the card
 * @param assets - Pre-loaded font and background assets
 * @returns SVG string
 */
export async function renderSocialCardToSvg(
  title: string,
  assets: { font: ArrayBuffer; logo: string; background: string },
): Promise<string> {
  const element = createSocialCardElement(
    title,
    assets.logo,
    assets.background,
  );

  /* eslint-disable @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-argument */
  return satori(element as any, {
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
}

/**
 * Render a social card to SVG data URL (for use in img src)
 */
export async function renderSocialCardToDataUrl(
  title: string,
  assets: { font: ArrayBuffer; logo: string; background: string },
): Promise<string> {
  const svg = await renderSocialCardToSvg(title, assets);
  return `data:image/svg+xml;base64,${btoa(unescape(encodeURIComponent(svg)))}`;
}
