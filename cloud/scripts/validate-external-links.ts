#!/usr/bin/env bun
/**
 * Script to validate external links in the prerendered HTML
 * This ensures external links don't lead to 404s or other errors
 */
import fs from "fs";
import path from "path";
import { JSDOM } from "jsdom";
import { glob } from "glob";
import { colorize, printHeader, icons, coloredLog } from "./lib/terminal";

interface LinkCheckResult {
  url: string;
  status: number | null;
  error?: string;
  retries?: number;
  redirectUrl?: string;
  pageFound: string[];
}

interface ValidationResult {
  valid: boolean;
  nLinksChecked: number;
  brokenLinks: LinkCheckResult[];
  redirectedLinks: LinkCheckResult[];
}

// Cache to avoid checking the same URL multiple times
const linkCache = new Map<string, LinkCheckResult>();

// Default timeout for requests (5 seconds)
const DEFAULT_TIMEOUT = 5000;

// Maximum retry attempts for timeouts and certain errors
const MAX_RETRIES = 3;

// Exponential backoff base (ms) for retries
const RETRY_BACKOFF_BASE = 1000;

// Rate limiting: wait this many ms between requests to the same domain
const RATE_LIMIT_MS = 1000;
const domainLastAccessed = new Map<string, number>();

// Domain allowlist - domains we know are valid but might block our requests
const URL_ALLOWLIST = new Set([
  "https://www.linkedin.com/in/wbakst/",
  "https://twitter.com/WilliamBakst",
  "https://www.uber.com/en-GB/blog/generative-ai-for-high-quality-mobile-testing/",
  "https://openai.com/*",
  "https://platform.openai.com/*",
  "https://direct.mit.edu/tacl/article/doi/10.1162/tacl_a_00324/96460/How-Can-We-Know-What-Language-Models-Know",

  // If needed, allowlist domains that we know are valid but block requests
]);

/**
 * Check if a URL matches any entry in the allowlist, supporting wildcards
 * @param url The URL to check
 * @param allowlist The set of allowlisted URLs (may contain wildcards with *)
 * @returns boolean indicating if the URL is allowlisted
 */
