#!/usr/bin/env bun
/**
 * Script to validate internal links and images in the prerendered HTML
 * This ensures all internal links point to valid routes and all images to valid files
 */
import fs from "fs";
import path from "path";
import { JSDOM } from "jsdom";
import { canonicalizePath } from "../src/lib/utils";
import { glob } from "glob";
import { colorize, printHeader, icons, coloredLog } from "./lib/terminal";
import { isHiddenRoute, getAllRoutes } from "@/src/lib/router-utils";
import llmMeta from "@/content/llms/_llms-meta";

interface ValidationResult {
  valid: boolean;
  brokenLinks: { page: string; link: string; text: string }[];
  brokenImages: { page: string; src: string; alt: string }[];
  disallowedAssets: string[]; // Paths to PNG images that should be WebP
  nonCanonicalLinks: { page: string; link: string; canonical: string; text: string }[];
}

/**
 * Known redirects that are handled by Cloudflare/hosting platform
 * These are intentional redirects and should not be treated as broken links
 */
const KNOWN_REDIRECTS = ["/discord-invite", "/slack-invite"];

/**
 * Parse sitemap.xml to extract all valid routes
 */
function parseSitemap(sitemapPath: string): Set<string> {
  const validRoutes = new Set<string>();

  if (!fs.existsSync(sitemapPath)) {
    console.warn(`⚠️  Sitemap not found at ${sitemapPath}, falling back to empty route set`);
    return validRoutes;
  }

  try {
    const sitemapContent = fs.readFileSync(sitemapPath, "utf-8");
    const dom = new JSDOM(sitemapContent, { contentType: "text/xml" });
    const urls = dom.window.document.querySelectorAll("url loc");

    urls.forEach((loc) => {
      const fullUrl = loc.textContent?.trim();
      if (fullUrl) {
        // Extract path from full URL (e.g., "https://mirascope.com/docs/test" -> "/docs/test")
        try {
          const url = new URL(fullUrl);
          const path = url.pathname;
          validRoutes.add(path);

          // Also add variants with/without trailing slash
          if (path !== "/" && path.endsWith("/")) {
            validRoutes.add(path.slice(0, -1));
          } else if (path !== "/") {
            validRoutes.add(path + "/");
          }
        } catch (e) {
          console.warn(`⚠️  Invalid URL in sitemap: ${fullUrl}`);
        }
      }
    });
  } catch (error) {
    console.warn(`⚠️  Error parsing sitemap: ${error}`);
  }

  return validRoutes;
}

async function validateLinksAndImages(
  distDir: string,
  verbose: boolean = false
): Promise<ValidationResult> {
  printHeader("Validating Internal Links and Images");

  // Parse sitemap.xml to get all valid routes
  // If distDir is process.cwd() (skip-dist-check mode), look in public directory
  const isSkipDistMode = path.resolve(distDir) === path.resolve(process.cwd());
  const sitemapPath = isSkipDistMode
    ? path.join(process.cwd(), "public", "sitemap.xml")
    : path.join(distDir, "sitemap.xml");

  const validRoutesSet = parseSitemap(sitemapPath);
  for (const route of getAllRoutes(true)) {
    if (isHiddenRoute(route)) {
      // Hidden routes will not be included in the sitemap, but they are still
      // okay to link to.
      validRoutesSet.add(route);
    }
  }
  llmMeta.forEach((llmDoc) => {
    if (llmDoc.route && isHiddenRoute(llmDoc.route)) {
      validRoutesSet.add(llmDoc.route);
      validRoutesSet.add(llmDoc.route + ".txt");
    }
  });

  if (verbose) {
    console.log(`Found ${validRoutesSet.size} valid routes`);
  }

  // Find all HTML files in the dist directory
  const htmlFiles = await glob(`${distDir}/**/*.html`);
  console.log(`${icons.info} Found ${htmlFiles.length} HTML files to check`);

  // Gather all assets in the dist directory
  const assetFiles = await glob(`${distDir}/assets/**/*.*`);
  const validAssetSet = new Set<string>();

  // Normalize asset paths for validation
  assetFiles.forEach((assetPath) => {
    // Convert to web path format (relative to dist directory)
    const webPath = "/" + path.relative(distDir, assetPath);
    validAssetSet.add(webPath);

    // Add WebP variants to valid assets set since they'll be generated during build
    if (![".svg", ".gif", ".webp"].includes(path.extname(assetPath).toLowerCase())) {
      const basePath = webPath.substring(0, webPath.lastIndexOf("."));
      validAssetSet.add(`${basePath}.webp`);
      validAssetSet.add(`${basePath}-medium.webp`);
      validAssetSet.add(`${basePath}-small.webp`);
    }
  });

  if (verbose) {
    console.log(`Found ${validAssetSet.size} valid assets in the site`);
  }

  const brokenLinks: { page: string; link: string; text: string }[] = [];
  const brokenImages: { page: string; src: string; alt: string }[] = [];
  const nonCanonicalLinks: { page: string; link: string; canonical: string; text: string }[] = [];
  let totalLinks = 0;
  let totalImages = 0;

  // Process each HTML file
  for (const htmlFile of htmlFiles) {
    const content = fs.readFileSync(htmlFile, "utf-8");
    const dom = new JSDOM(content);
    const links = dom.window.document.querySelectorAll("a[href^='/']");
    const images = dom.window.document.querySelectorAll("img[src^='/']");

    // Get the relative path for reporting
    const relativePath = path.relative(distDir, htmlFile);
    // Convert dist/some/path/index.html to /some/path or dist/page.html to /page
    const currentPage = "/" + relativePath.replace(/\/index\.html$/, "").replace(/\.html$/, "");

    if (verbose) {
      console.log(`Checking ${links.length} links and ${images.length} images in ${relativePath}`);
    }

    // Check each internal link
    links.forEach((link: Element) => {
      totalLinks++;
      const href = link.getAttribute("href") as string;

      // Skip anchor links to the same page
      if (href.startsWith("#")) {
        return;
      }

      // Parse the URL to handle query parameters and anchors
      let urlPath = href;
      try {
        // Handle absolute paths with host
        if (href.startsWith("/")) {
          urlPath = href.split("#")[0].split("?")[0];
        } else {
          const url = new URL(href, "https://example.com");
          urlPath = url.pathname;
        }
      } catch (e) {
        // If URL parsing fails, use the original href
        urlPath = href;
      }

      // Skip validation for known redirects
      if (KNOWN_REDIRECTS.includes(urlPath)) {
        return;
      }

      // First check if link uses canonical format
      const canonicalPath = canonicalizePath(urlPath);
      if (urlPath !== canonicalPath) {
        nonCanonicalLinks.push({
          page: currentPage,
          link: href,
          canonical: canonicalPath,
          text: link.textContent || "[No text]",
        });
      }

      // Then check if the canonical path is a valid route
      if (!validRoutesSet.has(canonicalPath)) {
        brokenLinks.push({
          page: currentPage,
          link: href,
          text: link.textContent || "[No text]",
        });
      }
    });

    // Check each internal image
    images.forEach((image: Element) => {
      totalImages++;
      const src = image.getAttribute("src") as string;
      const alt = image.getAttribute("alt") || "[No alt text]";

      // Skip data URLs
      if (src.startsWith("data:")) {
        return;
      }

      // Check if the image source exists in the asset files
      // ResponsiveImage component uses WebP versions, but we also need to check original sources
      const isValidImage = validAssetSet.has(src);

      if (!isValidImage) {
        brokenImages.push({
          page: currentPage,
          src,
          alt,
        });
      }
    });
  }

  // Output results for links
  let isValid = true;

  if (brokenLinks.length > 0) {
    isValid = false;
    coloredLog(`\n${icons.error} Found ${brokenLinks.length} broken internal links:`, "red");

    // Group by page for easier readability
    const byPage = brokenLinks.reduce(
      (acc, { page, link, text }) => {
        if (!acc[page]) acc[page] = [];
        acc[page].push({ link, text });
        return acc;
      },
      {} as Record<string, { link: string; text: string }[]>
    );

    Object.entries(byPage).forEach(([page, links]) => {
      console.log(`\n${colorize(`Page: ${page}`, "yellow")}`);
      links.forEach(({ link, text }) => {
        console.log(
          `  ${icons.arrow} ${colorize(link, "red")} (${text.substring(0, 30)}${text.length > 30 ? "..." : ""})`
        );
      });
    });
  } else {
    coloredLog(`\n${icons.success} All ${totalLinks} internal links are valid!`, "green");
  }

  // Output results for non-canonical links
  if (nonCanonicalLinks.length > 0) {
    coloredLog(
      `\n${icons.error} Found ${nonCanonicalLinks.length} links using non-canonical URLs:`,
      "yellow"
    );

    // Group by page for easier readability
    const byPage = nonCanonicalLinks.reduce(
      (acc, { page, link, canonical, text }) => {
        if (!acc[page]) acc[page] = [];
        acc[page].push({ link, canonical, text });
        return acc;
      },
      {} as Record<string, { link: string; canonical: string; text: string }[]>
    );

    Object.entries(byPage).forEach(([page, links]) => {
      console.log(`\n${colorize(`Page: ${page}`, "yellow")}`);
      links.forEach(({ link, canonical, text }) => {
        console.log(
          `  ${icons.arrow} ${colorize(link, "yellow")} should be ${colorize(canonical, "green")} (${text.substring(0, 30)}${text.length > 30 ? "..." : ""})`
        );
      });
    });

    coloredLog(
      `\nThese links will be automatically redirected, but should be updated to use canonical URLs.`,
      "cyan"
    );
  }

  // Output results for images
  if (brokenImages.length > 0) {
    isValid = false;
    coloredLog(`\n${icons.error} Found ${brokenImages.length} broken internal images:`, "red");

    // Group by page for easier readability
    const byPage = brokenImages.reduce(
      (acc, { page, src, alt }) => {
        if (!acc[page]) acc[page] = [];
        acc[page].push({ src, alt });
        return acc;
      },
      {} as Record<string, { src: string; alt: string }[]>
    );

    Object.entries(byPage).forEach(([page, images]) => {
      console.log(`\n${colorize(`Page: ${page}`, "yellow")}`);
      images.forEach(({ src, alt }) => {
        console.log(
          `  ${icons.arrow} ${colorize(src, "red")} (${alt.substring(0, 30)}${alt.length > 30 ? "..." : ""})`
        );
      });
    });
  } else {
    coloredLog(`\n${icons.success} All ${totalImages} internal images are valid!`, "green");
  }

  // Check for PNG files in the source public directory that should be WebP
  const disallowedAssets: string[] = [];
  const sourceAssetsDir = path.join(process.cwd(), "public/assets");

  // Find all PNG/JPG images in the source directory
  const pngFiles = await glob(`${sourceAssetsDir}/**/*.{png,jpg,jpeg}`, { absolute: true });

  // Add all found PNG/JPG files to disallowed assets
  for (const pngFile of pngFiles) {
    // Get the relative path for reporting
    const relativePath = path.relative(process.cwd(), pngFile);
    disallowedAssets.push(relativePath);
  }

  // Output results for disallowed assets
  if (disallowedAssets.length > 0) {
    isValid = false;
    coloredLog(
      `\n${icons.error} Found ${disallowedAssets.length} PNG/JPG images that should be converted to WebP:`,
      "red"
    );

    disallowedAssets.forEach((assetPath) => {
      console.log(`  ${icons.arrow} ${colorize(assetPath, "red")}`);
    });

    coloredLog(
      `\nPlease run 'bun run convert-to-webp' to convert these images to WebP format.`,
      "yellow"
    );
  } else {
    coloredLog(`\n${icons.success} No disallowed image formats found in source assets!`, "green");
  }

  return {
    valid: isValid,
    brokenLinks,
    brokenImages,
    disallowedAssets,
    nonCanonicalLinks,
  };
}