function isUrlAllowlisted(url: string, allowlist: Set<string>): boolean {
  // First check for exact match
  if (allowlist.has(url)) {
    return true;
  }

  // Then check for wildcard patterns
  for (const pattern of allowlist) {
    if (pattern.includes("*")) {
      // Convert the wildcard pattern to a regex
      const regexPattern = pattern
        .replace(/[-[\]{}()+?.,\\^$|#\s]/g, "\\$&") // Escape special regex chars except *
        .replace(/\*/g, ".*"); // Convert * to regex .*

      const regex = new RegExp(`^${regexPattern}$`);
      if (regex.test(url)) {
        return true;
      }
    }
  }

  return false;
}

/**
 * Check if a URL is reachable with retry logic
 * @param url The URL to check
 * @param timeout Timeout in milliseconds
 * @param retryCount Current retry attempt (used internally for recursion)
 */
async function checkUrl(
  url: string,
  timeout = DEFAULT_TIMEOUT,
  retryCount = 0
): Promise<Omit<LinkCheckResult, "pageFound">> {
  try {
    // Parse the URL to get the domain for rate limiting
    const parsedUrl = new URL(url);
    const domain = parsedUrl.hostname;

    // Check if URL matches any entry in the allowlist (including wildcards)
    if (isUrlAllowlisted(url, URL_ALLOWLIST)) {
      return { url, status: 200 }; // Assume it's valid
    }

    // Apply rate limiting
    const now = Date.now();
    const lastAccessed = domainLastAccessed.get(domain) || 0;
    const timeSinceLastAccess = now - lastAccessed;

    if (timeSinceLastAccess < RATE_LIMIT_MS) {
      // Wait to respect rate limit
      await new Promise((resolve) => setTimeout(resolve, RATE_LIMIT_MS - timeSinceLastAccess));
    }

    // Update last accessed time
    domainLastAccessed.set(domain, Date.now());

    // Use HEAD request to avoid downloading the full page
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
      const response = await fetch(url, {
        method: "HEAD",
        redirect: "follow",
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      // Track redirects by comparing final URL with original URL
      const redirectUrl = response.url !== url ? response.url : undefined;

      return { url, status: response.status, redirectUrl };
    } catch (e: any) {
      // If HEAD request fails, try a GET (some servers don't support HEAD)
      if (e.name === "AbortError") {
        throw new Error("Request timeout");
      }

      // Try with GET request as fallback
      const getController = new AbortController();
      const getTimeoutId = setTimeout(() => getController.abort(), timeout);

      try {
        const response = await fetch(url, {
          method: "GET",
          redirect: "follow",
          signal: getController.signal,
        });

        clearTimeout(getTimeoutId);

        // Track redirects by comparing final URL with original URL
        const redirectUrl = response.url !== url ? response.url : undefined;

        return { url, status: response.status, redirectUrl };
      } catch (getError: any) {
        clearTimeout(getTimeoutId);
        throw getError;
      }
    }
  } catch (error: any) {
    // Implement retry logic for timeouts and certain temporary errors
    const isTimeout = error.message === "Request timeout" || error.name === "AbortError";
    const isNetworkError =
      error.message?.includes("fetch failed") ||
      error.message?.includes("network") ||
      error.message?.includes("ECONNREFUSED") ||
      error.message?.includes("ETIMEDOUT");

    if ((isTimeout || isNetworkError) && retryCount < MAX_RETRIES) {
      // Calculate exponential backoff delay
      const backoffDelay = RETRY_BACKOFF_BASE * Math.pow(2, retryCount);

      // Log retry attempt
      console.log(
        `Retrying ${url} (attempt ${retryCount + 1}/${MAX_RETRIES}) after ${backoffDelay}ms delay...`
      );

      // Wait for backoff period
      await new Promise((resolve) => setTimeout(resolve, backoffDelay));

      // Retry with incremented counter and longer timeout
      return checkUrl(url, timeout * 1.5, retryCount + 1);
    }

    return {
      url,
      status: null,
      error: error.message || "Unknown error",
      retries: retryCount,
    };
  }
}

async function validateExternalLinks(
  distDir: string,
  verbose: boolean = false,
  concurrentRequests: number = 5
): Promise<ValidationResult> {
  printHeader("Validating External Links");

  // Find all HTML files in the dist directory
  const htmlFiles = await glob(`${distDir}/**/index.html`);
  console.log(`${icons.info} Found ${htmlFiles.length} HTML files to check`);

  // Collect all external links
  const externalLinks = new Map<string, string[]>();

  // Process each HTML file to collect external links
  for (const htmlFile of htmlFiles) {
    const content = fs.readFileSync(htmlFile, "utf-8");
    const dom = new JSDOM(content);
    const links = dom.window.document.querySelectorAll("a[href]");

    // Get the relative path for reporting
    const relativePath = path.relative(distDir, htmlFile);
    // Convert dist/some/path/index.html to /some/path
    const currentPage = "/" + relativePath.replace(/\/index\.html$/, "");

    // Check each link
    links.forEach((link: Element) => {
      const href = link.getAttribute("href") as string;

      // Skip internal links (those starting with /)
      if (href.startsWith("/") || href.startsWith("#")) {
        return;
      }

      // Skip non-http(s) links like mailto:, tel:, etc.
      if (!href.startsWith("http://") && !href.startsWith("https://")) {
        return;
      }

      // Add to the external links map
      if (!externalLinks.has(href)) {
        externalLinks.set(href, []);
      }
      externalLinks.get(href)?.push(currentPage);
    });
  }

  if (verbose) {
    console.log(`Found ${externalLinks.size} unique external links to check`);
  }

  // Create a worker pool for parallel processing
  const results: LinkCheckResult[] = [];
  const urlsToCheck = Array.from(externalLinks.keys());
  let processed = 0;
  let running = 0;
  let index = 0;

  // Create a synchronized counter for progress tracking
  const incrementProcessed = () => {
    processed++;
    if (processed % 10 === 0 || processed === urlsToCheck.length) {
      console.log(`[${processed}/${urlsToCheck.length}] Checked ${processed} links...`);
    }
  };

  // Process a single URL and return its result
  const processUrl = async (url: string): Promise<LinkCheckResult> => {
    // Check if we've already seen this URL
    if (linkCache.has(url)) {
      const cachedResult = linkCache.get(url)!;
      incrementProcessed();
      return {
        ...cachedResult,
        pageFound: externalLinks.get(url) || [],
      };
    }

    try {
      const result = await checkUrl(url);
      incrementProcessed();

      if (verbose || result.status === null || result.status >= 400) {
        const status = result.status ? result.status : "Error";
        const message = result.error ? `: ${result.error}` : "";
        const retryInfo = result.retries ? ` (after ${result.retries} retries)` : "";
        console.log(
          `[${processed}/${urlsToCheck.length}] ${url} - ${status}${message}${retryInfo}`
        );
      }

      // Cache the result
      linkCache.set(url, { ...result, pageFound: [] });

      return {
        ...result,
        pageFound: externalLinks.get(url) || [],
      };
    } catch (error: any) {
      console.error(`Error checking ${url}:`, error);
      incrementProcessed();

      const result = {
        url,
        status: null,
        error: error.message || "Unknown error",
        pageFound: externalLinks.get(url) || [],
      };

      // Cache the error result
      linkCache.set(url, { ...result, pageFound: [] });

      return result;
    }
  };

  // Process URLs with true parallelism
  const runNextWorker = async () => {
    if (index >= urlsToCheck.length) return;

    const url = urlsToCheck[index++];
    running++;

    try {
      const result = await processUrl(url);
      results.push(result);
    } catch (e) {
      console.error(`Worker error processing ${url}:`, e);
    }

    running--;
    await runNextWorker();
  };

  // Start workers up to concurrency limit
  const workers: Promise<void>[] = [];
  for (let i = 0; i < concurrentRequests; i++) {
    workers.push(runNextWorker());
  }

  // Wait for all workers to complete
  await Promise.all(workers);

  // Filter broken links (status >= 400 or errors)
  const brokenLinks = results.filter((result) => result.status === null || result.status >= 400);

  // Find redirected links
  const redirectedLinks = results.filter(
    (result) => result.redirectUrl && result.status && result.status < 400
  );

  // Console output for redirects
  if (redirectedLinks.length > 0) {
    coloredLog(`\n${icons.info} Found ${redirectedLinks.length} redirected links:`, "blue");

    redirectedLinks.forEach(({ url, redirectUrl, pageFound }) => {
      console.log(`${icons.arrow} ${url}`);
      console.log(`  ${icons.success} Redirects to: ${colorize(redirectUrl || "", "green")}`);
      if (pageFound.length > 0) {
        console.log(
          `  ${icons.dot} Found on: ${pageFound.length > 1 ? pageFound.length + " pages" : pageFound[0]}`
        );
      }
    });
  }

  // Console output for broken links
  if (brokenLinks.length > 0) {
    coloredLog(`\n${icons.error} Found ${brokenLinks.length} broken external links:`, "red");

    // Group by status code for easier readability
    const byStatus = brokenLinks.reduce(
      (acc, link) => {
        const key = link.status ? `Status ${link.status}` : `Error: ${link.error}`;
        if (!acc[key]) acc[key] = [];
        acc[key].push(link);
        return acc;
      },
      {} as Record<string, LinkCheckResult[]>
    );

    Object.entries(byStatus).forEach(([status, links]) => {
      console.log(`\n${colorize(`${status}:`, "yellow")}`);
      links.forEach(({ url, pageFound }) => {
        console.log(`  ${icons.arrow} ${colorize(url, "red")}`);
        pageFound.forEach((page) => {
          console.log(`    ${icons.dot} Found on: ${page}`);
        });
      });
    });
  }

  // Create a combined JSON report with all link data
  const jsonReportPath = path.join(process.cwd(), "links-report.json");
  fs.writeFileSync(
    jsonReportPath,
    JSON.stringify(
      {
        date: new Date().toISOString(),
        totalChecked: results.length,
        brokenLinks,
        redirectedLinks,
      },
      null,
      2
    )
  );
  console.log(`\nDetailed JSON report saved to: ${jsonReportPath}`);

  // Create a combined markdown report
  const mdReportPath = path.join(process.cwd(), "links-report.md");
  const mdReport = generateMarkdownReport(brokenLinks, redirectedLinks, results.length);
  fs.writeFileSync(mdReportPath, mdReport);
  console.log(`Markdown report saved to: ${mdReportPath}`);

  if (brokenLinks.length > 0) {
    return {
      valid: false,
      nLinksChecked: results.length,
      brokenLinks,
      redirectedLinks,
    };
  } else {
    coloredLog(`\n${icons.success} All links validated, no broken links found!`, "green");
    return {
      valid: true,
      nLinksChecked: results.length,
      brokenLinks: [],
      redirectedLinks,
    };
  }
}

/**
 * Generate a combined markdown report with both broken and redirected links
 */
function generateMarkdownReport(
  brokenLinks: LinkCheckResult[],
  redirectedLinks: LinkCheckResult[],
  totalChecked: number
): string {
  const date = new Date().toISOString().split("T")[0];
  let report = `# Link Validation Report - ${date}\n\n`;

  // Summary section
  report += `## Summary\n`;
  report += `- Total links checked: ${totalChecked}\n`;
  report += `- Broken links found: ${brokenLinks.length}\n`;
  report += `- Redirected links found: ${redirectedLinks.length}\n\n`;

  // Broken links section
  if (brokenLinks.length > 0) {
    report += `## Broken Links\n\n`;

    // Group by status code or error type
    const byStatus = brokenLinks.reduce(
      (acc, link) => {
        // Create more specific categories for retry failures
        let key;
        if (link.status) {
          key = `Status ${link.status}`;
        } else if (link.error?.includes("timeout") || link.error?.includes("AbortError")) {
          key = "Error: Request Timeout";
        } else {
          key = `Error: ${link.error}`;
        }
        if (!acc[key]) acc[key] = [];
        acc[key].push(link);
        return acc;
      },
      {} as Record<string, LinkCheckResult[]>
    );

    Object.entries(byStatus).forEach(([status, links]) => {
      report += `### ${status}\n\n`;

      links.forEach((link) => {
        const { url, pageFound, retries } = link;
        const retryInfo = retries ? ` (failed after ${retries} retries)` : "";
        report += `- ${url}${retryInfo}\n`;
        report += `  - Found on pages:\n`;
        pageFound.forEach((page) => {
          report += `    - ${page}\n`;
        });
        report += `\n`;
      });
    });
  } else {
    report += `## Broken Links\n\nNo broken links found. All links are working properly! 🎉\n\n`;
  }

  // Redirected links section
  if (redirectedLinks.length > 0) {
    report += `## Redirected Links\n\n`;
    report += `| Original URL | Redirects To | Found On |\n`;
    report += `|-------------|-------------|----------|\n`;

    redirectedLinks.forEach(({ url, redirectUrl, pageFound }) => {
      const pages =
        pageFound.length > 3
          ? pageFound.slice(0, 2).join(", ") + `, and ${pageFound.length - 2} more`
          : pageFound.join(", ");

      report += `| ${url} | ${redirectUrl} | ${pages} |\n`;
    });
    report += `\n`;
  } else {
    report += `## Redirected Links\n\nNo redirected links found.\n\n`;
  }

  // Next steps section
  report += `## Next Steps\n\n`;

  if (brokenLinks.length > 0) {
    report += `- Review and fix the broken links above\n`;
  }

  if (redirectedLinks.length > 0) {
    report += `- Consider updating redirected links to point directly to their destinations for better performance\n`;
  }

  report += `- Consider adding problematic domains to the allowlist if they're known to be valid but block requests\n`;
  report += `- Run the check again after fixing issues\n`;

  return report;
}

// When run directly
async function main() {
  const args = process.argv.slice(2);
  const verbose = args.includes("--verbose");
  const concurrentRequests = parseInt(
    args.find((arg) => arg.startsWith("--concurrency="))?.split("=")[1] || "5"
  );
  const distDir = path.join(process.cwd(), "dist");

  // Check if dist directory exists
  if (!fs.existsSync(distDir)) {
    coloredLog(`${icons.error} Dist directory not found! Run \`bun run build\` first.`, "red");
    process.exit(1);
  }

  try {
    const result = await validateExternalLinks(distDir, verbose, concurrentRequests);

    console.log(
      `\nExternal link check complete.\n` +
        `- Checked ${result.nLinksChecked} links\n` +
        `- Found ${result.brokenLinks.length} broken links\n` +
        `- Found ${result.redirectedLinks.length} redirected links`
    );

    // Set output for GitHub Actions
    if (process.env.GITHUB_OUTPUT) {
      fs.appendFileSync(
        process.env.GITHUB_OUTPUT,
        `has_broken_links=${result.brokenLinks.length > 0}\n`
      );
      fs.appendFileSync(
        process.env.GITHUB_OUTPUT,
        `broken_link_count=${result.brokenLinks.length}\n`
      );
      fs.appendFileSync(
        process.env.GITHUB_OUTPUT,
        `redirected_link_count=${result.redirectedLinks.length}\n`
      );
    }
  } catch (error) {
    coloredLog(`${icons.error} Error validating links:`, "red");
    console.error(error);
    process.exit(1);
  }
}

// Run the script if invoked directly
if (import.meta.path === Bun.main) {
  await main();
}

// Export for use in other scripts
export { validateExternalLinks };