// When run directly
async function main() {
  const args = process.argv.slice(2);
  const verbose = args.includes("--verbose");
  const ignoreDisallowed = args.includes("--ignore-disallowed");
  const distDir = path.join(process.cwd(), "dist");
  const skipDistCheck = args.includes("--skip-dist-check");

  // Check if dist directory exists (unless skipped)
  if (!skipDistCheck && !fs.existsSync(distDir)) {
    coloredLog(`${icons.error} Dist directory not found! Run \`bun run build\` first.`, "red");
    coloredLog(
      `To validate source assets only, use \`bun run validate-assets --skip-dist-check\``,
      "yellow"
    );
    process.exit(1);
  }

  try {
    const result = await validateLinksAndImages(skipDistCheck ? process.cwd() : distDir, verbose);

    // Determine if we should fail the validation
    let shouldFail = false;

    // Always fail on broken links or images
    if (
      result.brokenLinks.length > 0 ||
      result.brokenImages.length > 0 ||
      result.nonCanonicalLinks.length > 0
    ) {
      shouldFail = true;
    }

    // Only fail on disallowed assets if not ignored
    if (!ignoreDisallowed && result.disallowedAssets.length > 0) {
      shouldFail = true;
      coloredLog(`\nTo convert PNG/JPG to WebP: \`bun run convert-to-webp\``, "cyan");
      coloredLog(`To ignore this check: \`bun run validate-assets --ignore-disallowed\``, "cyan");
    }

    if (shouldFail) {
      process.exit(1);
    }
  } catch (error) {
    coloredLog(`${icons.error} Error validating assets:`, "red");
    console.error(error);
    process.exit(1);
  }
}

// Run the script if invoked directly
if (import.meta.path === Bun.main) {
  await main();
}

// Export for use in other scripts
export { validateLinksAndImages };
